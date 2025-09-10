#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsappbulkmessage.settings')
django.setup()

from messaging.models import Contact

# Add test contact
test_contact, created = Contact.objects.get_or_create(
    phone_number='+60162107682',
    defaults={'name': 'Test Contact'}
)

if created:
    print(f"Created test contact: {test_contact.name} - {test_contact.phone_number}")
else:
    print(f"Test contact already exists: {test_contact.name} - {test_contact.phone_number}")
