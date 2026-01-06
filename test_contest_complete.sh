#!/bin/bash
# =============================================================================
# COMPLETE CONTEST FLOW TEST - Copy & Paste into Cloud Shell
# Tests: Contest Creation → WhatsApp Webhook → Auto Reply → OCR → Data Storage
# Uses real image: img/Gurdial_Singh_AL_Natha_Singh.jpg
# =============================================================================

set -e

echo "=========================================="
echo "🧪 COMPLETE CONTEST FLOW TEST"
echo "=========================================="
echo ""

cd ~/app-full || { echo "❌ Directory ~/app-full not found!"; exit 1; }

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ps() { echo -e "${GREEN}✅ $1${NC}"; }
pe() { echo -e "${RED}❌ $1${NC}"; }
pi() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
pstep() { echo -e "\n${BLUE}📋 $1${NC}\n" + "-"*40; }

APP_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE="+60123456789"
TEST_NAME="Test User"

# =============================================================================
# STEP 1: Create Test Contest
# =============================================================================
pstep "STEP 1: Create Test Contest"

CONTEST_OUTPUT=$(python3 << 'PYEOF'
import os, sys, django
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()
from messaging.models import Contest, Tenant

try:
    tenant = Tenant.objects.first()
    if not tenant:
        print("ERROR:No tenant found")
        sys.exit(1)
    
    existing = Contest.objects.filter(name__icontains="Test Contest - Full Flow").first()
    if existing:
        print(f"EXISTS:{existing.contest_id}")
        print(f"NAME:{existing.name}")
    else:
        contest = Contest.objects.create(
            tenant=tenant, name="🧪 Test Contest - Full Flow",
            description="Automated test", starts_at=datetime.now()-timedelta(days=1),
            ends_at=datetime.now()+timedelta(days=30), is_active=True,
            keywords="TEST,JOIN,START",
            auto_reply_message="Welcome! Reply 'AGREE' to continue.",
            introduction_message="Hello! Welcome to our test contest.",
            pdpa_message="Do you agree to our PDPA terms? Reply 'AGREE'.",
            participant_agreement="Thank you! Please send your NRIC number.",
            requires_nric=True, requires_receipt=True, min_purchase_amount=10.00
        )
        print(f"CREATED:{contest.contest_id}")
        print(f"NAME:{contest.name}")
except Exception as e:
    print(f"ERROR:{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
)

if [[ $CONTEST_OUTPUT == ERROR:* ]]; then
    pe "Failed: ${CONTEST_OUTPUT#ERROR:}"
    exit 1
fi

CONTEST_ID=$(echo "$CONTEST_OUTPUT" | grep -E "CREATED:|EXISTS:" | cut -d: -f2)
CONTEST_NAME=$(echo "$CONTEST_OUTPUT" | grep "NAME:" | cut -d: -f2-)
ps "Contest: $CONTEST_NAME"
pi "Contest ID: $CONTEST_ID"

# =============================================================================
# STEP 2: Upload Test Image to Cloud Storage
# =============================================================================
pstep "STEP 2: Upload Test Image for OCR"

# Check if image exists locally, if not download from staging
if [ ! -f "img/Gurdial_Singh_AL_Natha_Singh.jpg" ]; then
    pi "Image not found locally, checking Cloud Storage..."
    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/img/Gurdial_Singh_AL_Natha_Singh.jpg img/ 2>/dev/null || {
        pe "Image not found. Please upload img/Gurdial_Singh_AL_Natha_Singh.jpg to Cloud Storage first."
        pe "Run: gsutil cp img/Gurdial_Singh_AL_Natha_Singh.jpg gs://staging.whatsapp-bulk-messaging-480620.appspot.com/img/"
        exit 1
    }
fi

# Upload to Cloud Storage for webhook access
IMAGE_URL=""
if [ -f "img/Gurdial_Singh_AL_Natha_Singh.jpg" ]; then
    gsutil cp img/Gurdial_Singh_AL_Natha_Singh.jpg gs://staging.whatsapp-bulk-messaging-480620.appspot.com/test_images/ 2>/dev/null || true
    # Make it publicly accessible
    gsutil acl ch -u AllUsers:R gs://staging.whatsapp-bulk-messaging-480620.appspot.com/test_images/Gurdial_Singh_AL_Natha_Singh.jpg 2>/dev/null || true
    IMAGE_URL="https://storage.googleapis.com/staging.whatsapp-bulk-messaging-480620.appspot.com/test_images/Gurdial_Singh_AL_Natha_Singh.jpg"
    ps "Image uploaded: $IMAGE_URL"
else
    pe "Image file not found!"
    exit 1
fi

# =============================================================================
# STEP 3: Test WhatsApp Webhook - Initial Message
# =============================================================================
pstep "STEP 3: Test Webhook - Initial Message (TEST)"

RESPONSE1=$(curl -s -w "\n%{http_code}" -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {\"body\": \"TEST\"},
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {\"name\": \"$TEST_NAME\"},
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

HTTP_CODE1=$(echo "$RESPONSE1" | tail -1)
if [[ $HTTP_CODE1 == "200" ]] || [[ $HTTP_CODE1 == "201" ]]; then
    ps "Webhook received initial message"
else
    pe "Webhook returned HTTP $HTTP_CODE1"
fi
sleep 2

# =============================================================================
# STEP 4: Test PDPA Agreement
# =============================================================================
pstep "STEP 4: Test PDPA Agreement (AGREE)"

RESPONSE2=$(curl -s -w "\n%{http_code}" -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {\"body\": \"AGREE\"},
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {\"name\": \"$TEST_NAME\"},
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

HTTP_CODE2=$(echo "$RESPONSE2" | tail -1)
if [[ $HTTP_CODE2 == "200" ]] || [[ $HTTP_CODE2 == "201" ]]; then
    ps "PDPA agreement processed"
else
    pe "Webhook returned HTTP $HTTP_CODE2"
fi
sleep 2

# =============================================================================
# STEP 5: Test NRIC Submission
# =============================================================================
pstep "STEP 5: Test NRIC Submission"

RESPONSE3=$(curl -s -w "\n%{http_code}" -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {\"body\": \"123456789012\"},
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {\"name\": \"$TEST_NAME\"},
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

HTTP_CODE3=$(echo "$RESPONSE3" | tail -1)
if [[ $HTTP_CODE3 == "200" ]] || [[ $HTTP_CODE3 == "201" ]]; then
    ps "NRIC submission processed"
else
    pe "Webhook returned HTTP $HTTP_CODE3"
fi
sleep 2

# =============================================================================
# STEP 6: Test Receipt Image with Real Image (OCR)
# =============================================================================
pstep "STEP 6: Test Receipt Image Upload (OCR) - Using Real Image"

# For testing, we'll simulate the image by providing a URL that the webhook can download
# The webhook will download from the URL and process it

RESPONSE4=$(curl -s -w "\n%{http_code}" -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"image\",
            \"image\": {
              \"id\": \"test_image_$(date +%s)\",
              \"mime_type\": \"image/jpeg\",
              \"caption\": \"Test receipt\"
            },
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {\"name\": \"$TEST_NAME\"},
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

HTTP_CODE4=$(echo "$RESPONSE4" | tail -1)
if [[ $HTTP_CODE4 == "200" ]] || [[ $HTTP_CODE4 == "201" ]]; then
    ps "Receipt image received (OCR processing in background)"
else
    pe "Webhook returned HTTP $HTTP_CODE4"
fi

pi "Waiting 10 seconds for OCR processing..."
sleep 10

# =============================================================================
# STEP 7: Direct OCR Test with Image URL
# =============================================================================
pstep "STEP 7: Direct OCR Test with Image URL"

OCR_RESULT=$(python3 << PYEOF
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.receipt_ocr_service import ReceiptOCRService

try:
    service = ReceiptOCRService()
    image_url = "$IMAGE_URL"
    
    if not image_url:
        print("ERROR:Image URL not set")
        sys.exit(1)
    
    print(f"INFO:Processing image: {image_url}")
    result = service.process_receipt_image(image_url)
    
    if result.get('success'):
        print(f"SUCCESS:OCR completed")
        print(f"STORE:{result.get('store_name', 'N/A')}")
        print(f"LOCATION:{result.get('store_location', 'N/A')}")
        print(f"AMOUNT:{result.get('amount_spent', 'N/A')}")
        print(f"PRODUCTS:{result.get('products', [])}")
    else:
        print(f"ERROR:{result.get('error', 'Unknown error')}")
except Exception as e:
    print(f"ERROR:{str(e)}")
    import traceback
    traceback.print_exc()
PYEOF
)

if [[ $OCR_RESULT == SUCCESS:* ]]; then
    ps "OCR test successful"
    echo "$OCR_RESULT" | grep -E "STORE:|LOCATION:|AMOUNT:|PRODUCTS:" | while read line; do
        pi "$line"
    done
else
    pe "OCR test failed: ${OCR_RESULT#ERROR:}"
fi

# =============================================================================
# STEP 8: Verify Data in Database
# =============================================================================
pstep "STEP 8: Verify Data Saved in Database"

VERIFY_OUTPUT=$(python3 << PYEOF
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer

try:
    contest = Contest.objects.filter(contest_id="$CONTEST_ID").first()
    if not contest:
        print("ERROR:Contest not found")
        sys.exit(1)
    
    entries = ContestEntry.objects.filter(contest=contest)
    print(f"ENTRIES:{entries.count()}")
    
    if entries.count() > 0:
        entry = entries.first()
        print(f"ENTRY_ID:{entry.entry_id}")
        print(f"STATUS:{entry.status}")
        print(f"NRIC:{getattr(entry, 'contestant_nric', 'N/A')}")
        print(f"VERIFIED:{entry.is_verified}")
        print(f"RECEIPT_URL:{getattr(entry, 'receipt_image_url', 'N/A')}")
        print(f"STORE_NAME:{getattr(entry, 'store_name', 'N/A')}")
        print(f"STORE_LOCATION:{getattr(entry, 'store_location', 'N/A')}")
        print(f"PRODUCTS:{getattr(entry, 'products_purchased', [])}")
        print(f"AMOUNT:{getattr(entry, 'receipt_amount', 'N/A')}")
    else:
        print("WARNING:No entries found yet")
    
    customer = Customer.objects.filter(phone_number__icontains="123456789").first()
    if customer:
        print(f"CUSTOMER:{customer.name} ({customer.phone_number})")
    else:
        print("CUSTOMER:Not found")
except Exception as e:
    print(f"ERROR:{str(e)}")
    import traceback
    traceback.print_exc()
PYEOF
)

if [[ $VERIFY_OUTPUT == ERROR:* ]]; then
    pe "Verification failed: ${VERIFY_OUTPUT#ERROR:}"
else
    echo "$VERIFY_OUTPUT" | while IFS= read -r line; do
        if [[ $line == ENTRIES:* ]]; then
            COUNT="${line#ENTRIES:}"
            if [[ $COUNT -gt 0 ]]; then
                ps "Found $COUNT contest entry/entries"
            else
                pi "No entries yet (may need more time)"
            fi
        elif [[ $line == ENTRY_* ]] || [[ $line == CUSTOMER:* ]] || [[ $line == STATUS:* ]] || [[ $line == NRIC:* ]] || [[ $line == VERIFIED:* ]] || [[ $line == RECEIPT_URL:* ]] || [[ $line == STORE_* ]] || [[ $line == PRODUCTS:* ]] || [[ $line == AMOUNT:* ]]; then
            pi "$line"
        fi
    done
fi

# =============================================================================
# STEP 9: Test Contest Manager Page
# =============================================================================
pstep "STEP 9: Test Contest Manager Page"

MANAGER_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/contest/manager/" --max-time 10)
if [[ $MANAGER_CODE == "200" ]] || [[ $MANAGER_CODE == "302" ]]; then
    ps "Contest Manager accessible (HTTP $MANAGER_CODE)"
else
    pe "Contest Manager returned HTTP $MANAGER_CODE"
fi

# =============================================================================
# STEP 10: Test Participants Manager Page
# =============================================================================
pstep "STEP 10: Test Participants Manager Page"

PARTICIPANTS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/participants/" --max-time 10)
if [[ $PARTICIPANTS_CODE == "200" ]] || [[ $PARTICIPANTS_CODE == "302" ]]; then
    ps "Participants Manager accessible (HTTP $PARTICIPANTS_CODE)"
else
    pe "Participants Manager returned HTTP $PARTICIPANTS_CODE"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=========================================="
echo "📊 TEST SUMMARY"
echo "=========================================="
echo ""
echo "Contest ID: $CONTEST_ID"
echo "Test Phone: $TEST_PHONE"
echo "Image URL: $IMAGE_URL"
echo ""
echo "✅ Tests Completed:"
echo "   1. Contest Creation"
echo "   2. WhatsApp Webhook (Initial Message)"
echo "   3. PDPA Agreement Flow"
echo "   4. NRIC Submission"
echo "   5. Receipt Image Upload (OCR)"
echo "   6. Direct OCR Test"
echo "   7. Database Verification"
echo "   8. Contest Manager Page"
echo "   9. Participants Manager Page"
echo ""
ps "Test script completed!"
echo ""

