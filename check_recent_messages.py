#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import CoreMessage, Customer, Contest, Tenant
from django.utils import timezone
from datetime import timedelta

def check_recent_messages():
    print("📱 Checking Recent Messages")
    print("=" * 50)
    
    # Check recent messages
    recent_time = timezone.now() - timedelta(hours=1)
    messages = CoreMessage.objects.filter(
        created_at__gte=recent_time,
        direction='inbound'
    ).order_by('-created_at')
    
    print(f"📊 Messages in last hour: {messages.count()}")
    
    for msg in messages[:5]:  # Show last 5 messages
        print(f"   - {msg.created_at}: {msg.text_body[:50]}...")
        print(f"     From: {msg.conversation.customer.phone_number if msg.conversation else 'Unknown'}")
        print(f"     Tenant: {msg.tenant.name if msg.tenant else 'None'}")
        print()
    
    # Check customers
    customers = Customer.objects.all()
    print(f"👥 Total customers: {customers.count()}")
    
    for customer in customers[:3]:
        print(f"   - {customer.name} ({customer.phone_number})")
        print(f"     Last interaction: {customer.last_whatsapp_interaction}")
        print()
    
    # Check contests
    tenant = Tenant.objects.first()
    if tenant:
        contests = Contest.objects.filter(tenant=tenant)
        print(f"🏆 Contests: {contests.count()}")
        
        for contest in contests:
            now = timezone.now()
            is_active = contest.is_active and contest.starts_at <= now <= contest.ends_at
            print(f"   - {contest.name}")
            print(f"     Active: {contest.is_active}")
            print(f"     Currently Active: {is_active}")
            print(f"     Starts: {contest.starts_at}")
            print(f"     Ends: {contest.ends_at}")
            print()

if __name__ == '__main__':
    check_recent_messages()
