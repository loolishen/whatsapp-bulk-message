#!/usr/bin/env python
import os
import sys
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Customer, Tenant, Consent, CoreMessage, Conversation, WhatsAppConnection
from messaging.pdpa_service import PDPAConsentService

def test_wabot_webhook():
    """Test WABOT webhook integration"""
    print("🧪 Testing WABOT Webhook Integration")
    print("=" * 50)
    
    # Test webhook URL (replace with your actual webhook URL)
    webhook_url = "http://127.0.0.1:8000/webhook/whatsapp/"
    
    # Simulate WABOT webhook payload
    test_payload = {
        "type": "message",
        "data": {
            "id": "test_msg_123",
            "from": "60162107682",
            "message": "hello",
            "timestamp": "1640995200"
        }
    }
    
    print(f"📱 Testing with phone: {test_payload['data']['from']}")
    print(f"💬 Message: {test_payload['data']['message']}")
    
    try:
        # Send webhook request
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Webhook Response: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
            
            # Check if customer was created
            tenant = Tenant.objects.first()
            if tenant:
                customer = Customer.objects.filter(
                    phone_number__icontains="60162107682",
                    tenant=tenant
                ).first()
                
                if customer:
                    print(f"✅ Customer found: {customer.name}")
                    print(f"   - Phone: {customer.phone_number}")
                    print(f"   - Created: {customer.created_at}")
                    
                    # Check messages
                    messages = CoreMessage.objects.filter(
                        tenant=tenant,
                        conversation__customer=customer
                    ).order_by('-created_at')
                    
                    print(f"💬 Messages found: {messages.count()}")
                    for msg in messages:
                        print(f"   - {msg.direction.upper()}: {msg.text_body} ({msg.created_at})")
                    
                    # Check consent
                    consents = Consent.objects.filter(
                        tenant=tenant,
                        customer=customer,
                        type='whatsapp'
                    ).order_by('-occurred_at')
                    
                    print(f"📋 Consent records: {consents.count()}")
                    for consent in consents:
                        print(f"   - {consent.status.upper()}: {consent.occurred_at}")
                else:
                    print("❌ No customer found")
            else:
                print("❌ No tenant found")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")

def test_whatsapp_service():
    """Test WhatsApp service directly"""
    print("\n🔧 Testing WhatsApp Service")
    print("=" * 30)
    
    from messaging.whatsapp_service import WhatsAppAPIService
    
    wa_service = WhatsAppAPIService()
    
    # Test instance status
    print("📊 Checking instance status...")
    status = wa_service.get_instance_status()
    print(f"Status: {status}")
    
    # Test sending message
    print("\n📤 Testing message send...")
    result = wa_service.send_text_message("60162107682", "Test message from Django app")
    print(f"Send result: {result}")

if __name__ == "__main__":
    test_wabot_webhook()
    test_whatsapp_service()
