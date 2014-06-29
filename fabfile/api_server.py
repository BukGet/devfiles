from fabric.api import *
from fabric.contrib import *
from fabfile.common import *


@task
def build():
    run('yum -y install npm')
    run('npm install -g forever')
    run('chkconfig --levels 2345 nginx on')
    config_nginx()

    install_dnsupdater()
    install_nodeapi()
    install_geodns()

    files.append('/etc/mongod.conf', 'slave = true')
    files.append('/etc/mongod.conf', 'source = nj.vpn.bukget.org')

    run('service mongod start')

    # Now, lets start the api up.
    run('initctl reload-configuration')
    run('initctl start nodeapi')
    run('initctl start geodns')

    print 'Don\'t forget to fix config.js for dnsupdater'


@task
def nginx():
    '''Nginx Configuration'''
    env.warn_only = True        # Just setting this incase we need it.
    if not installed('nginx'):
        run()

    # We will need to download the Nginx template config.  This config
    # file is a pre-configured vhost for the bukget API.  We will need to
    # replace the hostname placeholder with the actual hostname.
    hostname = run('hostname')
    run('rm -rf /etc/nginx/conf.d/default.conf')
    run('curl -o /etc/nginx/conf.d/api.bukget.org.conf https://raw.githubusercontent.com/BukGet/devfiles/master/templates/nginx_vhost.conf')
    files.sed('/etc/nginx/conf.d/api.bukget.org.conf', '@HOSTNAME@', hostname)
    run('service nginx restart')
