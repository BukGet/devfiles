from fabric.api import *
from fabric.contrib import *
from fabfile.common import *


@task
def install():
    if not installed('npm'):
       yum('npm')
       run('npm install -g forever')