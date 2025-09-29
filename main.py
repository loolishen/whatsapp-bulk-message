import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')

# Get the Django WSGI application
app = get_wsgi_application()
