from fabric.api import *
from fabric.contrib import *
#from settings import *
import datetime
import time

env.key_filename = '/opt/keys/id_rsa'

@task
def new_bukget():
    '''Preps a fresh CentOS 6 installation and installs the BukGet services.'''
    env.warn_only = True        # Just setting this incase we need it.

    send_sshkey()
    # First thing we need to do is update the system to current and install
    # the Development Tools package group as these will be used to build in
    # the python packages.
    run('yum -y update')
    run('yum -y groupinstall "Development Tools"')

    # For some reason, this package is installed by default, however all it
    # does in 99% of cases is span the system log, so lets pull it out.
    run('yum -y remove lldpad')

    # Next we will run the VMWare Tools installer.  If the box isn't a VMWare
    # VM, it will just skip through, so it doesnt hurt to run that here.
    install_vmware_tools()

    # Next up is installing Hamachi.  We have a process already for this in
    # place, so lets just call that.
    hamachi()

    # Next up, installing the EPEL & 10gen Repositories.
    run('yum -y install http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm')
    run('curl -o /etc/yum.repos.d/10gen.repo https://raw.github.com/BukGet/devfiles/master/templates/10gen.repo')

    # Next we will need to install the following packages:
    #  * python-devel               - Needed to byte-compile python libraries
    #  * libyaml & libyaml-devel    - Needed to byte-compile pyyaml
    #  * mongo-10gen                - MongoDB Tools
    #  * mongo-10gen-server         - The MongoDB Service itself
    #  * nginx                      - The front-end web server
    #  * anacron                    - A cron daemon
    run('yum -y install python-devel libyaml libyaml-devel mongo-10gen mongo-10gen-server nginx ntp anacron')

    # Lets make sure that time on this server does drift, so first fix the time
    # then enable the ntp service.
    run('ntpdate time.centos.org')
    run('chkconfig --levels 2345 ntpd on')
    run('service ntpd start')
    run('service crond start')

    # Lets go ahead and make sure that MongoDB and Nginx startup at boot.
    run('chkconfig --levels 2345 mongod on')
    run('chkconfig --levels 2345 nginx on')
    run('chkconfig --levels 2345 postfix on')
    run('chkconfig --levels 2345 crond on')

    # Make the Necessary pulls for logrotate and cront o function properly.
    run('curl -o /etc/logrotate.d/bukget https://raw.github.com/BukGet/devfiles/master/templates/logrotate.conf')
    run('curl -o /etc/cron.d/0hourly https://raw.github.com/BukGet/devfiles/master/templates/cronhourlyfix.conf')

    # A couple of things that we need to do for postfix, mainly update the
    # aliases to point root traffic to our group.
    files.append('/etc/aliases', 'root:     staff@bukget.org')
    run('newaliases')

    config_nginx()
    # As just about everything depends on this folder, lets go ahead and create
    # it ;)
    run('mkdir /var/log/bukget')

    # Now we should be able to start all of these services up :D
    run('service mongod start')
    run('service postfix start')

    # Now, we need to install pip.  We use pip to pull in the dependencies for
    # the BukGet packages.  Lets also clean up the tarball that the distribute
    # installation leaves behind.
    run('curl http://python-distribute.org/distribute_setup.py | python')
    run('curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python')
    run('rm -f distribute*.tar.gz')

    with cd('/opt'):
        run('git clone git://github.com/BukGet/bukget.git')

    # Now it's time to actually install the API code.  This is actually fairly
    # easy as all of the packages we need are in the python package index.  The
    # process we will be using is the same as upgrading the code, so we will
    # just call that function.
    upgrade_api()

    # Now, lets start the api up.
    run('initctl start bukget')
    print 'Install & Prep Complete!  Please run either make_prod or make_dev.'


@task
def make_prod():
    '''
    Makes the necessary configuration changes to turn a given host into a
    production API server.
    '''
    # Step 1: Turn on any services that dev servers have disabled by default:
    run('chkconfig --levels 2345 iptables on')
    if 'Firewall is not running' in run('service iptables status'):
        run('service iptables start')

    # We need to adjust the IPTables rules to block communication on
    # non-essential ports, restrict SSH communication from the outside world,
    # and generally just lock things down a touch.
    run('iptables -F INPUT')
    run('iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT')
    run('iptables -A INPUT -p icmp -j ACCEPT')
    run('iptables -A INPUT -i lo -j ACCEPT')

    # Allows anything from Hamachi-space.  As this is our back-channel VPN, this
    # should always be the case.
    run('iptables -A INPUT --src 25.0.0.0/8 -j ACCEPT')

    # Also allow SSH from the bukget.org webhost.  This is a failsafe incase
    # Hamachi is down & we have issues with the API servers.
    run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 --src 70.32.35.194 -j ACCEPT')

    # We also kinda need to enable port 80 for all the web traffic we expect ;)
    run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT')

    # Lastly, lets finish this off and save the iptables config.
    run('iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited')
    run('iptables -A FORWARD -j REJECT --reject-with icmp-host-prohibited')
    run('service iptables save')


@task
def make_dev():
    '''
    Sets the Machine up for development use.  These machines should never be 
    exposed directly to the internet, as this process (among other things)
    disables the host firewall for full access to the host.
    '''
    run('service iptables stop')
    run('service ip6tables stop')
    run('chkconfig iptables off')
    run('chkconfig ip6tables off')


