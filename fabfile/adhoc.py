from fabric.api import *
from fabric.contrib import *
from fabfile.common import *

@task
def remove_private_keys():
    '''
    Dave copied over the private key as well as the public keys to all of the
    hosts.  Our goal here is to simply remove the id_rsa keys from the api
    servers, as there is no reason for them to be there.
    '''
    run('rm -f /root/.ssh/id_rsa')
    run('restorecon -R -v /root/.ssh')


@task
def test():
    '''
    A simple test for checking to see if everything is setup correctly for
    fabric.
    '''
    run('hostname')

@task
def logrotate():
		'''
		Manually run logrotate.
		'''
		run('logrotate -v /etc/logrotate.conf')