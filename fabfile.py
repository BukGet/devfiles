from fabric.api import *
from fabric.contrib import *
from settings import *
import time


@task
def new_bukget():
    '''Preps a fresh CentOS 6 installation and installs he BukGet services.'''
    env.warn_only = True        # Just setting this incase we need it.

    # First thing we need to do is update the system to current and install
    # the Development Tools package group as these will be used to build in
    # the python packages.
    run('yum -y update')
    run('yum -y groupinstall "Development Tools"')

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
    #  * python-devel               - Needed to byte-compile somee python packages
    #  * libyaml & libyaml-devel    - Needed to byte-compile pyyaml
    #  * mongo-10gen                - MongoDB Tools
    #  * mongo-10gen-server         - The MongoDB Service itself
    #  * nginx                      - The front-end web server
    #  * anacron                    - A cron daemon
    run('yum -y install python-devel libyaml libyaml-devel mongo-10gen mongo-10gen-server nginx')

    # Lets go ahead and make sure that MongoDB and Nginx startup at boot.
    run('chkconfig --levels 2345 mongod on')
    run('chkconfig --levels 2345 nginx on')

    # Also, we will need to download the Nginx Ttemplate config.  This config
    # file is a pre-configured vhost for the bukget API.  We will need to
    # replace the hostname placeholder with the actual hostname.
    hostname = run('hostname')
    run('curl -o /etc/nginx/conf.d/api.bukget.org.conf https://raw.github.com/BukGet/devfiles/master/templates/nginx_vhost.conf')
    files.sed('/etc/nginx/conf.d/api.bukget.org.conf', '@HOSTNAME@', hostname)

    # As just about everything depends on this folder, lets go ahead and create
    # it ;)
    run('mkdir /var/log/bukget')

    # New we should be able to start all of these services up :D
    run('service nginx start')
    run('service mongod start')

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

    # Lastly, we can start the api up.
    run('initctl start bukget')


@task
def upgrade_api():
    '''Installs and Upgrades the BukGet API'''
    with cd('/opt/bukget/api'):
        run('pip install --upgrade ./')
    if not files.exists('/etc/init/bukget.conf'):
        run('curl -o /etc/init/bukget.conf https://raw.github.com/BukGet/devfiles/master/templates/upstart.conf')
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
def hamachi():
    '''Hamachi Installation and Configuration.'''
    env.warn_only = True        # Just setting this incase we need it.

    # The first step is to install Hamachi.  As Hamachi depends on having the
    # LSB packages installed, we will first install that before installing
    # the Hamachi package.
    run('yum -y install redhat-lsb')
    run('yum -y install https://secure.logmein.com/labs/logmein-hamachi-2.1.0.86-1.x86_64.rpm')
    run('service logmein-hamachi start')

    # We need to wait a couple of seconds after installing hamachi to make sure everything has
    # started up ok.
    time.sleep(5)

    # Now to go ahead and login to hamachi, attach to the LogMeIn account and to
    # the Hamachi Network that all of the BukGet servers are on.  This action
    # does require Steve to login to his hamachi account and manually add the
    # server to the network however.
    run('hamachi login')
    run('hamachi attach %s' % hamachi_login)
    run('hamachi join 170-613-561')


@task
def install_vmware_tools():
    '''VMWare Tools Installation.'''
    if 'VMware' in run('cat /proc/scsi/scsi'):
        run('rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-DSA-KEY.pub')
        run('rpm --import http://packages.vmware.com/tools/keys/VMWARE-PACKAGING-GPG-RSA-KEY.pub')
        put('%s/vmware-tools.repo' % pkg_dir, '/etc/yum.repos.d/vmware-tools.repo')
        run('yum -y install vmware-tools-esx-kmods vmware-open-vm-tools-nox')