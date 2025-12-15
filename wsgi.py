"""
WSGI application entry point for App Engine Standard.
FLATTENED STRUCTURE - settings are now in root.
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module - NOW IN ROOT
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Import and expose Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

