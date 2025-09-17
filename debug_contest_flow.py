#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Contest, Customer, Tenant, Conversation
from messaging.step_by_step_contest_service import StepByStepContestService
from django.utils import timezone

def debug_contest_flow():
    print("🔍 Debugging Contest Flow")
    print("=" * 50)
    
    # Get tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found")
        return
    
    print(f"✅ Tenant: {tenant.name}")
    
    # Get all contests
    contests = Contest.objects.filter(tenant=tenant).order_by('-created_at')
    print(f"📊 Total contests: {contests.count()}")
    
    for contest in contests:
        now = timezone.now()
        is_active = contest.is_active and contest.starts_at <= now <= contest.ends_at
        print(f"   - {contest.name}")
        print(f"     Active: {contest.is_active}")
        print(f"     Starts: {contest.starts_at}")
        print(f"     Ends: {contest.ends_at}")
        print(f"     Currently Active: {is_active}")
        print(f"     Has Custom Messages: {bool(contest.custom_pdpa_message or contest.custom_instructions)}")
        print()
    
    # Get active contests
    active_contests = contests.filter(is_active=True)
    now = timezone.now()
    currently_active = [c for c in active_contests if c.starts_at <= now <= c.ends_at]
    
    print(f"🎯 Currently Active Contests: {len(currently_active)}")
    for contest in currently_active:
        print(f"   - {contest.name}")
    
    # Test with a customer
    test_phone = "60123456789"
    customer, created = Customer.objects.get_or_create(
        phone_number=test_phone,
        tenant=tenant,
        defaults={'name': 'Test Customer'}
    )
    
    print(f"\n👤 Customer: {customer.name} ({customer.phone_number})")
    
    # Create conversation
    from messaging.models import WhatsAppConnection
    conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
    if conn:
        conversation, created = Conversation.objects.get_or_create(
            tenant=tenant,
            customer=customer,
            whatsapp_connection=conn,
            defaults={}
        )
        print(f"💬 Conversation: {'Created' if created else 'Found'}")
    else:
        conversation = None
        print("❌ No WhatsApp connection found")
    
    # Test the service
    service = StepByStepContestService()
    message_text = "hello"
    
    print(f"\n🔄 Testing message: '{message_text}'")
    
    try:
        results = service.process_message_for_contests(
            customer, message_text, tenant, conversation
        )
        
        print(f"📊 Results: {results}")
        
        if results['flows_processed'] > 0:
            print("✅ Step-by-step flow was triggered!")
        else:
            print("❌ Step-by-step flow was NOT triggered")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_contest_flow()
