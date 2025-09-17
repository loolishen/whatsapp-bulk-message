"""
Management command to test contest flow manually
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.models import Contest, Customer, Tenant, Conversation, WhatsAppConnection, ContestFlowState
from messaging.step_by_step_contest_service import StepByStepContestService
from messaging.pdpa_service import PDPAConsentService

class Command(BaseCommand):
    help = 'Test contest flow manually'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            default='60123456789',
            help='Phone number to test with'
        )
        parser.add_argument(
            '--message',
            type=str,
            default='hello',
            help='Message to test with'
        )
    
    def handle(self, *args, **options):
        phone = options['phone']
        message = options['message']
        
        self.stdout.write("🧪 Testing Contest Flow Manually")
        self.stdout.write("=" * 50)
        
        # Get tenant
        tenant = Tenant.objects.first()
        if not tenant:
            self.stdout.write(self.style.ERROR("❌ No tenant found"))
            return
        
        self.stdout.write(f"✅ Tenant: {tenant.name}")
        
        # Get active contests
        now = timezone.now()
        active_contests = Contest.objects.filter(
            tenant=tenant,
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        )
        
        self.stdout.write(f"🎯 Active contests: {active_contests.count()}")
        for contest in active_contests:
            self.stdout.write(f"   - {contest.name}")
            self.stdout.write(f"     Custom PDPA: {bool(contest.custom_pdpa_message)}")
            self.stdout.write(f"     Custom Instructions: {bool(contest.custom_instructions)}")
        
        if not active_contests.exists():
            self.stdout.write(self.style.ERROR("❌ No active contests found"))
            return
        
        # Create test customer
        customer, created = Customer.objects.get_or_create(
            phone_number=phone,
            tenant=tenant,
            defaults={'name': f'Test Customer {phone}'}
        )
        
        self.stdout.write(f"\n👤 Customer: {customer.name} ({customer.phone_number})")
        
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
        
        self.stdout.write(f"💬 Conversation: {'Created' if created else 'Found'}")
        
        # Test the services
        self.stdout.write(f"\n🔄 Testing message: '{message}'")
        
        # Test PDPA service
        pdpa_service = PDPAConsentService()
        pdpa_handled = pdpa_service.handle_incoming_message(customer, message, tenant)
        self.stdout.write(f"📋 PDPA handled: {pdpa_handled}")
        
        # Test step-by-step contest service
        step_service = StepByStepContestService()
        contest_results = step_service.process_message_for_contests(
            customer, message, tenant, conversation
        )
        
        self.stdout.write(f"🏆 Contest results: {contest_results}")
        
        if contest_results['flows_processed'] > 0:
            self.stdout.write(self.style.SUCCESS("✅ Step-by-step flow was triggered!"))
            
            # Check if flow state was created
            flow_states = ContestFlowState.objects.filter(customer=customer)
            self.stdout.write(f"📊 Flow states created: {flow_states.count()}")
            
            for flow in flow_states:
                self.stdout.write(f"   - {flow.contest.name}: {flow.current_step}")
        else:
            self.stdout.write(self.style.WARNING("❌ Step-by-step flow was NOT triggered"))
            self.stdout.write("   Possible reasons:")
            self.stdout.write("   - No active contests")
            self.stdout.write("   - Customer already has a flow for this contest")
            self.stdout.write("   - Contest doesn't have custom messages")
