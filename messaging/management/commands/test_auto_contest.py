from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from messaging.models import Tenant, Customer, Contest, ContestEntry
from messaging.auto_contest_service import AutoContestService

class Command(BaseCommand):
    help = 'Test automatic contest entry functionality'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, default='Demo Tenant', help='Tenant name')
        parser.add_argument('--phone', type=str, default='60123456789', help='Test phone number')
        parser.add_argument('--message', type=str, default='hello', help='Test message')

    def handle(self, *args, **options):
        tenant_name = options['tenant']
        phone_number = options['phone']
        message_text = options['message']
        
        print("🧪 Testing Auto Contest Entry Functionality")
        print("=" * 50)
        
        try:
            # Get tenant
            tenant = Tenant.objects.filter(name=tenant_name).first()
            if not tenant:
                self.stdout.write(self.style.ERROR(f"Tenant '{tenant_name}' not found"))
                return
            
            print(f"✅ Found tenant: {tenant.name}")
            
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'name': f'Test Customer {phone_number[-4:]}',
                    'tenant': tenant,
                    'gender': 'N/A',
                    'marital_status': 'N/A'
                }
            )
            
            if created:
                print(f"✅ Created test customer: {customer.name}")
            else:
                print(f"✅ Found existing customer: {customer.name}")
            
            # Check for active contests
            now = timezone.now()
            active_contests = Contest.objects.filter(
                tenant=tenant,
                is_active=True,
                starts_at__lte=now,
                ends_at__gte=now
            )
            
            print(f"📋 Active contests: {active_contests.count()}")
            
            if active_contests.count() == 0:
                print("⚠️  No active contests found. Creating a test contest...")
                
                # Create a test contest
                test_contest = Contest.objects.create(
                    tenant=tenant,
                    name="Test Auto Contest",
                    description="Test contest for automatic entry",
                    starts_at=now - timedelta(hours=1),
                    ends_at=now + timedelta(hours=23),
                    is_active=True,
                    requires_nric=False,
                    requires_receipt=False,
                    contest_instructions="Send any message to participate!",
                    eligibility_message="You are automatically entered into this contest!"
                )
                
                print(f"✅ Created test contest: {test_contest.name}")
                active_contests = [test_contest]
            
            # Test auto contest service
            auto_contest_service = AutoContestService()
            
            print(f"\n🔄 Processing message: '{message_text}'")
            print(f"📱 From: {customer.name} ({customer.phone_number})")
            
            # Process message for contests
            results = auto_contest_service.process_message_for_contests(
                customer, message_text, tenant
            )
            
            print(f"\n📊 Results:")
            print(f"   Contests checked: {results['contests_checked']}")
            print(f"   Contests added: {results['contests_added']}")
            print(f"   Contests updated: {results['contests_updated']}")
            
            if results['errors']:
                print(f"   Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"     - {error}")
            
            # Show contest entries
            print(f"\n📋 Contest Entries:")
            entries = ContestEntry.objects.filter(
                tenant=tenant,
                customer=customer
            ).order_by('-submitted_at')
            
            for entry in entries:
                print(f"   - {entry.contest.name}: {entry.status} ({entry.submitted_at})")
            
            # Show contest stats
            print(f"\n📈 Contest Statistics:")
            stats = auto_contest_service.get_contest_stats(tenant)
            print(f"   Active contests: {stats['active_contests']}")
            print(f"   Total entries: {stats['total_entries']}")
            print(f"   Status breakdown: {stats['status_breakdown']}")
            
            if results['contests_added'] > 0 or results['contests_updated'] > 0:
                self.stdout.write(self.style.SUCCESS("✅ Auto contest processing successful!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  No contest entries were created/updated"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            import traceback
            traceback.print_exc()
