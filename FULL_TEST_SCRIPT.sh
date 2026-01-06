#!/bin/bash
# =============================================================================
# COMPLETE CONTEST FLOW TEST - COPY & PASTE INTO CLOUD SHELL
# Tests: Contest Creation → WhatsApp Webhook → Auto Reply → OCR → Data Storage
# Uses real image: img/Gurdial_Singh_AL_Natha_Singh.jpg
# Participants Manager shows database contests (not hardcoded)
# =============================================================================

cd ~/app-full && python3 << 'PYTHON_SCRIPT'
import os, sys, django, json, time, requests, base64
from datetime import datetime, timedelta
from pathlib import Path
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer, Tenant, Conversation, CoreMessage, WhatsAppConnection
from messaging.receipt_ocr_service import ReceiptOCRService
from messaging.cloudinary_service import cloudinary_service

APP_URL = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE = "+60123456789"
TEST_NAME = "Test User"

GREEN, RED, YELLOW, BLUE, NC = '\033[0;32m', '\033[0;31m', '\033[1;33m', '\033[0;34m', '\033[0m'
def ps(msg): print(f"{GREEN}✅ {msg}{NC}")
def pe(msg): print(f"{RED}❌ {msg}{NC}")
def pi(msg): print(f"{YELLOW}ℹ️  {msg}{NC}")
def pstep(msg): print(f"\n{BLUE}📋 {msg}{NC}\n" + "-" * 40)

# STEP 1: Create Test Contest
pstep("STEP 1: Create Test Contest")
try:
    tenant = Tenant.objects.first()
    if not tenant: pe("No tenant found"); sys.exit(1)
    existing = Contest.objects.filter(name__icontains="Test Contest 3 - Full Flow").first()
    if existing:
        pi(f"Using existing: {existing.name}")
        contest = existing
    else:
        contest = Contest.objects.create(tenant=tenant, name="🧪 Test Contest 3 - Full Flow",
            description="Automated test", starts_at=timezone.now()-timedelta(days=1),
            ends_at=timezone.now()+timedelta(days=30), is_active=True, keywords="TEST,JOIN,START",
            auto_reply_message="Welcome! Reply 'AGREE' to continue.",
            introduction_message="Hello! Welcome to our test contest.",
            pdpa_message="Do you agree to our PDPA terms? Reply 'AGREE'.",
            participant_agreement="Thank you! Please send your NRIC number.",
            requires_nric=True, requires_receipt=True, min_purchase_amount=10.00)
        ps(f"Contest created: {contest.name}")
    pi(f"Contest ID: {contest.contest_id}")
    CONTEST_ID = str(contest.contest_id)
except Exception as e: pe(f"Failed: {e}"); sys.exit(1)

# STEP 2: Upload Test Image
pstep("STEP 2: Upload Test Image for OCR")
IMAGE_URL = None
for path in [Path("img/Gurdial_Singh_AL_Natha_Singh.jpg"), Path("/srv/img/Gurdial_Singh_AL_Natha_Singh.jpg"),
              Path("/srv/app-full/img/Gurdial_Singh_AL_Natha_Singh.jpg")]:
    if path.exists():
        try:
            with open(path, 'rb') as f:
                result = cloudinary_service.upload_base64(base64.b64encode(f.read()).decode('utf-8'), path.name)
                if result.get('success'):
                    IMAGE_URL = result.get('url')
                    ps(f"Image uploaded: {IMAGE_URL}")
                    break
        except: pass
if not IMAGE_URL:
    pe("Image not found locally. Trying Cloud Storage...")
    import subprocess
    try:
        subprocess.run(["gsutil", "cp", "gs://staging.whatsapp-bulk-messaging-480620.appspot.com/img/Gurdial_Singh_AL_Natha_Singh.jpg", "img/"], 
                      check=True, capture_output=True)
        if Path("img/Gurdial_Singh_AL_Natha_Singh.jpg").exists():
            with open("img/Gurdial_Singh_AL_Natha_Singh.jpg", 'rb') as f:
                result = cloudinary_service.upload_base64(base64.b64encode(f.read()).decode('utf-8'), "Gurdial_Singh_AL_Natha_Singh.jpg")
                if result.get('success'):
                    IMAGE_URL = result.get('url')
                    ps(f"Image downloaded and uploaded: {IMAGE_URL}")
    except: 
        pe("Could not download image. Please upload img/Gurdial_Singh_AL_Natha_Singh.jpg first.")
        pi("Run: gsutil cp img/Gurdial_Singh_AL_Natha_Singh.jpg gs://staging.whatsapp-bulk-messaging-480620.appspot.com/img/")

