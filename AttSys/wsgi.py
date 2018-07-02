SETTINGS_MODULE = "AttSys.settings"

import os, sys, site

#configuration for server
# if SETTINGS_MODULE == "AttSys.settings":
#     site.addsitedir('/home/teenoh/.virtualenvs/achime/lib/python3.5/site-packages')
#     activate_this = os.path.expanduser("~/.virtualenvs/attSys/bin/activate_this.py")
#     exec(open(activate_this).read())
#     project = '/home/teenoh/webapps/attsys/attsys/AttSys/'
#     workspace = os.path.dirname(project)
#     sys.path.append(workspace)



from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)

application = get_wsgi_application()