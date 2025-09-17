#!/usr/bin/env python
import os
import sys
import django
import json
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

def test_webhook_call():
    print("🧪 Testing Webhook Call")
    print("=" * 50)
    
    # Test data in WABOT format
    test_data = {
        "type": "message",
        "data": {
            "from": "60123456789",  # Your friend's number
            "message": "hello",
            "id": "test_message_123",
            "timestamp": "2025-09-17T16:00:00Z"
        }
    }
    
    # Make the webhook call
    webhook_url = "http://localhost:8000/webhook/whatsapp/"
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"✅ Webhook call successful!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Webhook call failed: {e}")

if __name__ == '__main__':
    test_webhook_call()
