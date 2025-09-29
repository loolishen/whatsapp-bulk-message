import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project directory to the Python path
sys.path.insert(0, '/home/yourusername/public_html/whatsapp-bulk-message')
sys.path.insert(0, '/home/yourusername/public_html/whatsapp-bulk-message/whatsapp_bulk')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

application = get_wsgi_application()
