#!/usr/bin/env python3
"""
Quick test script to verify WABot Send Message API works
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.whatsapp_service import WhatsAppAPIService

def test_send_message():
    """Test sending a simple message via WABot API"""
    
    # Initialize WABot service
    wa_service = WhatsAppAPIService()
    
    print("=" * 60)
    print("🧪 WABot Send Message Test")
    print("=" * 60)
    print(f"Instance ID: {wa_service.instance_id}")
    print(f"API URL: {wa_service.base_url}")
    print(f"Access Token: {wa_service.access_token[:10]}...")
    print()
    
    # Test phone number (your own number for testing)
    test_phone = "60162107682"  # Your WABot number
    test_message = "🤖 Test message from Django webhook!\n\nIf you see this, the WABot API is working correctly! ✅"
    
    print(f"📱 Sending test message to: {test_phone}")
    print(f"💬 Message: {test_message[:50]}...")
    print()
    
    # Send the message
    result = wa_service.send_text_message(test_phone, test_message)
    
    print("=" * 60)
    print("📊 RESULT:")
    print("=" * 60)
    
    if result.get('success'):
        print("✅ SUCCESS! Message sent via WABot API")
        print(f"Response: {result.get('data')}")
        print()
        print("👉 Check your WhatsApp - you should receive the test message!")
    else:
        print("❌ FAILED! Could not send message")
        print(f"Error: {result.get('error')}")
        print()
        print("🔍 Troubleshooting:")
        print("  1. Check if WABot instance is connected")
        print("  2. Verify API token and instance ID in app.yaml")
        print("  3. Check WABot dashboard for errors")
    
    print("=" * 60)

if __name__ == '__main__':
    test_send_message()

