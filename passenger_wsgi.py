import os, sys

sys.path.insert(0, '/home/xx5dnkq5vjmm/whatsapp-crm')
sys.path.insert(0, '/home/xx5dnkq5vjmm/whatsapp-crm/whatsapp_bulk')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
