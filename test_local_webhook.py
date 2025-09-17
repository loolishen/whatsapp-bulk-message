#!/usr/bin/env python
import requests
import json

def test_local_webhook():
    """Test the local webhook endpoint"""
    print("🧪 Testing Local Webhook Endpoint")
    print("=" * 40)
    
    # Local webhook URL
    webhook_url = "http://127.0.0.1:8000/webhook/whatsapp/"
    
    # Test WABOT webhook payload
    test_payload = {
        "type": "message",
        "data": {
            "id": "test_msg_001",
            "from": "60162107682",
            "message": "hello",
            "timestamp": "1640995200"
        }
    }
    
    print(f"📡 Sending webhook to: {webhook_url}")
    print(f"📱 From: {test_payload['data']['from']}")
    print(f"💬 Message: {test_payload['data']['message']}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Is Django server running?")
        print("💡 Run: python manage.py runserver 0.0.0.0:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_local_webhook()
