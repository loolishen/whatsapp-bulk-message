#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Tenant, WhatsAppConnection, Customer

def setup_test_data():
    """Set up test data for WABOT testing"""
    print("🔧 Setting up test data for WABOT testing")
    print("=" * 50)
    
    # Create or get tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Tenant",
        defaults={
            'description': 'Test tenant for WABOT integration',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Created tenant: {tenant.name}")
    else:
        print(f"✅ Found existing tenant: {tenant.name}")
    
    # Create or get WhatsApp connection
    connection, created = WhatsAppConnection.objects.get_or_create(
        tenant=tenant,
        instance_id="68A0A11A89A8D",
        defaults={
            'access_token': '68a0a10422130',
            'phone_number': '+60123456789',
            'status': 'active'
        }
    )
    
    if created:
        print(f"✅ Created WhatsApp connection: {connection.instance_id}")
    else:
        print(f"✅ Found existing WhatsApp connection: {connection.instance_id}")
    
    # Check existing customers
    customers = Customer.objects.filter(tenant=tenant)
    print(f"📊 Existing customers: {customers.count()}")
    
    for customer in customers[:5]:  # Show first 5 customers
        print(f"   - {customer.name} ({customer.phone_number})")
    
    print(f"\n🎯 Ready for testing!")
    print(f"   - Tenant: {tenant.name}")
    print(f"   - WhatsApp Connection: {connection.instance_id}")
    print(f"   - Webhook URL: http://127.0.0.1:8000/webhook/whatsapp/")
    
    return tenant, connection

if __name__ == "__main__":
    setup_test_data()
