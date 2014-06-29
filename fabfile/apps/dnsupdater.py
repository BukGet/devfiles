from fabric.api import *
from fabric.contrib import *
from fabfile.common import *
import nodejs

@task
def install():
    '''
    DNS Updater Installation.
    '''
    nodejs.install()
    dl_template('upstart_dnsupdater.conf', '/etc/init/dnsupdater.conf')
    with cd('/opt'):
        run('git clone git://github.com/BukGet/dnsupdater.git dnsupdater')
    with cd('/opt/dnsupdater'):
        run('npm install')
    start()

@task
def upgrade():
    with cd('/opt/dnsupdater'):
        run('git pull')
    restart()


@task
def start():
    run('initctl start dnsupdater')


@task
def stop():
    run('initctl stop dnsupdater')


@task
def restart():
    run('initctl restart dnsupdater')