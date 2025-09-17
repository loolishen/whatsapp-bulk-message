#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Customer, Tenant
from django.contrib.auth.models import User

# Create test data
print("Creating test data...")

# Create tenant
tenant, created = Tenant.objects.get_or_create(
    name="Test Tenant",
    defaults={'description': 'Test tenant for development'}
)
print(f"Tenant: {'created' if created else 'found'} - {tenant.name}")

# Create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)
print(f"User: {'created' if created else 'found'} - {user.username}")

# Create test customers
test_customers = [
    {'name': 'Test Customer 1', 'phone_number': '60123456789'},
    {'name': 'Test Customer 2', 'phone_number': '60123456790'},
    {'name': 'Test Customer 3', 'phone_number': '60123456791'},
]

for customer_data in test_customers:
    customer, created = Customer.objects.get_or_create(
        phone_number=customer_data['phone_number'],
        defaults={
            'name': customer_data['name'],
            'tenant': tenant,
            'gender': 'N/A',
            'marital_status': 'N/A'
        }
    )
    print(f"Customer: {'created' if created else 'found'} - {customer.name} ({customer.customer_id})")

print(f"\nTotal customers: {Customer.objects.count()}")
print(f"Total tenants: {Tenant.objects.count()}")
print("Test data creation completed!")
