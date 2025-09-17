#!/usr/bin/env python
import requests
import json

def test_wabot_api():
    print("🧪 Testing WABOT API with different endpoints")
    print("=" * 50)
    
    access_token = "68a0a10422130"
    instance_id = "68A0A11A89A8D"
    
    # Try different API endpoint formats
    endpoints = [
        f"https://app.wabot.my/api/messages?access_token={access_token}&instance_id={instance_id}",
        f"https://app.wabot.my/api/get_messages?access_token={access_token}&instance_id={instance_id}",
        f"https://app.wabot.my/api/v1/messages?access_token={access_token}&instance_id={instance_id}",
        f"https://app.wabot.my/api/instance/{instance_id}/messages?access_token={access_token}",
    ]
    
    for i, url in enumerate(endpoints, 1):
        print(f"\n{i}. Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Success! Response: {json.dumps(data, indent=2)[:200]}...")
                    break
                except:
                    print(f"   Response (first 200 chars): {response.text[:200]}")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Also try with headers instead of query params
    print(f"\n5. Testing with headers...")
    try:
        url = "https://app.wabot.my/api/messages"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        params = {'instance_id': instance_id}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == '__main__':
    test_wabot_api()
