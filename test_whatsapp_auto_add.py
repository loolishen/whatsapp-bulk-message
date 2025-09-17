#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Customer, Tenant, Consent, CoreMessage, Conversation, WhatsAppConnection
from messaging.pdpa_service import PDPAConsentService
from messaging.whatsapp_webhook import WhatsAppWebhookView
from django.utils import timezone

def test_whatsapp_auto_add():
    """Test WhatsApp auto-add functionality"""
    print("🧪 Testing WhatsApp Auto-Add Functionality")
    print("=" * 50)
    
    # Get or create tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Creating test tenant...")
        tenant = Tenant.objects.create(
            name="Test Tenant",
            description="Test tenant for WhatsApp auto-add"
        )
        print(f"✅ Created tenant: {tenant.name}")
    else:
        print(f"✅ Using tenant: {tenant.name}")
    
    # Test phone number (your number)
    test_phone = "60162107682"
    print(f"📱 Testing with phone: {test_phone}")
    
    # Initialize webhook handler
    webhook = WhatsAppWebhookView()
    
    # Simulate incoming message data
    message_data = {
        'id': 'test_message_123',
        'from': test_phone,
        'timestamp': str(int(timezone.now().timestamp())),
        'type': 'text',
        'text': {
            'body': 'hello'
        }
    }
    
    print("\n1️⃣ Simulating incoming 'hello' message...")
    
    # Get or create customer
    customer = webhook._get_or_create_contact(test_phone)
    if not customer:
        print("❌ Failed to create/find customer")
        return
    
    print(f"✅ Customer: {customer.name} ({customer.phone_number})")
    print(f"   - Customer ID: {customer.customer_id}")
    print(f"   - Tenant: {customer.tenant.name}")
    print(f"   - Created: {customer.created_at}")
    
    # Test PDPA service
    print("\n2️⃣ Testing PDPA service...")
    pdpa_service = PDPAConsentService()
    
    # Check current consent status
    consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
    print(f"📋 Current consent status: {consent_status}")
    
    # Simulate PDPA handling
    result = pdpa_service.handle_incoming_message(customer, "hello", tenant)
    print(f"✅ PDPA service result: {result}")
    
    # Check updated consent status
    new_consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
    print(f"📋 Updated consent status: {new_consent_status}")
    
    # Test IC number processing
    print("\n3️⃣ Testing IC number processing...")
    ic_result = pdpa_service.handle_incoming_message(customer, "901231-01-1234", tenant)
    print(f"✅ IC processing result: {ic_result}")
    
    if ic_result:
        # Refresh customer data
        customer.refresh_from_db()
        print(f"📊 Updated customer info:")
        print(f"   - Name: {customer.name}")
        print(f"   - Age: {customer.age}")
        print(f"   - Gender: {customer.gender}")
        print(f"   - State: {customer.state}")
        print(f"   - IC: {customer.ic_number}")
    
    # Test consent responses
    print("\n4️⃣ Testing consent responses...")
    
    # Test YES response
    print("Testing 'YES' response...")
    yes_result = pdpa_service.handle_incoming_message(customer, "yes", tenant)
    print(f"✅ YES result: {yes_result}")
    
    # Test STOP response
    print("Testing 'STOP' response...")
    stop_result = pdpa_service.handle_incoming_message(customer, "stop", tenant)
    print(f"✅ STOP result: {stop_result}")
    
    # Final status
    final_consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
    print(f"\n📋 Final consent status: {final_consent_status}")
    
    # Show consent history
    consents = Consent.objects.filter(
        tenant=tenant,
        customer=customer,
        type='whatsapp'
    ).order_by('-occurred_at')
    
    print(f"\n📜 Consent History ({consents.count()} records):")
    for consent in consents:
        print(f"   {consent.occurred_at.strftime('%Y-%m-%d %H:%M:%S')} - {consent.status.upper()}")
    
    # Show messages
    messages = CoreMessage.objects.filter(
        tenant=tenant,
        conversation__customer=customer
    ).order_by('-created_at')
    
    print(f"\n💬 Messages ({messages.count()} records):")
    for message in messages:
        print(f"   {message.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {message.direction.upper()}: {message.text_body[:50]}...")
    
    print("\n🎉 Test completed!")
    print(f"\n📊 Summary:")
    print(f"   - Customer created: {customer.name}")
    print(f"   - Phone: {customer.phone_number}")
    print(f"   - Consent status: {final_consent_status}")
    print(f"   - Total messages: {messages.count()}")
    print(f"   - Consent records: {consents.count()}")

if __name__ == "__main__":
    test_whatsapp_auto_add()
