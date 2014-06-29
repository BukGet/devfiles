from fabric.api import *
from fabric.contrib import *
from fabfile.common import *

@task
def prep():
    env.warn_only = True

    # First we need to update the system, install the development tools, and
    # remove lldpad and httpd if they are installed.  From there we will install
    # the EPEL repository as well as some basic services that every box will
    # need, such as ntp, anacron, and postfix.
    yum(action='update')
    yum('"Development Tools"', action='groupinstall')
    yum('lldpad', 'httpd', action='remove')
    yum('http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm')
    yum('ntp', 'anacron', 'htop', 'postfix')

    # Next we will change the localtime to UTC then force the machine to
    # update it's time.
    if not files.exists('/etc/sysconfig/clock'):
        run('touch /etc/sysconfig/clock')
    files.append('/etc/sysconfig/clock','\n'.join(['ZONE=\"UTC\"', 'UTC=True']))
    run('ls -sf /usr/share/zoneinfo/UTC /etc/localtime')
    run('hwclock --systohc')
    update_time()

    # Then we will make sure that the base services will start at boot.
    run('chkconfig --levels 2345 postfix on')
    run('chkconfig --levels 2345 crond on')

    # Next up to apply the logrotate config and the "fix" that we sometimes
    # need for anacron to play nice.
    dl_template('logrotate.conf', '/etc/logrotate.d/bukget')
    dl_template('cronhourlyfix.conf', '/etc/cron.d/0hourly')

    # Now we need to add in the rules to send all root emails to the Staff
    # email account: staff@bukget.org
    files.append('/etc/aliases', 'root:     staff@bukget.org')
    run('newaliases')

    # a lot of our services write their log data into /var/log/bukget, so we
    # might as well create it here.
    run('mkdir /var/log/bukget')

    # Now to start up any services that handn't started.
    run('service crond start')
    run('service postfix start')

    # Lastly, lets go ahead and clone in the ops scripts repository...
    with cd('/opt'):
        run('git clone git://github.com/BukGet/devfiles.git devfiles')


@task
def update_time():
    '''
    Forces a NTP sync and restarts the NTP daemon.
    '''
    if 'running' in run('service ntpd status'):
        service('ntpd', 'stop')
    run('ntpdate time.centos.org')
    service('ntpd', 'start')


@task
def push_ssh_keys():
    '''
    Will pull the authorized_keys file from the operations repository and
    drop it in place for the root user.
    '''
    if not files.exists('/root/.ssh'):
        run('mkdir /root/.ssh')
    dl_template('authorized_keys', '/root/.ssh/authorized_keys')
    run('chmod 0700 /root/.ssh')
    run('chmod 0600 /root/.ssh/authorized_keys')
    run('chmod 0600 /root/.ssh/id_rsa')
    run('restorecon -R -v /root/.ssh')


@task
def update_ops():
    '''
    Updates the ops (devfiles) repository.
    '''
    with cd('/opt/devfiles'):
        run('git pull')
