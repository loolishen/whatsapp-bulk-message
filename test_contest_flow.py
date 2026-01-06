#!/usr/bin/env python3
"""
Complete Contest Flow Test Script
Tests: Contest Creation → WhatsApp Webhook → Auto Reply → OCR → Data Storage
Run this in Cloud Shell: python3 test_contest_flow.py
"""

import os
import sys
import django
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer, Tenant

# Configuration
APP_URL = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE = "+60123456789"
TEST_NAME = "Test User"
TEST_EMAIL = "test@example.com"

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def print_error(msg):
    print(f"{RED}❌ {msg}{NC}")

def print_info(msg):
    print(f"{YELLOW}ℹ️  {msg}{NC}")

def print_step(msg):
    print(f"\n{BLUE}📋 {msg}{NC}")
    print("-" * 40)

# =============================================================================
# STEP 1: Create Test Contest
# =============================================================================
print_step("STEP 1: Create Test Contest")

try:
    tenant = Tenant.objects.first()
    if not tenant:
        print_error("No tenant found. Please create a tenant first.")
        sys.exit(1)
    
    # Check if test contest already exists
    existing = Contest.objects.filter(name__icontains="Test Contest - Full Flow").first()
    if existing:
        print_info(f"Using existing contest: {existing.name}")
        contest = existing
    else:
        contest = Contest.objects.create(
            tenant=tenant,
            name="🧪 Test Contest - Full Flow",
            description="Automated test contest for full flow testing",
            starts_at=datetime.now() - timedelta(days=1),
            ends_at=datetime.now() + timedelta(days=30),
            is_active=True,
            keywords="TEST,JOIN,START",
            auto_reply_message="Welcome to the test contest! Please reply with 'AGREE' to continue.",
            introduction_message="Hello! Welcome to our test contest. This is an automated test.",
            pdpa_message="Do you agree to our PDPA terms? Reply 'AGREE' to continue.",
            participant_agreement="Thank you for agreeing! Please send your NRIC number.",
            requires_nric=True,
            requires_receipt=True,
            min_purchase_amount=10.00
        )
        print_success(f"Contest created: {contest.name}")
    
    print_info(f"Contest ID: {contest.contest_id}")
    print_info(f"Keywords: {contest.keywords}")
    
except Exception as e:
    print_error(f"Failed to create contest: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# STEP 2: Test WhatsApp Webhook - Initial Message
# =============================================================================
print_step("STEP 2: Test WhatsApp Webhook - Initial Message (Keyword: TEST)")

webhook_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": TEST_PHONE,
                    "type": "text",
                    "text": {
                        "body": "TEST"
                    },
                    "id": f"test_msg_{int(time.time())}",
                    "timestamp": str(int(time.time()))
                }],
                "contacts": [{
                    "profile": {
                        "name": TEST_NAME
                    },
                    "wa_id": TEST_PHONE
                }]
            }
        }]
    }]
}

try:
    response = requests.post(
        f"{APP_URL}/webhook/whatsapp/",
        json=webhook_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code in [200, 201]:
        print_success("Webhook received initial message")
    else:
        print_error(f"Webhook returned status {response.status_code}")
        print_info(f"Response: {response.text[:200]}")
except Exception as e:
    print_error(f"Webhook request failed: {e}")

time.sleep(2)

# =============================================================================
# STEP 3: Test PDPA Agreement
# =============================================================================
print_step("STEP 3: Test PDPA Agreement (Reply: AGREE)")

webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "AGREE"
webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"] = f"test_msg_{int(time.time())}"

try:
    response = requests.post(
        f"{APP_URL}/webhook/whatsapp/",
        json=webhook_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code in [200, 201]:
        print_success("PDPA agreement processed")
    else:
        print_error(f"Webhook returned status {response.status_code}")
except Exception as e:
    print_error(f"Webhook request failed: {e}")

time.sleep(2)

# =============================================================================
# STEP 4: Test NRIC Submission
# =============================================================================
print_step("STEP 4: Test NRIC Submission")

webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "123456789012"
webhook_payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"] = f"test_msg_{int(time.time())}"

try:
    response = requests.post(
        f"{APP_URL}/webhook/whatsapp/",
        json=webhook_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code in [200, 201]:
        print_success("NRIC submission processed")
    else:
        print_error(f"Webhook returned status {response.status_code}")
except Exception as e:
    print_error(f"Webhook request failed: {e}")

time.sleep(2)

# =============================================================================
# STEP 5: Test Receipt Image (OCR)
# =============================================================================
print_step("STEP 5: Test Receipt Image Upload (OCR)")

# Create image webhook payload
image_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": TEST_PHONE,
                    "type": "image",
                    "image": {
                        "id": f"test_image_{int(time.time())}",
                        "mime_type": "image/png",
                        "caption": "Test receipt"
                    },
                    "id": f"test_msg_{int(time.time())}",
                    "timestamp": str(int(time.time()))
                }],
                "contacts": [{
                    "profile": {
                        "name": TEST_NAME
                    },
                    "wa_id": TEST_PHONE
                }]
            }
        }]
    }]
}