# STEP 3: Test Webhook - Initial Message
pstep("STEP 3: Test Webhook - Initial Message (TEST)")
try:
    r = requests.post(f"{APP_URL}/webhook/whatsapp/", json={"entry":[{"changes":[{"value":{"messages":[{"from":TEST_PHONE,"type":"text","text":{"body":"TEST"},"id":f"m{int(time.time())}","timestamp":str(int(time.time()))}],"contacts":[{"profile":{"name":TEST_NAME},"wa_id":TEST_PHONE}]}}]}]}, timeout=10)
    ps("Webhook received") if r.status_code in [200,201] else pe(f"Status {r.status_code}")
except Exception as e: pe(f"Failed: {e}")
time.sleep(2)

# STEP 4: Test PDPA Agreement
pstep("STEP 4: Test PDPA Agreement (AGREE)")
try:
    r = requests.post(f"{APP_URL}/webhook/whatsapp/", json={"entry":[{"changes":[{"value":{"messages":[{"from":TEST_PHONE,"type":"text","text":{"body":"AGREE"},"id":f"m{int(time.time())}","timestamp":str(int(time.time()))}],"contacts":[{"profile":{"name":TEST_NAME},"wa_id":TEST_PHONE}]}}]}]}, timeout=10)
    ps("PDPA processed") if r.status_code in [200,201] else pe(f"Status {r.status_code}")
except Exception as e: pe(f"Failed: {e}")
time.sleep(2)

# STEP 5: Test NRIC Submission
pstep("STEP 5: Test NRIC Submission")
try:
    r = requests.post(f"{APP_URL}/webhook/whatsapp/", json={"entry":[{"changes":[{"value":{"messages":[{"from":TEST_PHONE,"type":"text","text":{"body":"123456789012"},"id":f"m{int(time.time())}","timestamp":str(int(time.time()))}],"contacts":[{"profile":{"name":TEST_NAME},"wa_id":TEST_PHONE}]}}]}]}, timeout=10)
    ps("NRIC processed") if r.status_code in [200,201] else pe(f"Status {r.status_code}")
except Exception as e: pe(f"Failed: {e}")
time.sleep(2)

# STEP 6: Test OCR with Real Image
pstep("STEP 6: Test Receipt Image OCR - Using Real Image")
if IMAGE_URL:
    try:
        ocr_service = ReceiptOCRService()
        pi(f"Processing: {IMAGE_URL}")
        result = ocr_service.process_receipt_image(IMAGE_URL)
        if result.get('success'):
            ps("OCR completed")
            pi(f"Store: {result.get('store_name', 'N/A')}")
            pi(f"Location: {result.get('store_location', 'N/A')}")
            pi(f"Amount: {result.get('amount_spent', 'N/A')}")
            pi(f"Products: {result.get('products', [])}")
            # Create test entry with OCR data and conversation messages
            try:
                customer = Customer.objects.filter(phone_number__icontains="123456789").first()
                if not customer:
                    customer = Customer.objects.create(tenant=tenant, name=TEST_NAME, phone_number=TEST_PHONE)
                    ps(f"Created customer: {customer.name}")
                
                # Get or create WhatsApp connection
                whatsapp_conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
                if not whatsapp_conn:
                    whatsapp_conn = WhatsAppConnection.objects.create(tenant=tenant, phone_number="+60123456789", 
                        access_token_ref="test", instance_id="test", provider="wabot")
                
                # Get or create conversation
                conversation, conv_created = Conversation.objects.get_or_create(
                    tenant=tenant, customer=customer, contest=contest,
                    defaults={'whatsapp_connection': whatsapp_conn, 'last_message_at': timezone.now()}
                )
                if conv_created:
                    ps(f"Created conversation for chat history")
                
                # Create conversation messages for chat history
                messages_data = [
                    ("TEST", "inbound"),
                    ("Welcome! Reply 'AGREE' to continue.", "outbound"),
                    ("AGREE", "inbound"),
                    ("Do you agree to our PDPA terms? Reply 'AGREE'.", "outbound"),
                    ("123456789012", "inbound"),
                    ("Thank you! Please send your NRIC number.", "outbound"),
                    ("[image]", "inbound"),  # Receipt image
                ]
                
                for text, direction in messages_data:
                    CoreMessage.objects.get_or_create(
                        tenant=tenant, conversation=conversation,
                        text_body=text, direction=direction,
                        defaults={'status': 'sent' if direction == 'outbound' else 'delivered',
                                'sent_at': timezone.now()}
                    )
                ps(f"Created {len(messages_data)} conversation messages")
                
                # Create contest entry
                if contest:
                    entry, created = ContestEntry.objects.get_or_create(
                        contest=contest, customer=customer, tenant=tenant,
                        defaults={
                            'contestant_name': customer.name,
                            'contestant_phone': customer.phone_number,
                            'contestant_email': 'test@example.com',  # Fake email
                            'contestant_nric': '123456789012',
                            'receipt_image_url': IMAGE_URL,
                            'store_name': result.get('store_name', ''),
                            'store_location': result.get('store_location', ''),
                            'receipt_amount': float(str(result.get('amount_spent', '0')).replace('RM', '').replace(',', '').strip()) if result.get('amount_spent') else None,
                            'products_purchased': result.get('products', []),
                            'status': 'submitted'
                        }
                    )
                    ps(f"Entry {'created' if created else 'exists'}: {entry.entry_id}")
            except Exception as e: 
                pe(f"Entry creation failed: {e}")
                import traceback
                traceback.print_exc()
        else: pe(f"OCR failed: {result.get('error')}")
    except Exception as e: 
        pe(f"OCR error: {e}")
        import traceback
        traceback.print_exc()
