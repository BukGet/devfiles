from fabric.api import *
from fabric.contrib import *

@task
def installed(package):
    return not 'is not installed' in run('rpm -q %s' % package)


@task
def yum(*packages):
    return run('yum -y install %s' % ' '.join(packages))


@task
def chkconfig(service, onoff, levels=None):
    levels = 


@task
def dl_template(template, location):
    raw_file_host = 'https://raw.githubusercontent.com'
    tmpl_base = '/BukGet/devfiles/master/templates'
    url = '%s%s/%s' % (raw_file_host, tmpl_base, template)
    run('curl -o %s %s' % (location, url))