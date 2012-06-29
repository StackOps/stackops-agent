# Ref: http://jmoiron.net/blog/deploying-django-mod-wsgi-virtualenv/

import sys
import site
import os

#we are adding virtual enviornment path.
vepath = '/var/lib/horizon/openstack-dashboard/.dashboard-venv/lib/python2.6/site-packages'
os.environ['PYTHON_EGG_CACHE'] = '/var/lib/horizon/openstack-dashboard/.dashboard-venv/lib/python2.6/site-packages'

prev_sys_path = list(sys.path)

# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)

# reorder sys.path so new directories from the addsitedir show up first

new_sys_path = [p for p in sys.path if p not in prev_sys_path]

for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

# import from down here to pull in possible virtualenv django install

from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'dashboard.settings'
application = WSGIHandler()