try:
    response = requests.post(
        f"{APP_URL}/webhook/whatsapp/",
        json=image_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    if response.status_code in [200, 201]:
        print_success("Receipt image received (OCR will process in background)")
    else:
        print_error(f"Webhook returned status {response.status_code}")
except Exception as e:
    print_error(f"Webhook request failed: {e}")

print_info("Waiting 5 seconds for OCR processing...")
time.sleep(5)

# =============================================================================
# STEP 6: Verify Data in Database
# =============================================================================
print_step("STEP 6: Verify Data Saved in Database")

try:
    # Find entries for this contest
    entries = ContestEntry.objects.filter(contest=contest)
    entry_count = entries.count()
    
    print_info(f"Found {entry_count} contest entry/entries")
    
    if entry_count > 0:
        entry = entries.first()
        print_success(f"Entry ID: {entry.entry_id}")
        print_info(f"Status: {entry.status}")
        print_info(f"NRIC: {getattr(entry, 'contestant_nric', 'N/A')}")
        print_info(f"Verified: {entry.is_verified}")
        print_info(f"Receipt URL: {getattr(entry, 'receipt_image_url', 'N/A')}")
        print_info(f"Store Name: {getattr(entry, 'store_name', 'N/A')}")
        print_info(f"Store Location: {getattr(entry, 'store_location', 'N/A')}")
        print_info(f"Products: {getattr(entry, 'products_purchased', [])}")
        print_info(f"Receipt Amount: {getattr(entry, 'receipt_amount', 'N/A')}")
    else:
        print_info("No entries found yet (may need to wait for processing)")
    
    # Find customer
    customer = Customer.objects.filter(phone_number__icontains="123456789").first()
    if customer:
        print_success(f"Customer found: {customer.name} ({customer.phone_number})")
    else:
        print_info("Customer not found yet")
        
except Exception as e:
    print_error(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# STEP 7: Test Contest Manager Page
# =============================================================================
print_step("STEP 7: Test Contest Manager Page")

try:
    response = requests.get(
        f"{APP_URL}/contest/manager/",
        timeout=10,
        allow_redirects=False
    )
    if response.status_code in [200, 302]:
        print_success(f"Contest Manager page accessible (HTTP {response.status_code})")
    else:
        print_error(f"Contest Manager page returned HTTP {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# =============================================================================
# STEP 8: Test Participants Manager Page
# =============================================================================
print_step("STEP 8: Test Participants Manager Page")

try:
    response = requests.get(
        f"{APP_URL}/participants/",
        timeout=10,
        allow_redirects=False
    )
    if response.status_code in [200, 302]:
        print_success(f"Participants Manager page accessible (HTTP {response.status_code})")
    else:
        print_error(f"Participants Manager page returned HTTP {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 40)
print("📊 TEST SUMMARY")
print("=" * 40)
print(f"\nTest Contest ID: {contest.contest_id}")
print(f"Test Phone: {TEST_PHONE}")
print(f"\n✅ Tests Completed:")
print("   1. Contest Creation")
print("   2. WhatsApp Webhook (Initial Message)")
print("   3. PDPA Agreement Flow")
print("   4. NRIC Submission")
print("   5. Receipt Image Upload (OCR)")
print("   6. Database Verification")
print("   7. Contest Manager Page")
print("   8. Participants Manager Page")
print(f"\n📝 Next Steps:")
print(f"   1. Check App Engine logs: gcloud app logs read --limit=50")
print(f"   2. Visit Contest Manager: {APP_URL}/contest/manager/")
print(f"   3. Visit Participants Manager: {APP_URL}/participants/")
print(f"   4. Check database entries using Django shell")
print("")
print_success("Test script completed!")

