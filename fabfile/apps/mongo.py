from fabric.api import *
from fabric.contrib import *
from fabfile.common import *
import datetime


@task
def install():
    '''
    Installs the MogoDB database.
    '''
    if not installed('mongo-10gen-server'):
        dl_template('10gen.repo', '/etc/yum.repos.d/10gen.repo')
        yum('mongo-10gen', 'mongo-10gen-server')
        run('chkconfig --levels 2345 mongod on')
        start()


@task
def backup(database):
    '''
    Generate a backup of the database specified.
    '''
    # Get todays date and then generate the name of the backup file.
    date = datetime.date.today()
    name = 'bukget-db.%s.%s.%s.dump.tar.gz' % (date.year, date.month, date.day)

    # Generate the dump, then tar everything up into a nice, neat package.
    with cd('/tmp'):
        run('mongodump -d bukget')
        run('tar czf /tmp/%s dump' % name)

    # Pull the backup into the backups folder then remove the remote copy as its
    # no longer needed.
    get('/tmp/%s' % name, '/backups/db/')
    run('rm -f /tmp/%s' % name)
    run('rm -rf /tmp/dump')


@task
def restore(backup, database):
    '''
    Restores the backup file into the Mongo database specified.
    '''
    put(backup, '/tmp/backup.tar.gz')
    with cd('/tmp'):
        if files.exists('/tmp/dump'):
            run('rm -rf /tmp/dump')
        run('tar xzf backup.tar.gz')
        run('mongorestore -d %s --drop' % database)


@task
def master():
    '''
    Converts a MongoDB instance to master.
    '''
    if files.exists('/var/lib/mongo/local.0'):
        run('rm -f /var/lib/mongo.local.*')
        files.sed('/etc/mongod.conf', r'^slave = true$', '')
        files.sed('/etc/mongod.conf', r'^source = [a-z0-9]{2,3}.vpn.bukget.org$', '')
    files.append('/etc/mongod.conf', 'master = true')
    restart()


@task
def slave(master='nj.vpn.bukget.org'):
    '''
    Comverts a MongoDB instance to slave.
    '''
    files.sed('/etc/mongod.conf', r'^master = true\n$', '')
    files.append('/etc/mongod.conf', '\n'.join([
        'slave = true',
        'source = %s' % master
    ])
    restart()


@task
def promote(master):
    '''
    Promotes a new master into the cluster.
    '''
    files.sed('/etc/mongod.conf', r'[a-z0-9]{2,3}.vpn.bukget.org', master)
    restart()


@task
def start():
    run('service mongod start')


@task
def stop():
    run('service mongod stop')


@task
def restart():
    run('service mongod restart')