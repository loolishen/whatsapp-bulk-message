#!/usr/bin/env python
import os
import sys
import django
import json
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Contest, Customer, Tenant
from messaging.step_by_step_contest_service import StepByStepContestService

def test_webhook_simulation():
    print("🧪 Testing Webhook Simulation")
    print("=" * 50)
    
    # Get the tenant and contest
    try:
        tenant = Tenant.objects.first()
        if not tenant:
            print("❌ No tenant found")
            return
        
        print(f"✅ Found tenant: {tenant.name}")
        
        # Get the most recent contest
        contest = Contest.objects.filter(tenant=tenant).order_by('-created_at').first()
        if not contest:
            print("❌ No contest found")
            return
            
        print(f"✅ Found contest: {contest.name}")
        print(f"   - Active: {contest.is_active}")
        print(f"   - Starts: {contest.starts_at}")
        print(f"   - Ends: {contest.ends_at}")
        
        # Check if contest is currently active
        from django.utils import timezone
        now = timezone.now()
        is_active = contest.is_active and contest.starts_at <= now <= contest.ends_at
        print(f"   - Currently Active: {is_active}")
        
        # Create a test customer
        test_phone = "60123456789"
        customer, created = Customer.objects.get_or_create(
            phone_number=test_phone,
            tenant=tenant,
            defaults={'name': 'Test Customer'}
        )
        
        if created:
            print(f"✅ Created test customer: {customer.name}")
        else:
            print(f"✅ Found existing customer: {customer.name}")
        
        # Test the step-by-step service
        service = StepByStepContestService()
        
        # Simulate a message
        message_text = "hello"
        print(f"\n🔄 Testing message: '{message_text}'")
        
        # Create a mock conversation
        from messaging.models import Conversation
        conversation, created = Conversation.objects.get_or_create(
            customer=customer,
            tenant=tenant,
            defaults={'status': 'active'}
        )
        
        # Process the message
        results = service.process_message_for_contests(
            customer, message_text, tenant, conversation
        )
        
        print(f"📊 Results: {results}")
        
        if results['flows_processed'] > 0:
            print("✅ Step-by-step flow was triggered!")
        else:
            print("❌ Step-by-step flow was NOT triggered")
            print("   This could be because:")
            print("   - No active contests found")
            print("   - Contest is not in the right time period")
            print("   - Customer already has a flow for this contest")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_webhook_simulation()
