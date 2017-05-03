"""
WSGI config for HouseParty project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
# import uwsgi
#
# from core.service import check_online
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HouseParty.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# uwsgi.register_signal(82, "worker", check_online)
# uwsgi.add_timer(82, 10)
