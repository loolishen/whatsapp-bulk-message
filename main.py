"""
Main entry point for App Engine Standard.
This is what App Engine auto-detection looks for.
"""
import os
import sys

# Ensure the current directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings to use our flattened production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application

# App Engine Standard looks for 'app' variable
app = get_wsgi_application()






