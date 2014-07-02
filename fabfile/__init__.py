from fabfile import common
from fabfile import apps
from fabfile import base
from fabfile import production
from fabfile import development
from fabfile import networking
from fabfile import adhoc

from fabric.api import env

env.user = 'root'
env.disable_known_hosts = True
env.warn_only = True

env.roledefs['api_us'] = ['ca.vpn.bukget.org', 'ny.vpn.bukget.org']
env.roledefs['api_eu'] = ['fr.vpn.bukget.org', 'de.vpn.bukget.org']
env.roledefs['generators'] = ['tx.vpn.bukget.org', 'nj.gen.bukget.org']
env.roledefs['dev'] = ['dev.vpn.bukget.org']
env.roledefs['api_all'] = env.roledefs['api_us'] + env.roledefs['api_eu']