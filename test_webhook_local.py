#!/usr/bin/env python
import requests
import json

def test_webhook():
    print("🧪 Testing Webhook Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "type": "message",
        "data": {
            "from": "60123456789",
            "message": "hello",
            "id": "test_123",
            "timestamp": "2025-09-17T16:21:00Z"
        }
    }
    
    # Test local webhook
    local_url = "http://localhost:8000/webhook/whatsapp/"
    ngrok_url = "https://891d6af694a3.ngrok-free.app/webhook/whatsapp/"
    
    print("1. Testing local webhook...")
    try:
        response = requests.post(local_url, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n2. Testing ngrok webhook...")
    try:
        response = requests.post(ngrok_url, json=test_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == '__main__':
    test_webhook()