@task
def upgrade_api():
    '''Installs and Upgrades the BukGet API'''
    with cd('/opt/bukget/api'):
        run('pip install --upgrade ./')
    if not files.exists('/etc/init/bukget.conf'):
        run('curl -o /etc/init/bukget.conf https://raw.github.com/BukGet/devfiles/master/templates/upstart.conf')
        run('initctl reload-configuration')
    if not files.exists('/etc/init/nodeapi.conf'):
        run('curl -o /etc/init/nodeapi.conf https://raw.github.com/BukGet/devfiles/master/templates/upstart_nodeapi.conf')
        run('initctl reload-configuration')



@task
def upgrade_generator():
    '''Installs and Upgrades the BukGen generation scripts.'''
    with cd('/opt/bukget/bukgen'):
        run('pip install --upgrade ./')
    cronjob = '0 */6 *  *  * root /usr/bin/bukgen_bukkit speedy'
    logreader = '50 0  *  *  * root python /opt/bukget/scripts/logreader.py'
    if not files.contains('/etc/crontab', cronjob):
        files.append('/etc/crontab', cronjob)
    if not files.contains('/etc/crontab', logreader):
        files.append('/etc/crontab', logreader)


@task
def config_nginx():
    '''Nginx Configuration'''
    env.warn_only = True        # Just setting this incase we need it.

    # We will need to download the Nginx template config.  This config
    # file is a pre-configured vhost for the bukget API.  We will need to
    # replace the hostname placeholder with the actual hostname.
    hostname = run('hostname')
    run('curl -o /etc/nginx/conf.d/api.bukget.org.conf https://raw.github.com/BukGet/devfiles/master/templates/nginx_vhost.conf')
    files.sed('/etc/nginx/conf.d/api.bukget.org.conf', '@HOSTNAME@', hostname)
    run('service nginx restart')


@task
def hamachi():
    '''Hamachi Installation and Configuration.'''
    env.warn_only = True        # Just setting this incase we need it.

    # The first step is to install Hamachi.  As Hamachi depends on having the
    # LSB packages installed, we will first install that before installing
    # the Hamachi package.
    run('yum -y install redhat-lsb')
    run('yum -y install http://pkgs.chigeek.com/logmein-hamachi-2.1.0.101-1.x86_64.rpm')
    run('service logmein-hamachi start')

    # We need to wait a couple of seconds after installing hamachi to make sure everything has
    # started up ok.
    time.sleep(5)

    # Now to go ahead and login to hamachi, attach to the LogMeIn account and to
    # the Hamachi Network that all of the BukGet servers are on.  This action
    # does require Steve to login to his hamachi account and manually add the
    # server to the network however.
    run('hamachi login')
    run('hamachi do-join 170-613-561 ""')


@task
def backup_db():
    '''BukGet Database Backup'''
    # Get todays date and then generate the name of the backup file.
    date = datetime.date.today()
    name = 'bukget-db.%s.%s.%s.tar.gz' % (date.year, date.month, date.day)

    # Generate the dump, then 
    with cd('/tmp'):
        run('mongodump -d bukget')
        run('tar czf /tmp/%s dump' % name)
        run('rm -rf /tmp/dump')

    # Pull the backup into the backups folder then remove the remote copy as its
    # no longer needed.
    get('/tmp/%s' % name, '/backups/db/')
    run('rm -f /tmp/%s' % name)


@task
def dev_import_backup():
    '''Restore Archived Backup Database into Dev Environment'''
    # Firgure out what yesterdays database archive was named...
    date = datetime.date.today() - datetime.datedelta(days=-1)
    name = 'bukget-db.%s.%s.%s.tar.gz dump' % (date.year, date.month, date.day)

    # Now to perform the restore.
    put('/backups/db/%s' % name, '/tmp/backup.tar.gz')
    with cd('/tmp'):
        if files.exists('/tmp/dump'):
            run('rm -rf /tmp/dump')
        run('tar xzf backup.tar.gz')
        run('mongorestore -d bukget --drop')


@task(alias='sshkey')
def send_sshkey(keyfile='/opt/keys/id_rsa.pub'):
    env.warn_only = True        # We need this flag set for restorecon.  It only
                                # exists for redhat hosts so it may not fire on
                                # everything.
    pubkey = open(keyfile).read()
    if not files.exists('/root/.ssh'):
        run('mkdir /root/.ssh')
    if files.exists('/root/.ssh/authorized_keys') and files.contains('/root/.ssh/authorized_keys', pubkey):
        pass
    else:
        if not files.exists('/root/.ssh/authorized_keys'):
            run('touch /root/.ssh/authorized_keys')
        files.append('/root/.ssh/authorized_keys', pubkey)
    run('chmod 0700 /root/.ssh')
    run('chmod 0600 /root/.ssh/authorized_keys')
    run('restorecon -R -v /root/.ssh')


@task
def install_vmware_tools():
    '''VMWare Tools Installation.'''
    if 'VMware' in run('cat /proc/scsi/scsi'):
        # This is specific to ESXi 5.1.  I havent tested on earlier versions
        # of ESXi as well, so I don't know if these packages are locked into
        # only the most recent version or not, however this should install
        # the packages needed for VMWare if the box is infact a vmware guest.
        run('rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub')
        run('rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub')
        run('curl -o /etc/yum.repos.d/vmware-tools.repo https://raw.github.com/BukGet/devfiles/master/templates/vmware-tools.repo')
        run('yum -y install vmware-tools-esx-kmods vmware-open-vm-tools-nox')

@task
def install_nodeapi():
    '''NodeAPI Installation.'''
    run('yum install npm')
    run('npm install -g forever')
    with cd('/opt'):
        run('git clone git://github.com/BukGet/api.git')
    with cd('/opt/nodeapi'):
        run('npm install')    