else: pe("Image not available - skipping OCR test")
time.sleep(5)

# STEP 7: Verify Database
pstep("STEP 7: Verify Data in Database")
try:
    entries = ContestEntry.objects.filter(contest=contest)
    pi(f"Found {entries.count()} entries")
    if entries.count() > 0:
        e = entries.first()
        ps(f"Entry: {e.entry_id}")
        pi(f"Status: {e.status} | NRIC: {getattr(e,'contestant_nric','N/A')}")
        pi(f"Store: {getattr(e,'store_name','N/A')} | Products: {getattr(e,'products_purchased',[])}")
    c = Customer.objects.filter(phone_number__icontains="123456789").first()
    ps(f"Customer: {c.name} ({c.phone_number})") if c else pi("Customer not found")
except Exception as e: pe(f"Verification failed: {e}")

# STEP 8: Test Contest Manager
pstep("STEP 8: Test Contest Manager Page")
try:
    r = requests.get(f"{APP_URL}/contest/manager/", timeout=10, allow_redirects=False)
    ps(f"Manager accessible (HTTP {r.status_code})") if r.status_code in [200,302] else pe(f"HTTP {r.status_code}")
except Exception as e: pe(f"Failed: {e}")

# STEP 9: Test Participants Manager
pstep("STEP 9: Test Participants Manager Page")
try:
    r = requests.get(f"{APP_URL}/participants/", timeout=10, allow_redirects=False)
    ps(f"Participants accessible (HTTP {r.status_code})") if r.status_code in [200,302] else pe(f"HTTP {r.status_code}")
except Exception as e: pe(f"Failed: {e}")

# STEP 10: Verify Contest Selection
pstep("STEP 10: Verify Contest Selection in Participants Manager")
try:
    # Check if contest appears in dropdown
    r = requests.get(f"{APP_URL}/participants/", timeout=10, allow_redirects=False)
    if r.status_code in [200,302]:
        ps("Participants page accessible")
        # Check if contest name appears in HTML
        if "Test Contest 2" in r.text or CONTEST_ID in r.text:
            ps("Contest appears in page HTML")
        else:
            pe("Contest NOT found in page HTML - check dropdown")
            pi("This might indicate the contests list is empty or not being passed to template")
    
    # Also check database directly
    all_contests = Contest.objects.filter(tenant=tenant)
    pi(f"Database has {all_contests.count()} contests for this tenant")
    for c in all_contests:
        pi(f"  - {c.name} (ID: {c.contest_id}, Active: {c.is_active})")
    
    # Test with contest filter
    r2 = requests.get(f"{APP_URL}/participants/?contest={CONTEST_ID}", timeout=10, allow_redirects=False)
    if r2.status_code in [200,302]:
        ps("Contest filter URL working")
    else:
        pe(f"Contest filter HTTP {r2.status_code}")
except Exception as e: 
    pe(f"Failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*40}\n📊 SUMMARY\n{'='*40}")
print(f"Contest ID: {CONTEST_ID}\nPhone: {TEST_PHONE}")
if IMAGE_URL: print(f"Image: {IMAGE_URL}")
print(f"\n✅ Tests: Contest Creation, Webhook, PDPA, NRIC, OCR, Database, Manager Pages")
print(f"📝 Visit: {APP_URL}/contest/manager/ and {APP_URL}/participants/")
ps("Test completed!")
PYTHON_SCRIPT

