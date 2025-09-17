#!/usr/bin/env python
"""
Simple test script for auto contest functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Tenant, Customer, Contest
from messaging.auto_contest_service import AutoContestService
from django.utils import timezone
from datetime import timedelta

def test_auto_contest():
    print("🧪 Testing Auto Contest Functionality")
    print("=" * 50)
    
    try:
        # Get tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("❌ No tenant found. Please run: python setup_pro_user.py")
            return
        
        print(f"✅ Found tenant: {tenant.name}")
        
        # Create a test contest if none exists
        now = timezone.now()
        active_contests = Contest.objects.filter(
            tenant=tenant,
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        )
        
        if active_contests.count() == 0:
            print("⚠️  No active contests found. Creating a test contest...")
            
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
        else:
            print(f"✅ Found {active_contests.count()} active contest(s)")
        
        # Test with a customer
        phone_number = "60123456789"
        message_text = "Hello, I want to join the contest!"
        
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
        from messaging.models import ContestEntry
        print(f"\n📋 Contest Entries:")
        entries = ContestEntry.objects.filter(
            tenant=tenant,
            customer=customer
        ).order_by('-submitted_at')
        
        for entry in entries:
            print(f"   - {entry.contest.name}: {entry.status} ({entry.submitted_at})")
        
        if results['contests_added'] > 0 or results['contests_updated'] > 0:
            print("\n✅ Auto contest processing successful!")
        else:
            print("\n⚠️  No contest entries were created/updated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_auto_contest()
