#!/usr/bin/env python
"""
Test Echo Bot - Verify WABot API replies work
Run this after deploying to test that your bot can reply to messages
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.whatsapp_service import WhatsAppAPIService

def test_send_message(phone_number, message):
    """Test sending a message via WABot API"""
    print(f"\n🧪 Testing WABot Send Message API")
    print(f"   Phone: {phone_number}")
    print(f"   Message: {message}")
    print("-" * 50)
    
    service = WhatsAppAPIService()
    
    print(f"✓ Service initialized")
    print(f"   Instance ID: {service.instance_id}")
    print(f"   Base URL: {service.base_url}")
    print(f"   Access Token: {service.access_token[:10]}...")
    
    result = service.send_text_message(phone_number, message)
    
    print(f"\n📤 Send result:")
    if result['success']:
        print(f"   ✅ SUCCESS")
        print(f"   Response: {result.get('data', {})}")
        return True
    else:
        print(f"   ❌ FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    # Test with your own phone number
    test_phone = "60162657629"  # Your WABot number - will send to yourself
    test_message = "🤖 Echo Bot Test - If you receive this, replies are working!"
    
    print("=" * 50)
    print("WABot Echo Bot Test")
    print("=" * 50)
    
    success = test_send_message(test_phone, test_message)
    
    if success:
        print("\n✅ Test passed! Check your WhatsApp for the message.")
        print("   If you received it, the bot can now reply to users!")
    else:
        print("\n❌ Test failed. Check the error above.")
        print("   Possible issues:")
        print("   - WABot instance not connected")
        print("   - Invalid credentials")
        print("   - Phone number format incorrect")


"""
Test Echo Bot - Verify WABot API replies work
Run this after deploying to test that your bot can reply to messages
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.whatsapp_service import WhatsAppAPIService

def test_send_message(phone_number, message):
    """Test sending a message via WABot API"""
    print(f"\n🧪 Testing WABot Send Message API")
    print(f"   Phone: {phone_number}")
    print(f"   Message: {message}")
    print("-" * 50)
    
    service = WhatsAppAPIService()
    
    print(f"✓ Service initialized")
    print(f"   Instance ID: {service.instance_id}")
    print(f"   Base URL: {service.base_url}")
    print(f"   Access Token: {service.access_token[:10]}...")
    
    result = service.send_text_message(phone_number, message)
    
    print(f"\n📤 Send result:")
    if result['success']:
        print(f"   ✅ SUCCESS")
        print(f"   Response: {result.get('data', {})}")
        return True
    else:
        print(f"   ❌ FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    # Test with your own phone number
    test_phone = "60162657629"  # Your WABot number - will send to yourself
    test_message = "🤖 Echo Bot Test - If you receive this, replies are working!"
    
    print("=" * 50)
    print("WABot Echo Bot Test")
    print("=" * 50)
    
    success = test_send_message(test_phone, test_message)
    
    if success:
        print("\n✅ Test passed! Check your WhatsApp for the message.")
        print("   If you received it, the bot can now reply to users!")
    else:
        print("\n❌ Test failed. Check the error above.")
        print("   Possible issues:")
        print("   - WABot instance not connected")
        print("   - Invalid credentials")
        print("   - Phone number format incorrect")




