"""
WSGI config for whatsapp_bulk project.
This is the entry point for App Engine.
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings by default (can be overridden by environment variable)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')

application = get_wsgi_application()
