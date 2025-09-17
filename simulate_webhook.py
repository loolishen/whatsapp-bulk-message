#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.whatsapp_webhook import WhatsAppWebhookView
from django.test import RequestFactory
import json

def simulate_webhook():
    print("🧪 Simulating Webhook Call")
    print("=" * 50)
    
    # Create a mock request
    factory = RequestFactory()
    
    # Test data in WABOT format
    test_data = {
        "type": "message",
        "data": {
            "from": "60123456789",  # Your friend's number
            "message": "hello",
            "id": "test_message_123",
            "timestamp": "2025-09-17T16:21:00Z"
        }
    }
    
    # Create POST request
    request = factory.post(
        '/webhook/whatsapp/',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Process the request
    webhook_view = WhatsAppWebhookView()
    response = webhook_view.post(request)
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    
    # Check if any messages were created
    from messaging.models import CoreMessage
    recent_messages = CoreMessage.objects.filter(
        text_body="hello"
    ).order_by('-created_at')
    
    print(f"\nMessages created: {recent_messages.count()}")
    for msg in recent_messages:
        print(f"  - {msg.created_at}: {msg.text_body}")

if __name__ == '__main__':
    simulate_webhook()
