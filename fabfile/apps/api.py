from fabric.api import *
from fabric.contrib import *
from fabfile.common import *
import nodejs, mongo

@task
def install():
    '''
    Node.js BukGet API Implimentation installer
    '''
    nodejs.install()
    mongo.install()
    dl_template('upstart_nodeapi.conf', '/etc/init/nodeapi.conf')
    with cd('/opt'):
        run('git clone git://github.com/BukGet/api.git nodeapi')
    with cd('/opt/nodeapi'):
        run('npm install --production')
    run('initctl reload-configuration')
    start()


@task
def upgrade():
    with cd('/opt/nodeapi'):
        run('git pull')
        run('npm install --production')
    restart()


@task
def start():
    run('initctl start nodeapi')


@task
def stop():
    run('initctl stop nodeapi')


@task
def restart():
    stop()
    start()