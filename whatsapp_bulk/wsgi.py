"""
WSGI config for whatsapp_bulk project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

application = get_wsgi_application()
