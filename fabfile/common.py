from fabric.api import *
from fabric.contrib import *


def installed(package):
    env.warn_only = True        # Just setting this incase we need it.
    return not 'is not installed' in run('rpm -q %s' % package)


def yum(*packages,action='install'):
    return run('yum -y %s %s' % (action, ' '.join(packages)))


def dl_template(template, location):
    raw_file_host = 'https://raw.githubusercontent.com'
    tmpl_base = '/BukGet/devfiles/master/templates'
    url = '%s%s/%s' % (raw_file_host, tmpl_base, template)
    run('curl -o %s %s' % (location, url))


def service(name, action, mech='service'):
    if mech == 'service':
        run('service %s %s' % (name, action))
    elif mech == 'initctl':
        run('initctl %s %s' % (action, name))

def upgrade_all_packages():
    return run('yum -y update && yum -y upgrade')