#!/bin/bash
# =============================================================================
# CHECK CONTEST STATUS AND WEBHOOK DIAGNOSTICS
# Run this in Cloud Shell to verify why "TEST" isn't working
# =============================================================================

cd ~/app-full && python3 << 'PYTHON_SCRIPT'
import os, sys, django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, Tenant

GREEN, RED, YELLOW, BLUE, NC = '\033[0;32m', '\033[0;31m', '\033[1;33m', '\033[0;34m', '\033[0m'
def ps(msg): print(f"{GREEN}✅ {msg}{NC}")
def pe(msg): print(f"{RED}❌ {msg}{NC}")
def pi(msg): print(f"{YELLOW}ℹ️  {msg}{NC}")
def pstep(msg): print(f"\n{BLUE}📋 {msg}{NC}\n" + "-" * 40)

pstep("CHECKING CONTEST STATUS")
tenant = Tenant.objects.first()
if not tenant:
    pe("No tenant found")
    sys.exit(1)

now = timezone.now()
pi(f"Current time: {now}")

# Check all contests
all_contests = Contest.objects.filter(tenant=tenant).order_by('-created_at')
pi(f"\nTotal contests in database: {all_contests.count()}")

for contest in all_contests:
    print(f"\n{'='*60}")
    print(f"Contest: {contest.name}")
    print(f"  ID: {contest.contest_id}")
    print(f"  Keywords: {contest.keywords or 'NONE SET'}")
    print(f"  is_active: {contest.is_active}")
    print(f"  starts_at: {contest.starts_at}")
    print(f"  ends_at: {contest.ends_at}")
    
    # Check if it's currently active
    is_currently_active = (
        contest.is_active and 
        contest.starts_at <= now and 
        contest.ends_at >= now
    )
    
    if is_currently_active:
        ps(f"  ✅ ACTIVE - Will respond to keywords: {contest.keywords}")
    else:
        pe(f"  ❌ NOT ACTIVE")
        if not contest.is_active:
            print(f"     Reason: is_active = False")
        if contest.starts_at > now:
            print(f"     Reason: Starts in the future ({contest.starts_at})")
        if contest.ends_at < now:
            print(f"     Reason: Already ended ({contest.ends_at})")

# Check for contests that should respond to "TEST"
pstep("CHECKING FOR CONTESTS THAT MATCH 'TEST'")
test_contests = [c for c in all_contests if c.keywords and 'test' in c.keywords.lower()]
if test_contests:
    pi(f"Found {len(test_contests)} contest(s) with 'TEST' keyword:")
    for c in test_contests:
        is_active = c.is_active and c.starts_at <= now and c.ends_at >= now
        status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
        print(f"  - {c.name}: {status}")
        print(f"    Keywords: {c.keywords}")
else:
    pe("No contests found with 'TEST' keyword!")

# Suggest creating a fresh contest
pstep("RECOMMENDATION")
if not any(c.is_active and c.starts_at <= now and c.ends_at >= now for c in all_contests):
    pe("No active contests found!")
    pi("You need to create a fresh contest or activate an existing one.")
    print("\nTo create a fresh active contest, run:")
    print("  python3 -c \"")
    print("  import os, django")
    print("  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')")
    print("  django.setup()")
    print("  from messaging.models import Contest, Tenant")
    print("  from django.utils import timezone")
    print("  from datetime import timedelta")
    print("  tenant = Tenant.objects.first()")
    print("  contest = Contest.objects.create(")
    print("    tenant=tenant, name='Live Test Contest',")
    print("    description='Test contest for WhatsApp',")
    print("    starts_at=timezone.now()-timedelta(days=1),")
    print("    ends_at=timezone.now()+timedelta(days=30),")
    print("    is_active=True, keywords='TEST,JOIN,START',")
    print("    introduction_message='Hi! Welcome to our contest!',")
    print("    pdpa_message='Do you agree to our PDPA terms? Reply AGREE.',")
    print("    participant_agreement='Thank you! Please send your NRIC.',")
    print("    requires_nric=True, requires_receipt=True, min_purchase_amount=10.00")
    print("  )")
    print("  print(f'Created contest: {contest.name} with keywords: {contest.keywords}')")
    print("  \"")
else:
    ps("You have active contests! The issue might be:")
    pi("  1. Webhook not configured properly")
    pi("  2. WhatsApp number not connected")
    pi("  3. Message format issue")
    print("\nCheck webhook logs:")
    print("  gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i 'webhook\\|contest\\|test'")

PYTHON_SCRIPT




