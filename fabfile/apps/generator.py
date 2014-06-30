from fabric.api import *
from fabric.contrib import *
from fabfile.common import *
import mongo

@task
def install():
    '''
    Installs the BukGet generator system.
    '''
    
    # First step is to install mongodb (if not already installed) and then make
    # the mongodb environment a master.
    mongo.install()
    mongo.master()

    # Next we need to install the needed dependencies in order to actually use
    # this entertaining bit of python code.  This means installing the python
    # development headers, libyaml, and pip.
    yum('python-devel', 'libyaml', 'libyaml-devel')
    run('curl https://bootstrap.pypa.io/get-pip.py | python')
    run('pip install fabric')

    # Next we will go ahead and clone the generator repository.
    with cd('/opt'):
        run('git clone git://github.com/BukGet/generator.git')

    # Now to actually install the generator
    with cd('/opt/generator'):
        run('pip install --upgrade ./')

    # next we need to set some cronjobs, as these are setting the pace for when
    # generation is occuring.
    cronjobs = [
        '0 */6 * * * root /usr/bin/bukgen_bukkit speedy',
        '0 1   * * 5 root /usr/bin/bukgen_bukkit speedy_full',
        '30 5  * * * root python /opt/devfiles/logreader.py',
    ]
    for job in cronjobs:
        if not files.contains('/etc/crontab', job):
            files.append('/etc/crontab', job)
    run('ssh-keygen -t rsa -N ""')
    key = run('cat /root/.ssh/id_rsa.pub')
    print '\n'.join([
        '\n[!] System Built.  Please update the authorized_keys template with',
        '    the key below this message.  This key needs to be pushed out to',
        '    the rest of the environment in order for things like logrotate',
        '    to work.',
    ])
    print key

@task
def upgrade():
    '''
    Upgrades the BukGet generator to the current version in git.
    '''
    with cd('/opt/generator'):
        run('pip install --upgrade ./')

