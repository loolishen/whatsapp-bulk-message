#!/usr/bin/env python
import requests
import json

def test_wabot_api():
    print("🧪 Testing WABOT API")
    print("=" * 50)
    
    base_url = "https://app.wabot.my/api"
    access_token = "68a0a10422130"
    instance_id = "68A0A11A89A8D"
    
    # Test getting messages
    url = f"{base_url}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'instance_id': instance_id,
        'limit': 10
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            print(f"Found {len(messages)} messages")
            
            for msg in messages[:3]:  # Show first 3 messages
                print(f"  - {msg.get('from')}: {msg.get('body', '')}")
        else:
            print("❌ API call failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_wabot_api()
