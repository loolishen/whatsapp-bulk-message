#!/usr/bin/env python3
"""
Simple webhook test
"""
import requests
import json

def test_webhook():
    url = "http://localhost:8000/webhook/whatsapp/"
    
    # Test data
    data = {
        "type": "message",
        "data": {
            "from": "60162107682",
            "body": "hello",
            "id": "test123"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing webhook...")
        print(f"📤 Sending to: {url}")
        print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook()

