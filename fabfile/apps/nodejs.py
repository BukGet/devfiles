from fabric.api import *
from fabric.contrib import *
from fabfile.common import *

@task
def install():
	yum('npm')
	run('npm install -g forever')