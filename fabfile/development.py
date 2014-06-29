from fabric.api import *
from fabric.contrib import *

@task
def promote():
    '''
    Sets the Machine up for development use.  These machines should never be 
    exposed directly to the internet, as this process (among other things)
    disables the host firewall for full access to the host.
    '''
    run('service iptables stop')
    run('service ip6tables stop')
    run('chkconfig iptables off')
    run('chkconfig ip6tables off')