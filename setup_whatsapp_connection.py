#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_local')
django.setup()

from messaging.models import WhatsAppConnection, Tenant, TenantUser
from django.contrib.auth.models import User

print("=== SETTING UP WHATSAPP CONNECTION ===")

# Get the admin user and their tenant
user = User.objects.get(username='admin')
tenant_user = TenantUser.objects.get(user=user)
tenant = tenant_user.tenant

print(f"Setting up WhatsApp connection for tenant: {tenant.name}")

# Create WhatsApp connection
whatsapp_conn, created = WhatsAppConnection.objects.get_or_create(
    tenant=tenant,
    phone_number='60162107682',
    defaults={
        'access_token_ref': '68a0a10422130',
        'instance_id': '68A0A11A89A8D',
        'provider': 'wabot'
    }
)

if created:
    print(f"✅ WhatsApp connection created successfully!")
    print(f"   Phone: {whatsapp_conn.phone_number}")
    print(f"   Instance ID: {whatsapp_conn.instance_id}")
    print(f"   Provider: {whatsapp_conn.provider}")
else:
    print(f"✅ WhatsApp connection already exists!")
    print(f"   Phone: {whatsapp_conn.phone_number}")
    print(f"   Instance ID: {whatsapp_conn.instance_id}")
    print(f"   Provider: {whatsapp_conn.provider}")

print("\n=== VERIFICATION ===")
connections = WhatsAppConnection.objects.filter(tenant=tenant)
print(f"Total connections for this tenant: {connections.count()}")
for conn in connections:
    print(f"- Phone: {conn.phone_number} | Instance: {conn.instance_id} | Provider: {conn.provider}")
