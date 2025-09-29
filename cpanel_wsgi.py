"""
WSGI configuration for cPanel deployment
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project directory to the Python path
# Update these paths to match your cPanel setup
project_path = '/home/yourusername/public_html/whatsapp-bulk-message'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Add the project's parent directory to the path
parent_path = os.path.dirname(project_path)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

# Create the WSGI application
application = get_wsgi_application()