# =============================================================================
# CHECK CONTEST STATUS AND WEBHOOK DIAGNOSTICS
# Run this in Cloud Shell to verify why "TEST" isn't working
# =============================================================================

cd ~/app-full && python3 << 'PYTHON_SCRIPT'
import os, sys, django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, Tenant

GREEN, RED, YELLOW, BLUE, NC = '\033[0;32m', '\033[0;31m', '\033[1;33m', '\033[0;34m', '\033[0m'
def ps(msg): print(f"{GREEN}✅ {msg}{NC}")
def pe(msg): print(f"{RED}❌ {msg}{NC}")
def pi(msg): print(f"{YELLOW}ℹ️  {msg}{NC}")
def pstep(msg): print(f"\n{BLUE}📋 {msg}{NC}\n" + "-" * 40)

pstep("CHECKING CONTEST STATUS")
tenant = Tenant.objects.first()
if not tenant:
    pe("No tenant found")
    sys.exit(1)

now = timezone.now()
pi(f"Current time: {now}")

# Check all contests
all_contests = Contest.objects.filter(tenant=tenant).order_by('-created_at')
pi(f"\nTotal contests in database: {all_contests.count()}")

for contest in all_contests:
    print(f"\n{'='*60}")
    print(f"Contest: {contest.name}")
    print(f"  ID: {contest.contest_id}")
    print(f"  Keywords: {contest.keywords or 'NONE SET'}")
    print(f"  is_active: {contest.is_active}")
    print(f"  starts_at: {contest.starts_at}")
    print(f"  ends_at: {contest.ends_at}")
    
    # Check if it's currently active
    is_currently_active = (
        contest.is_active and 
        contest.starts_at <= now and 
        contest.ends_at >= now
    )
    
    if is_currently_active:
        ps(f"  ✅ ACTIVE - Will respond to keywords: {contest.keywords}")
    else:
        pe(f"  ❌ NOT ACTIVE")
        if not contest.is_active:
            print(f"     Reason: is_active = False")
        if contest.starts_at > now:
            print(f"     Reason: Starts in the future ({contest.starts_at})")
        if contest.ends_at < now:
            print(f"     Reason: Already ended ({contest.ends_at})")

# Check for contests that should respond to "TEST"
pstep("CHECKING FOR CONTESTS THAT MATCH 'TEST'")
test_contests = [c for c in all_contests if c.keywords and 'test' in c.keywords.lower()]
if test_contests:
    pi(f"Found {len(test_contests)} contest(s) with 'TEST' keyword:")
    for c in test_contests:
        is_active = c.is_active and c.starts_at <= now and c.ends_at >= now
        status = "✅ ACTIVE" if is_active else "❌ INACTIVE"
        print(f"  - {c.name}: {status}")
        print(f"    Keywords: {c.keywords}")
else:
    pe("No contests found with 'TEST' keyword!")

# Suggest creating a fresh contest
pstep("RECOMMENDATION")
if not any(c.is_active and c.starts_at <= now and c.ends_at >= now for c in all_contests):
    pe("No active contests found!")
    pi("You need to create a fresh contest or activate an existing one.")
    print("\nTo create a fresh active contest, run:")
    print("  python3 -c \"")
    print("  import os, django")
    print("  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')")
    print("  django.setup()")
    print("  from messaging.models import Contest, Tenant")
    print("  from django.utils import timezone")
    print("  from datetime import timedelta")
    print("  tenant = Tenant.objects.first()")
    print("  contest = Contest.objects.create(")
    print("    tenant=tenant, name='Live Test Contest',")
    print("    description='Test contest for WhatsApp',")
    print("    starts_at=timezone.now()-timedelta(days=1),")
    print("    ends_at=timezone.now()+timedelta(days=30),")
    print("    is_active=True, keywords='TEST,JOIN,START',")
    print("    introduction_message='Hi! Welcome to our contest!',")
    print("    pdpa_message='Do you agree to our PDPA terms? Reply AGREE.',")
    print("    participant_agreement='Thank you! Please send your NRIC.',")
    print("    requires_nric=True, requires_receipt=True, min_purchase_amount=10.00")
    print("  )")
    print("  print(f'Created contest: {contest.name} with keywords: {contest.keywords}')")
    print("  \"")
else:
    ps("You have active contests! The issue might be:")
    pi("  1. Webhook not configured properly")
    pi("  2. WhatsApp number not connected")
    pi("  3. Message format issue")
    print("\nCheck webhook logs:")
    print("  gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i 'webhook\\|contest\\|test'")

PYTHON_SCRIPT






