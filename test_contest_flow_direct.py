#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Contest, Customer, Tenant, Conversation, WhatsAppConnection
from messaging.step_by_step_contest_service import StepByStepContestService
from messaging.pdpa_service import PDPAConsentService
from django.utils import timezone

def test_contest_flow_direct():
    print("🧪 Testing Contest Flow Directly")
    print("=" * 50)
    
    try:
    
    # Get tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found")
        return
    
    print(f"✅ Tenant: {tenant.name}")
    
    # Get active contests
    now = timezone.now()
    active_contests = Contest.objects.filter(
        tenant=tenant,
        is_active=True,
        starts_at__lte=now,
        ends_at__gte=now
    )
    
    print(f"🎯 Active contests: {active_contests.count()}")
    for contest in active_contests:
        print(f"   - {contest.name}")
        print(f"     Custom PDPA: {bool(contest.custom_pdpa_message)}")
        print(f"     Custom Instructions: {bool(contest.custom_instructions)}")
    
    if not active_contests.exists():
        print("❌ No active contests found")
        return
    
    # Create test customer
    test_phone = "60123456789"
    customer, created = Customer.objects.get_or_create(
        phone_number=test_phone,
        tenant=tenant,
        defaults={'name': 'Test Customer'}
    )
    
    print(f"\n👤 Customer: {customer.name} ({customer.phone_number})")
    
    # Create WhatsApp connection if it doesn't exist
    conn, created = WhatsAppConnection.objects.get_or_create(
        tenant=tenant,
        defaults={'instance_id': 'test_instance'}
    )
    
    # Create conversation
    conversation, created = Conversation.objects.get_or_create(
        tenant=tenant,
        customer=customer,
        whatsapp_connection=conn,
        defaults={}
    )
    
    print(f"💬 Conversation: {'Created' if created else 'Found'}")
    
    # Test the services
    print(f"\n🔄 Testing message: 'hello'")
    
    # Test PDPA service
    pdpa_service = PDPAConsentService()
    pdpa_handled = pdpa_service.handle_incoming_message(customer, "hello", tenant)
    print(f"📋 PDPA handled: {pdpa_handled}")
    
    # Test step-by-step contest service
    step_service = StepByStepContestService()
    contest_results = step_service.process_message_for_contests(
        customer, "hello", tenant, conversation
    )
    
    print(f"🏆 Contest results: {contest_results}")
    
    if contest_results['flows_processed'] > 0:
        print("✅ Step-by-step flow was triggered!")
        
        # Check if flow state was created
        from messaging.models import ContestFlowState
        flow_states = ContestFlowState.objects.filter(customer=customer)
        print(f"📊 Flow states created: {flow_states.count()}")
        
        for flow in flow_states:
            print(f"   - {flow.contest.name}: {flow.current_step}")
    else:
        print("❌ Step-by-step flow was NOT triggered")
        print("   Possible reasons:")
        print("   - No active contests")
        print("   - Customer already has a flow for this contest")
        print("   - Contest doesn't have custom messages")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_contest_flow_direct()
