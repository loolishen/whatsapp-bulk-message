#!/usr/bin/env python3
"""
Test webhook with debug output
"""
import requests
import json

def test_debug_webhook():
    url = "http://localhost:8000/debug-webhook/"
    
    # Test data
    data = {
        "type": "message",
        "data": {
            "from": "60162107682",
            "body": "test message",
            "id": "test123"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing debug webhook...")
        print(f"📤 Sending to: {url}")
        print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Debug webhook test successful!")
        else:
            print("❌ Debug webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_debug_webhook()

