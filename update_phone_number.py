#!/usr/bin/env python
"""
Update WhatsApp Connection phone number from old to new
Run this in Cloud Shell after deploying with the new phone number
"""
import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from messaging.models import WhatsAppConnection, Tenant

print("=" * 70)
print("UPDATING WHATSAPP CONNECTION PHONE NUMBER")
print("=" * 70)

OLD_PHONE = '601163955379'
NEW_PHONE = '60162107682'

try:
    # Find all connections with the old phone number
    old_connections = WhatsAppConnection.objects.filter(phone_number=OLD_PHONE)
    count = old_connections.count()
    
    if count == 0:
        print(f"\n✅ No connections found with old phone number {OLD_PHONE}")
        print(f"   Checking for new phone number {NEW_PHONE}...")
        
        new_connections = WhatsAppConnection.objects.filter(phone_number=NEW_PHONE)
        if new_connections.exists():
            print(f"\n✅ Found {new_connections.count()} connection(s) with new phone number!")
            for conn in new_connections:
                print(f"   - Tenant: {conn.tenant.name}")
                print(f"   - Phone: {conn.phone_number}")
                print(f"   - Instance ID: {conn.instance_id}")
                print(f"   - Provider: {conn.provider}")
        else:
            print(f"\n⚠️  No connections found with new phone number either.")
            print(f"   You may need to create a new WhatsAppConnection:")
            print(f"   1. Login to Django admin: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/")
            print(f"   2. Go to Messaging → WhatsApp Connections")
            print(f"   3. Add new connection with phone: {NEW_PHONE}")
            print(f"   4. Instance ID: 68A0A11A89A8D")
            print(f"   5. Access token ref: 68a0a10422130")
            print(f"   6. Provider: wabot")
    else:
        print(f"\n📞 Found {count} connection(s) with old phone number {OLD_PHONE}")
        print(f"   Updating to new phone number {NEW_PHONE}...")
        
        for conn in old_connections:
            print(f"\n   Updating connection for tenant: {conn.tenant.name}")
            print(f"   - Old phone: {conn.phone_number}")
            
            # Update the phone number
            conn.phone_number = NEW_PHONE
            conn.save()
            
            print(f"   - New phone: {conn.phone_number}")
            print(f"   - Instance ID: {conn.instance_id}")
            print(f"   - Provider: {conn.provider}")
        
        print(f"\n✅ Successfully updated {count} connection(s)!")
    
    # Show all current connections
    print(f"\n{'=' * 70}")
    print("CURRENT WHATSAPP CONNECTIONS:")
    print(f"{'=' * 70}")
    
    all_connections = WhatsAppConnection.objects.all()
    if all_connections.exists():
        for conn in all_connections:
            print(f"\n  Tenant: {conn.tenant.name}")
            print(f"  Phone: {conn.phone_number}")
            print(f"  Instance ID: {conn.instance_id}")
            print(f"  Provider: {conn.provider}")
            print(f"  {'-' * 68}")
    else:
        print("\n  No WhatsApp connections found in database.")
    
    print(f"\n{'=' * 70}")
    print("UPDATE COMPLETE!")
    print(f"{'=' * 70}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

