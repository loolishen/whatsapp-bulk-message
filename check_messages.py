#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import CoreMessage, Customer
from django.utils import timezone
from datetime import timedelta

# Check recent messages
recent_time = timezone.now() - timedelta(hours=1)
messages = CoreMessage.objects.filter(created_at__gte=recent_time).order_by('-created_at')

print(f"📱 Recent messages: {messages.count()}")
for msg in messages:
    print(f"   {msg.created_at}: {msg.text_body} (from: {msg.conversation.customer.phone_number if msg.conversation else 'Unknown'})")

# Check customers
customers = Customer.objects.all()
print(f"\n👥 Customers: {customers.count()}")
for customer in customers:
    print(f"   {customer.name} ({customer.phone_number})")
