#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Customer, Tenant
from messaging.views import bulk_delete_customers
from django.test import RequestFactory
from django.contrib.auth.models import User

# Test bulk delete functionality
print("Testing bulk delete functionality...")

# Get tenant and customers
tenant = Tenant.objects.first()
if not tenant:
    print("No tenant found")
    sys.exit(1)

customers = Customer.objects.filter(tenant=tenant)[:2]
if not customers:
    print("No customers found")
    sys.exit(1)

print(f"Found {customers.count()} customers to test with")

# Create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)

# Create a mock request
factory = RequestFactory()
request = factory.post('/bulk-delete-customers/', {
    'customer_ids[]': [str(customer.customer_id) for customer in customers],
    'csrfmiddlewaretoken': 'test_token'
})

# Set user and tenant
request.user = user

# Mock the _get_tenant function
def mock_get_tenant(req):
    return tenant

# Replace the function temporarily
import messaging.views
original_get_tenant = messaging.views._get_tenant
messaging.views._get_tenant = mock_get_tenant

try:
    # Test the view
    response = bulk_delete_customers(request)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore original function
    messaging.views._get_tenant = original_get_tenant

print("Test completed!")
