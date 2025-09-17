#!/usr/bin/env python3
"""
Test complete contest flow with PDPA integration
"""
import requests
import json

def test_contest_flow():
    url = "http://localhost:8000/webhook/whatsapp/"
    
    # Test 1: Initial message (should trigger PDPA)
    print("🧪 Test 1: Initial message (PDPA trigger)")
    data1 = {
        "type": "message",
        "data": {
            "from": "60123456789",
            "body": "hello",
            "id": "wabot_001",
            "timestamp": "2025-09-17T12:00:00Z"
        }
    }
    
    response1 = requests.post(url, json=data1, headers={"Content-Type": "application/json"})
    print(f"📊 Status: {response1.status_code}")
    print(f"📝 Response: {response1.text}")
    
    # Test 2: PDPA consent (YES)
    print("\n🧪 Test 2: PDPA consent (YES)")
    data2 = {
        "type": "message",
        "data": {
            "from": "60123456789",
            "body": "YES",
            "id": "wabot_002",
            "timestamp": "2025-09-17T12:01:00Z"
        }
    }
    
    response2 = requests.post(url, json=data2, headers={"Content-Type": "application/json"})
    print(f"📊 Status: {response2.status_code}")
    print(f"📝 Response: {response2.text}")
    
    # Test 3: Contest message
    print("\n🧪 Test 3: Contest message")
    data3 = {
        "type": "message",
        "data": {
            "from": "60123456789",
            "body": "I want to join the contest",
            "id": "wabot_003",
            "timestamp": "2025-09-17T12:02:00Z"
        }
    }
    
    response3 = requests.post(url, json=data3, headers={"Content-Type": "application/json"})
    print(f"📊 Status: {response3.status_code}")
    print(f"📝 Response: {response3.text}")
    
    print("\n✅ Complete contest flow test finished!")
    print("🔍 Check your Django logs and database for results")

if __name__ == "__main__":
    test_contest_flow()

