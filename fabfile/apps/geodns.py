from fabric.api import *
from fabric.contrib import *
from fabfile.common import *


@task
def install():
    '''
    GeoDNS Installation
    '''

    # If the directories don't exist, let go ahead and create them.
    if not files.exists('/opt/geodns'):
        run('mkdir /opt/geodns')
        run('mkdir /opt/geodns/dns')

    # Next we will download the appropriate files, mainly the upstart config,
    # the geodns config, and the geodns binary itself.  Once we have these all
    # downloaded we will need to set the appropriate permissions on the geodns
    # binary.
    dl_template('upstart_geodns.conf', '/etc/init/geodns.conf')
    dl_template('geodns.conf', '/opt/geodns/dns/geodns.conf')
    dl_template('geodns.bin', '/opt/geodns/geodns')
    run('chmod 755 /opt/geodns/geodns')
    geoip_update()
    start()


@task
def upgrade():
    '''
    Upgrades the GeoDNS binary..
    '''
    dl_template('geodns.bin', '/opt/geodns/geodns')
    restart()


@task
def geoip_update():
    '''
    Updates the GeoIP database
    '''
    database = 'GeoLiteCountry'
    package = 'GeoIP.dat.gz'
    base = 'http://geolite.maxmind.com/download/geoip/database'
    url = '%s/%s/%s' % (base, database, package)
    with cd('/usr/share/GeoIP'):
        run('wget -N %s' % url)
        run('rm -rf GeoIP.dat')
        run('gunzip GeoIP.dat.gz')
    restart()


@task
def start():
    run('initctl start geodns')


@task
def stop():
    run('initctl stop geodns')


@task
def restart():
    run('initctl restart geodns')