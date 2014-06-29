from fabric.api import *
from fabric.contrib import *

@task
def hamachi():
    '''Hamachi Installation and Configuration.'''
    env.warn_only = True        # Just setting this incase we need it.

    # The first step is to install Hamachi.  As Hamachi depends on having the
    # LSB packages installed, we will first install that before installing
    # the Hamachi package.
    run('yum -y install redhat-lsb')
    run('yum -y install http://pkgs.chigeek.com/logmein-hamachi-2.1.0.101-1.x86_64.rpm')
    run('service logmein-hamachi start')

    # We need to wait a couple of seconds after installing hamachi to make sure everything has
    # started up ok.
    time.sleep(5)

    # Now to go ahead and login to hamachi, attach to the LogMeIn account and to
    # the Hamachi Network that all of the BukGet servers are on.  This action
    # does require Steve to login to his hamachi account and manually add the
    # server to the network however.
    run('hamachi login')
    run('hamachi do-join 170-613-561 ""')