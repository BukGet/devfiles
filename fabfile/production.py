from fabric.api import *
from fabric.contrib import *

@task
def promote(server='api'):
    '''
    Promotes a server to production status.
    '''
    env.warn_only = True 
    # Step 1: Turn on any services that dev servers have disabled by default:
    run('chkconfig --levels 2345 iptables on')
    if 'Firewall is not running' in run('service iptables status'):
        run('service iptables start')


    run('iptables -F INPUT')
    run('iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT')
    run('iptables -A INPUT -p icmp -j ACCEPT')
    run('iptables -A INPUT -i lo -j ACCEPT')

    # Allows anything from Hamachi-space.  As this is our back-channel VPN, this
    # should always be the case.
    run('iptables -A INPUT --src 25.0.0.0/8 -j ACCEPT')

    # Also allow SSH from the bukget.org webhost.  This is a failsafe incase
    # Hamachi is down & we have issues with the API servers.
    if server == 'api':
        run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 --src 70.32.35.194 -j ACCEPT')
        run('iptables -A INPUT -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 53 -j ACCEPT')
        run('iptables -A INPUT -p udp -m state --state NEW,ESTABLISHED -m udp --dport 53 -j ACCEPT')

    if server == 'gen':
        run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT')

    # We also kinda need to enable port 80 for all the web traffic we expect ;)
    if server == 'api':
        run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT')
        run('iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT')

    # Lastly, lets finish this off and save the iptables config.
    run('iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited')
    run('iptables -A FORWARD -j REJECT --reject-with icmp-host-prohibited')
    run('service iptables save')
