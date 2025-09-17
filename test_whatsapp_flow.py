#!/usr/bin/env python
"""
Test WhatsApp flow with WABOT integration
"""
import requests
import json
import time

# Your webhook URL (replace with your actual URL)
WEBHOOK_URL = "http://127.0.0.1:8000/webhook/whatsapp/"

# Test phone number (replace with your actual number)
TEST_PHONE = "60162107682"  # Replace with your WhatsApp number

def test_whatsapp_webhook():
    """Test the WhatsApp webhook with a simple message"""
    
    print("🧪 Testing WhatsApp Webhook Integration")
    print("=" * 50)
    
    # Test message payload (WABOT format)
    test_payload = {
        "type": "message",
        "data": {
            "id": f"test_msg_{int(time.time())}",
            "from": TEST_PHONE,
            "to": "601112345678",  # Your WABOT number
            "message": "hello",
            "timestamp": str(int(time.time())),
            "instance_id": "68A0A11A89A8D"
        }
    }
    
    print(f"📱 Sending test message from: {TEST_PHONE}")
    print(f"💬 Message: 'hello'")
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
            print("\n🎯 What should happen next:")
            print("1. Customer should be created in database")
            print("2. PDPA consent message should be sent")
            print("3. Contest entry should be created (if contest is active)")
            print("4. Custom post-PDPA messages should be sent")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Is Django server running?")
        print("💡 Make sure to run: python manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_whatsapp_webhook()