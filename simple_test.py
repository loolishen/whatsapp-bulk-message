#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Customer, Tenant
from messaging.pdpa_service import PDPAConsentService

# Test basic functionality
print("Testing PDPA Service...")

# Get tenant
tenant = Tenant.objects.first()
if not tenant:
    print("No tenant found")
    sys.exit(1)

print(f"Tenant: {tenant.name}")

# Get or create customer
customer, created = Customer.objects.get_or_create(
    phone_number="60162107682",
    defaults={
        'name': 'Test Customer 7682',
        'tenant': tenant,
        'gender': 'N/A',
        'marital_status': 'N/A'
    }
)

print(f"Customer: {customer.name} ({'created' if created else 'found'})")

# Test PDPA service
pdpa_service = PDPAConsentService()
consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
print(f"Consent status: {consent_status}")

# Test message handling
result = pdpa_service.handle_incoming_message(customer, "hello", tenant)
print(f"Message handling result: {result}")

print("Test completed!")
