#!/usr/bin/env python
"""
Verify tenant account and WhatsApp connection configuration
Run this in Cloud Shell to check everything is set up correctly
"""
import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser, WhatsAppConnection

print("=" * 70)
print("TENANT & WHATSAPP CONNECTION VERIFICATION")
print("=" * 70)

User = get_user_model()

# Check for tenant account
print("\n1️⃣  CHECKING TENANT ACCOUNT:")
print("-" * 70)

try:
    user = User.objects.get(username='tenant')
    print(f"✅ User found: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Is Staff: {user.is_staff}")
    print(f"   Is Superuser: {user.is_superuser}")
    
    # Verify password works
    if user.check_password('Tenant123!'):
        print(f"✅ Password verified: Tenant123!")
    else:
        print(f"⚠️  Password verification failed - might need to reset")
    
except User.DoesNotExist:
    print(f"❌ User 'tenant' not found!")
    print(f"   Run migrate_db.py to create the user")
    sys.exit(1)

# Check for tenant
print("\n2️⃣  CHECKING TENANT:")
print("-" * 70)

try:
    tenant_user = TenantUser.objects.get(user=user)
    tenant = tenant_user.tenant
    print(f"✅ Tenant found: {tenant.name}")
    print(f"   Tenant ID: {tenant.tenant_id}")
    print(f"   Plan: {tenant.plan}")
    print(f"   Role: {tenant_user.role}")
    print(f"   Created: {tenant.creation_date}")
except TenantUser.DoesNotExist:
    print(f"❌ TenantUser link not found!")
    print(f"   Run migrate_db.py to link user to tenant")
    sys.exit(1)

# Check for WhatsApp connections
print("\n3️⃣  CHECKING WHATSAPP CONNECTIONS:")
print("-" * 70)

connections = WhatsAppConnection.objects.filter(tenant=tenant)
if connections.exists():
    print(f"✅ Found {connections.count()} WhatsApp connection(s):")
    for conn in connections:
        print(f"\n   Connection ID: {conn.whatsapp_connection_id}")
        print(f"   Phone Number: {conn.phone_number}")
        print(f"   Instance ID: {conn.instance_id}")
        print(f"   Provider: {conn.provider}")
        print(f"   Access Token Ref: {conn.access_token_ref}")
        
        # Check if this is the new phone number
        if conn.phone_number == '601163955379':
            print(f"   ✅ NEW PHONE NUMBER - All set!")
        elif conn.phone_number == '60162107682':
            print(f"   ⚠️  OLD PHONE NUMBER - Run update_phone_number.py")
else:
    print(f"⚠️  No WhatsApp connections found!")
    print(f"\n   To create a connection, you have two options:")
    print(f"   A) Django Admin (Recommended):")
    print(f"      1. Go to: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/")
    print(f"      2. Login with: tenant / Tenant123!")
    print(f"      3. Go to: Messaging → WhatsApp Connections → Add")
    print(f"      4. Fill in:")
    print(f"         - Tenant: {tenant.name}")
    print(f"         - Phone number: 601163955379")
    print(f"         - Instance id: 68A0A11A89A8D")
    print(f"         - Access token ref: 68a0a10422130")
    print(f"         - Provider: wabot")
    print(f"\n   B) Python Script:")
    print(f"      Run setup_whatsapp_connection.py (already updated with new phone)")

# Check environment variables
print("\n4️⃣  CHECKING ENVIRONMENT VARIABLES:")
print("-" * 70)

env_vars = {
    'WABOT_INSTANCE_ID': os.environ.get('WABOT_INSTANCE_ID', 'NOT SET'),
    'WABOT_API_TOKEN': os.environ.get('WABOT_API_TOKEN', 'NOT SET'),
    'WABOT_PHONE_NUMBER': os.environ.get('WABOT_PHONE_NUMBER', 'NOT SET'),
    'WABOT_API_URL': os.environ.get('WABOT_API_URL', 'NOT SET'),
}

all_set = True
for key, value in env_vars.items():
    if value == 'NOT SET':
        print(f"❌ {key}: {value}")
        all_set = False
    else:
        # Mask token for security
        if 'TOKEN' in key:
            display_value = value[:5] + "***" + value[-5:] if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"✅ {key}: {display_value}")
        
        # Check if phone number is the new one
        if key == 'WABOT_PHONE_NUMBER' and value == '601163955379':
            print(f"   ✅ NEW PHONE NUMBER SET!")
        elif key == 'WABOT_PHONE_NUMBER' and value == '60162107682':
            print(f"   ⚠️  OLD PHONE NUMBER - Redeploy app.yaml with new number")

if not all_set:
    print(f"\n⚠️  Some environment variables not set in production")
    print(f"   Make sure app.yaml has all WABot configuration")

# Summary
print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)

print(f"\n✅ Login Credentials:")
print(f"   URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/")
print(f"   Username: tenant")
print(f"   Password: Tenant123!")

print(f"\n✅ Tenant Information:")
print(f"   Name: {tenant.name}")
print(f"   Plan: {tenant.plan}")

if connections.filter(phone_number='601163955379').exists():
    print(f"\n✅ WhatsApp Connection:")
    print(f"   Phone: +601163955379")
    print(f"   Status: Ready to receive messages!")
    print(f"\n📌 NEXT STEPS:")
    print(f"   1. Make sure WABot.my webhook is set to:")
    print(f"      https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/")
    print(f"   2. Test by sending a message to +601163955379")
    print(f"   3. Check logs: gcloud app logs tail -s default --project=whatsapp-bulk-messaging-480620")
elif connections.filter(phone_number='60162107682').exists():
    print(f"\n⚠️  WhatsApp Connection:")
    print(f"   Phone: 60162107682 (OLD NUMBER)")
    print(f"\n📌 ACTION REQUIRED:")
    print(f"   Run: python update_phone_number.py")
else:
    print(f"\n⚠️  WhatsApp Connection:")
    print(f"   Status: Not configured")
    print(f"\n📌 ACTION REQUIRED:")
    print(f"   Create connection via Django admin or run setup_whatsapp_connection.py")

print("\n" + "=" * 70)



