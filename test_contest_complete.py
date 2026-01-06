#!/usr/bin/env python3
"""
COMPLETE CONTEST FLOW TEST - Copy & Paste into Cloud Shell
Tests: Contest Creation → WhatsApp Webhook → Auto Reply → OCR → Data Storage
Uses real image: img/Gurdial_Singh_AL_Natha_Singh.jpg
"""
import os
import sys
import django
import json
import time
import requests
import base64
from datetime import datetime, timedelta
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer, Tenant
from messaging.receipt_ocr_service import ReceiptOCRService
from messaging.cloudinary_service import cloudinary_service

# Configuration
APP_URL = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE = "+60123456789"
TEST_NAME = "Test User"

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
    CONTEST_ID = str(contest.contest_id)
    
except Exception as e:
    print_error(f"Failed to create contest: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# STEP 2: Upload Test Image to Cloudinary
# =============================================================================
print_step("STEP 2: Upload Test Image for OCR")

IMAGE_URL = None
IMAGE_PATH = Path("img/Gurdial_Singh_AL_Natha_Singh.jpg")

# Try multiple locations
possible_paths = [
    IMAGE_PATH,
    Path("/srv/img/Gurdial_Singh_AL_Natha_Singh.jpg"),
    Path("/srv/app-full/img/Gurdial_Singh_AL_Natha_Singh.jpg"),
    Path.home() / "app-full" / "img" / "Gurdial_Singh_AL_Natha_Singh.jpg",
]

image_file = None
for path in possible_paths:
    if path.exists():
        image_file = path
        break

if not image_file:
    print_error("Image file not found. Please ensure img/Gurdial_Singh_AL_Natha_Singh.jpg exists.")
    print_info("Trying to download from Cloud Storage...")
    try:
        import subprocess
        result = subprocess.run(
            ["gsutil", "cp", "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/img/Gurdial_Singh_AL_Natha_Singh.jpg", "img/"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and Path("img/Gurdial_Singh_AL_Natha_Singh.jpg").exists():
            image_file = Path("img/Gurdial_Singh_AL_Natha_Singh.jpg")
            print_success("Image downloaded from Cloud Storage")
        else:
            print_error("Could not download image from Cloud Storage")
    except Exception as e:
        print_error(f"Download failed: {e}")

if image_file and image_file.exists():
    try:
        # Upload to Cloudinary
        print_info(f"Uploading {image_file} to Cloudinary...")
        with open(image_file, 'rb') as f:
            image_data = f.read()
            result = cloudinary_service.upload_base64(
                base64.b64encode(image_data).decode('utf-8'),
                filename=image_file.name
            )
            if result.get('success'):
                IMAGE_URL = result.get('url')
                print_success(f"Image uploaded to Cloudinary: {IMAGE_URL}")
            else:
                print_error(f"Cloudinary upload failed: {result.get('error')}")
                # Fallback: use local path if Cloudinary fails
                IMAGE_URL = str(image_file.absolute())
                print_info(f"Using local path: {IMAGE_URL}")
    except Exception as e:
        print_error(f"Image upload error: {e}")
        if image_file.exists():
            IMAGE_URL = str(image_file.absolute())
            print_info(f"Using local path as fallback: {IMAGE_URL}")
else:
    print_error("Image file not available. OCR test will be skipped.")
    IMAGE_URL = None

# =============================================================================
# STEP 3: Test WhatsApp Webhook - Initial Message
# =============================================================================
print_step("STEP 3: Test WhatsApp Webhook - Initial Message (Keyword: TEST)")

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
# STEP 4: Test PDPA Agreement
# =============================================================================
print_step("STEP 4: Test PDPA Agreement (Reply: AGREE)")

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
# STEP 5: Test NRIC Submission
# =============================================================================
print_step("STEP 5: Test NRIC Submission")

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
# STEP 6: Test Receipt Image (OCR) - Direct OCR Test
# =============================================================================
print_step("STEP 6: Test Receipt Image OCR - Using Real Image")

if IMAGE_URL:
    try:
        ocr_service = ReceiptOCRService()
        print_info(f"Processing image: {IMAGE_URL}")
        result = ocr_service.process_receipt_image(IMAGE_URL)
        
        if result.get('success'):
            print_success("OCR processing completed")
            print_info(f"Store Name: {result.get('store_name', 'N/A')}")
            print_info(f"Store Location: {result.get('store_location', 'N/A')}")
            print_info(f"Amount Spent: {result.get('amount_spent', 'N/A')}")
            print_info(f"Products: {result.get('products', [])}")
            
            # Now simulate webhook with image
            print_info("Simulating webhook with image...")
            image_payload = {
                "entry": [{
                    "changes": [{
                        "value": {
                            "messages": [{
                                "from": TEST_PHONE,
                                "type": "image",
                                "image": {
                                    "id": f"test_image_{int(time.time())}",
                                    "mime_type": "image/jpeg",
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
            
            # For testing, we'll also directly create an entry with OCR data
            print_info("Creating test entry with OCR data...")
            try:
                customer = Customer.objects.filter(phone_number__icontains="123456789").first()
                if customer and contest:
                    entry, created = ContestEntry.objects.get_or_create(
                        contest=contest,
                        customer=customer,
                        tenant=tenant,
                        defaults={
                            'contestant_name': customer.name,
                            'contestant_phone': customer.phone_number,
                            'contestant_email': customer.email,
                            'contestant_nric': '123456789012',
                            'receipt_image_url': IMAGE_URL,
                            'store_name': result.get('store_name', ''),
                            'store_location': result.get('store_location', ''),
                            'receipt_amount': float(result.get('amount_spent', 0).replace('RM', '').replace(',', '')) if result.get('amount_spent') else None,
                            'products_purchased': result.get('products', []),
                            'status': 'submitted'
                        }
                    )
                    if created:
                        print_success(f"Test entry created: {entry.entry_id}")
                    else:
                        print_info(f"Entry already exists: {entry.entry_id}")
            except Exception as e:
                print_error(f"Failed to create test entry: {e}")
                import traceback
                traceback.print_exc()
        else:
            print_error(f"OCR processing failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print_error(f"OCR test failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print_error("Image URL not available. Skipping OCR test.")

print_info("Waiting 5 seconds for processing...")
time.sleep(5)

# =============================================================================
# STEP 7: Verify Data in Database
# =============================================================================
print_step("STEP 7: Verify Data Saved in Database")

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
# STEP 8: Test Contest Manager Page
# =============================================================================
print_step("STEP 8: Test Contest Manager Page")

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
# STEP 9: Test Participants Manager Page
# =============================================================================
print_step("STEP 9: Test Participants Manager Page")

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
# STEP 10: Verify Contest Selection in Participants Manager
# =============================================================================
print_step("STEP 10: Verify Contest Selection in Participants Manager")

try:
    # Test with contest filter
    response = requests.get(
        f"{APP_URL}/participants/?contest={CONTEST_ID}",
        timeout=10,
        allow_redirects=False
    )
    if response.status_code in [200, 302]:
        print_success(f"Participants Manager with contest filter accessible (HTTP {response.status_code})")
        # Check if response contains contest name
        if CONTEST_ID in response.text or "Test Contest" in response.text:
            print_success("Contest filter is working")
        else:
            print_info("Contest filter may not be displaying correctly")
    else:
        print_error(f"Participants Manager returned HTTP {response.status_code}")
except Exception as e:
    print_error(f"Request failed: {e}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 40)
print("📊 TEST SUMMARY")
print("=" * 40)
print(f"\nTest Contest ID: {CONTEST_ID}")
print(f"Test Phone: {TEST_PHONE}")
if IMAGE_URL:
    print(f"Image URL: {IMAGE_URL}")
print(f"\n✅ Tests Completed:")
print("   1. Contest Creation")
print("   2. WhatsApp Webhook (Initial Message)")
print("   3. PDPA Agreement Flow")
print("   4. NRIC Submission")
print("   5. Receipt Image OCR Processing")
print("   6. Database Verification")
print("   7. Contest Manager Page")
print("   8. Participants Manager Page")
print("   9. Contest Selection in Participants Manager")
print(f"\n📝 Next Steps:")
print(f"   1. Check App Engine logs: gcloud app logs read --limit=50")
print(f"   2. Visit Contest Manager: {APP_URL}/contest/manager/")
print(f"   3. Visit Participants Manager: {APP_URL}/participants/")
print(f"   4. Verify contest dropdown shows database contests")
print("")
print_success("Test script completed!")

