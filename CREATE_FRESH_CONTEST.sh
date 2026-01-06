#!/bin/bash
# =============================================================================
# CREATE FRESH ACTIVE CONTEST FOR WHATSAPP TESTING
# Run this in Cloud Shell to create a contest that will respond to "TEST"
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

pstep("CREATING FRESH ACTIVE CONTEST")
try:
    tenant = Tenant.objects.first()
    if not tenant:
        pe("No tenant found")
        sys.exit(1)
    
    # Delete old test contests (optional - comment out if you want to keep them)
    # old_tests = Contest.objects.filter(tenant=tenant, name__icontains="Test Contest")
    # if old_tests.exists():
    #     pi(f"Found {old_tests.count()} old test contests (keeping them)")
    
    # Create fresh contest
    now = timezone.now()
    contest = Contest.objects.create(
        tenant=tenant,
        name="🎯 Live WhatsApp Test Contest",
        description="Active contest for WhatsApp testing - responds to TEST, JOIN, START",
        starts_at=now - timedelta(days=1),  # Started yesterday
        ends_at=now + timedelta(days=30),   # Ends in 30 days
        is_active=True,
        keywords="TEST,JOIN,START",
        auto_reply_message="Welcome! Reply 'AGREE' to continue.",
        introduction_message="Hi! Welcome to Khind Merdeka Contest!",
        pdpa_message="Before we continue, we need your consent to collect and process your personal data.\n\nDo you agree to participate and allow us to process your information?\n\nReply 'I agree' to continue or 'No' to opt out.",
        participant_agreement="Wonderful! Welcome to the contest!",
        requires_nric=True,
        requires_receipt=True,
        min_purchase_amount=10.00
    )
    
    ps(f"✅ Contest created successfully!")
    print(f"\nContest Details:")
    print(f"  Name: {contest.name}")
    print(f"  ID: {contest.contest_id}")
    print(f"  Keywords: {contest.keywords}")
    print(f"  Active: {contest.is_active}")
    print(f"  Start: {contest.starts_at}")
    print(f"  End: {contest.ends_at}")
    print(f"  Currently Active: {contest.is_active and contest.starts_at <= now and contest.ends_at >= now}")
    
    print(f"\n📱 To test on WhatsApp:")
    print(f"  1. Text: TEST (or JOIN or START)")
    print(f"  2. Bot will reply with introduction and PDPA message")
    print(f"  3. Reply: AGREE")
    print(f"  4. Follow the prompts")
    
except Exception as e:
    pe(f"Failed to create contest: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

PYTHON_SCRIPT




# =============================================================================
# CREATE FRESH ACTIVE CONTEST FOR WHATSAPP TESTING
# Run this in Cloud Shell to create a contest that will respond to "TEST"
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

pstep("CREATING FRESH ACTIVE CONTEST")
try:
    tenant = Tenant.objects.first()
    if not tenant:
        pe("No tenant found")
        sys.exit(1)
    
    # Delete old test contests (optional - comment out if you want to keep them)
    # old_tests = Contest.objects.filter(tenant=tenant, name__icontains="Test Contest")
    # if old_tests.exists():
    #     pi(f"Found {old_tests.count()} old test contests (keeping them)")
    
    # Create fresh contest
    now = timezone.now()
    contest = Contest.objects.create(
        tenant=tenant,
        name="🎯 Live WhatsApp Test Contest",
        description="Active contest for WhatsApp testing - responds to TEST, JOIN, START",
        starts_at=now - timedelta(days=1),  # Started yesterday
        ends_at=now + timedelta(days=30),   # Ends in 30 days
        is_active=True,
        keywords="TEST,JOIN,START",
        auto_reply_message="Welcome! Reply 'AGREE' to continue.",
        introduction_message="Hi! Welcome to Khind Merdeka Contest!",
        pdpa_message="Before we continue, we need your consent to collect and process your personal data.\n\nDo you agree to participate and allow us to process your information?\n\nReply 'I agree' to continue or 'No' to opt out.",
        participant_agreement="Wonderful! Welcome to the contest!",
        requires_nric=True,
        requires_receipt=True,
        min_purchase_amount=10.00
    )
    
    ps(f"✅ Contest created successfully!")
    print(f"\nContest Details:")
    print(f"  Name: {contest.name}")
    print(f"  ID: {contest.contest_id}")
    print(f"  Keywords: {contest.keywords}")
    print(f"  Active: {contest.is_active}")
    print(f"  Start: {contest.starts_at}")
    print(f"  End: {contest.ends_at}")
    print(f"  Currently Active: {contest.is_active and contest.starts_at <= now and contest.ends_at >= now}")
    
    print(f"\n📱 To test on WhatsApp:")
    print(f"  1. Text: TEST (or JOIN or START)")
    print(f"  2. Bot will reply with introduction and PDPA message")
    print(f"  3. Reply: AGREE")
    print(f"  4. Follow the prompts")
    
except Exception as e:
    pe(f"Failed to create contest: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

PYTHON_SCRIPT






