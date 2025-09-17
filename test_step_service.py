#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

print("🧪 Testing Step-by-Step Contest Service")
print("=" * 50)

from messaging.models import Contest, Customer, Tenant, Conversation, WhatsAppConnection
from messaging.step_by_step_contest_service import StepByStepContestService
from django.utils import timezone

# Get tenant
tenant = Tenant.objects.first()
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

# Create test customer
test_phone = "60123456789"
customer, created = Customer.objects.get_or_create(
    phone_number=test_phone,
    tenant=tenant,
    defaults={'name': f'Test Customer {test_phone}'}
)
print(f"👤 Customer: {customer.name} ({customer.phone_number})")

# Create WhatsApp connection
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

# Test the step-by-step service
print(f"\n🔄 Testing message: 'hello'")

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
    print("   Errors:", contest_results.get('errors', []))

print("Test completed!")
