#!/usr/bin/env python
from zipfile import ZipFile
from cStringIO import StringIO
import yaml
import sys

def find_plugin_yaml(dataobj):
        '''
        '''
        yml = False
        try:
            # The first thing we are going to try to do is create a ZipFile
            # object with the StringIO data that we have.
            zfile = ZipFile(dataobj)
        except:
            print '[DEBUG] ZipFile Library Failed to Parse DataObject'
        else:
            # Before we start recursively jumping through hoops, lets first
            # check to see if the plugin.yml exists at this level.  If so, then
            # just set the yaml variable.  Otherwise we are gonna look for more
            # zip and jar files and dig into them.
            if 'plugin.yml' in zfile.namelist():
                try:
                    yml = yaml.load(zfile.read('plugin.yml'))
                except:
                    return False
            else:
                for filename in zfile.namelist():
                    if not yml and filename[-3:].lower() in ['zip', 'jar']:
                        print '[DEBUG] Found Zip/Jar file ' + filename
                        data = StringIO()
                        data.write(zfile.read(filename))
                        yml = find_plugin_yaml(data)
                        data.close()
                zfile.close()
        return yml


if __name__ == '__main__':
	print yaml.dump(find_plugin_yaml(open(sys.argv[1], 'r')))