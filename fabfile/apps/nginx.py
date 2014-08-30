from fabric.api import *
from fabric.contrib import *
from fabfile.common import *


@task
def install():
    '''Nginx Configuration'''
    env.warn_only = True        # Just setting this incase we need it.

    # Lets check to see if Nginx is installed.  If it isnt, then lets go ahead
    # and install the package.
    if not installed('nginx'):
        yum('nginx')
        run('chkconfig --levels 2345 on')

    # We will need to download the Nginx template config.  This config
    # file is a pre-configured vhost for the bukget API.  We will need to
    # replace the hostname placeholder with the actual hostname.
    hostname = run('hostname')
    run('rm -rf /etc/nginx/conf.d/default.conf')
    run('openssl ciphers -V "EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA256 EECDH+aRSA+SHA256 EECDH+aRSA+RC4 EDH+aRSA EECDH RC4 !aNULL !eNULL !LOW !3DES !MD5 !EXP !PSK !SRP !DSS"')
    with cd('/etc/nginx'):
        run('openssl dhparam -out dh2048.pem 2048')
    dl_template('nginx_vhost.conf', '/etc/nginx/conf.d/api.bukget.org.conf')
    files.sed('/etc/nginx/conf.d/api.bukget.org.conf', '@HOSTNAME@', hostname)

@task
def start():
    run('service nginx start')


@task
def stop():
    run('service nginx stop')


@task
def restart():
    run('service nginx restart')