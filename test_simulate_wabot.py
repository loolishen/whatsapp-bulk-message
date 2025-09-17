#!/usr/bin/env python3
"""
Simulate WABOT webhook message to test the complete flow
"""
import requests
import json

def test_complete_flow():
    url = "http://localhost:8000/webhook/whatsapp/"
    
    # Simulate what WABOT should send
    data = {
        "type": "message",
        "data": {
            "from": "60123456789",  # Different number
            "body": "hello",        # Message text
            "id": "wabot_12345",    # WABOT message ID
            "timestamp": "2025-09-17T12:00:00Z"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🧪 Testing complete WABOT flow...")
        print(f"📤 Sending to: {url}")
        print(f"📦 Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ WABOT flow test successful!")
            print("🔍 Check your Django logs for processing details")
        else:
            print("❌ WABOT flow test failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_complete_flow()

