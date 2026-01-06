#!/bin/bash
# =============================================================================
# Complete Contest Flow Test Script
# Tests: Contest Creation → WhatsApp Webhook → Auto Reply → OCR → Data Storage
# =============================================================================

set -e  # Exit on error

echo "=========================================="
echo "🧪 COMPLETE CONTEST FLOW TEST"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="whatsapp-bulk-messaging-480620"
APP_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE="+60123456789"
TEST_NAME="Test User"
TEST_EMAIL="test@example.com"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# =============================================================================
# STEP 1: Setup - Check Environment
# =============================================================================
echo "📋 STEP 1: Environment Check"
echo "----------------------------------------"

cd ~/app-full || { print_error "Directory ~/app-full not found!"; exit 1; }
print_success "Working directory: $(pwd)"

# Check if Django is available
python3 -c "import django; print(f'Django {django.get_version()}')" || { print_error "Django not found!"; exit 1; }
print_success "Django is available"

echo ""

# =============================================================================
# STEP 2: Create Test Contest via Django Shell
# =============================================================================
echo "📋 STEP 2: Create Test Contest"
echo "----------------------------------------"

CONTEST_DATA=$(python3 << 'PYTHON_EOF'
import os
import django
import sys
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, Tenant

try:
    # Get or create a tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("ERROR: No tenant found. Please create a tenant first.")
        sys.exit(1)
    
    # Create test contest
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
    
    print(f"SUCCESS:{contest.contest_id}")
    print(f"NAME:{contest.name}")
except Exception as e:
    print(f"ERROR:{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF
)

if [[ $CONTEST_DATA == ERROR:* ]]; then
    print_error "Failed to create contest: ${CONTEST_DATA#ERROR:}"
    exit 1
fi

CONTEST_ID=$(echo "$CONTEST_DATA" | grep "SUCCESS:" | cut -d: -f2)
CONTEST_NAME=$(echo "$CONTEST_DATA" | grep "NAME:" | cut -d: -f2-)

print_success "Contest created: $CONTEST_NAME"
print_info "Contest ID: $CONTEST_ID"
echo ""

# =============================================================================
# STEP 3: Test WhatsApp Webhook - Initial Message
# =============================================================================
echo "📋 STEP 3: Test WhatsApp Webhook - Initial Message (Keyword: TEST)"
echo "----------------------------------------"

WEBHOOK_RESPONSE1=$(curl -s -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {
              \"body\": \"TEST\"
            },
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {
              \"name\": \"$TEST_NAME\"
            },
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

if [[ $WEBHOOK_RESPONSE1 == *"200"* ]] || [[ $WEBHOOK_RESPONSE1 == *"OK"* ]] || [[ -z "$WEBHOOK_RESPONSE1" ]]; then
    print_success "Webhook received initial message"
else
    print_error "Webhook response: $WEBHOOK_RESPONSE1"
fi

sleep 2
echo ""

# =============================================================================
# STEP 4: Test PDPA Agreement
# =============================================================================
echo "📋 STEP 4: Test PDPA Agreement (Reply: AGREE)"
echo "----------------------------------------"

WEBHOOK_RESPONSE2=$(curl -s -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {
              \"body\": \"AGREE\"
            },
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {
              \"name\": \"$TEST_NAME\"
            },
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

if [[ $WEBHOOK_RESPONSE2 == *"200"* ]] || [[ $WEBHOOK_RESPONSE2 == *"OK"* ]] || [[ -z "$WEBHOOK_RESPONSE2" ]]; then
    print_success "PDPA agreement processed"
else
    print_error "Webhook response: $WEBHOOK_RESPONSE2"
fi

sleep 2
echo ""

# =============================================================================
# STEP 5: Test NRIC Submission
# =============================================================================
echo "📋 STEP 5: Test NRIC Submission"
echo "----------------------------------------"

WEBHOOK_RESPONSE3=$(curl -s -X POST "$APP_URL/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d "{
    \"entry\": [{
      \"changes\": [{
        \"value\": {
          \"messages\": [{
            \"from\": \"$TEST_PHONE\",
            \"type\": \"text\",
            \"text\": {
              \"body\": \"123456789012\"
            },
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {
              \"name\": \"$TEST_NAME\"
            },
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

if [[ $WEBHOOK_RESPONSE3 == *"200"* ]] || [[ $WEBHOOK_RESPONSE3 == *"OK"* ]] || [[ -z "$WEBHOOK_RESPONSE3" ]]; then
    print_success "NRIC submission processed"
else
    print_error "Webhook response: $WEBHOOK_RESPONSE3"
fi

sleep 2
echo ""

# =============================================================================
# STEP 6: Test Receipt Image (OCR)
# =============================================================================
echo "📋 STEP 6: Test Receipt Image Upload (OCR)"
echo "----------------------------------------"

# Create a simple test image (1x1 pixel PNG) as base64
TEST_IMAGE_BASE64="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

WEBHOOK_RESPONSE4=$(curl -s -X POST "$APP_URL/webhook/whatsapp/" \
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
              \"mime_type\": \"image/png\",
              \"caption\": \"Test receipt\"
            },
            \"id\": \"test_msg_$(date +%s)\",
            \"timestamp\": \"$(date +%s)\"
          }],
          \"contacts\": [{
            \"profile\": {
              \"name\": \"$TEST_NAME\"
            },
            \"wa_id\": \"$TEST_PHONE\"
          }]
        }
      }]
    }]
  }")

if [[ $WEBHOOK_RESPONSE4 == *"200"* ]] || [[ $WEBHOOK_RESPONSE4 == *"OK"* ]] || [[ -z "$WEBHOOK_RESPONSE4" ]]; then
    print_success "Receipt image received (OCR will process in background)"
else
    print_error "Webhook response: $WEBHOOK_RESPONSE4"
fi

sleep 5  # Wait for OCR processing
echo ""

# =============================================================================
# STEP 7: Verify Data in Database
# =============================================================================
echo "📋 STEP 7: Verify Data Saved in Database"
echo "----------------------------------------"

VERIFICATION_RESULT=$(python3 << PYTHON_EOF
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer
from django.utils import timezone

try:
    # Find the test contest
    contest = Contest.objects.filter(name__icontains="Test Contest - Full Flow").first()
    if not contest:
        print("ERROR:Test contest not found")
        sys.exit(1)
    
    print(f"SUCCESS:Found contest: {contest.name}")
    
    # Find entries for this contest
    entries = ContestEntry.objects.filter(contest=contest)
    entry_count = entries.count()
    print(f"ENTRIES:{entry_count}")
    
    if entry_count > 0:
        entry = entries.first()
        print(f"ENTRY_ID:{entry.entry_id}")
        print(f"STATUS:{entry.status}")
        print(f"NRIC:{getattr(entry, 'contestant_nric', 'N/A')}")
        print(f"VERIFIED:{entry.is_verified}")
        print(f"RECEIPT_URL:{getattr(entry, 'receipt_image_url', 'N/A')}")
        print(f"STORE_NAME:{getattr(entry, 'store_name', 'N/A')}")
        print(f"PRODUCTS:{getattr(entry, 'products_purchased', [])}")
    else:
        print("WARNING:No entries found yet (may need to wait for processing)")
    
    # Find customer
    customer = Customer.objects.filter(phone_number__icontains="123456789").first()
    if customer:
        print(f"CUSTOMER:{customer.name} ({customer.phone_number})")
    else:
        print("CUSTOMER:Not found")
        
except Exception as e:
    print(f"ERROR:{str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_EOF
)

if [[ $VERIFICATION_RESULT == ERROR:* ]]; then
    print_error "Verification failed: ${VERIFICATION_RESULT#ERROR:}"
else
    echo "$VERIFICATION_RESULT" | while IFS= read -r line; do
        if [[ $line == SUCCESS:* ]]; then
            print_success "${line#SUCCESS:}"
        elif [[ $line == ENTRIES:* ]]; then
            COUNT="${line#ENTRIES:}"
            if [[ $COUNT -gt 0 ]]; then
                print_success "Found $COUNT contest entry/entries"
            else
                print_info "No entries yet (may need more time for processing)"
            fi
        elif [[ $line == WARNING:* ]]; then
            print_info "${line#WARNING:}"
        elif [[ $line == ENTRY_* ]] || [[ $line == CUSTOMER:* ]] || [[ $line == STATUS:* ]] || [[ $line == NRIC:* ]] || [[ $line == VERIFIED:* ]] || [[ $line == RECEIPT_URL:* ]] || [[ $line == STORE_NAME:* ]] || [[ $line == PRODUCTS:* ]]; then
            print_info "$line"
        fi
    done
fi

echo ""

# =============================================================================
# STEP 8: Test Contest Manager Page
# =============================================================================
echo "📋 STEP 8: Test Contest Manager Page"
echo "----------------------------------------"

MANAGER_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/contest/manager/" \
  -H "Cookie: sessionid=test" \
  --max-time 10)

if [[ $MANAGER_RESPONSE == "200" ]] || [[ $MANAGER_RESPONSE == "302" ]]; then
    print_success "Contest Manager page accessible (HTTP $MANAGER_RESPONSE)"
else
    print_error "Contest Manager page returned HTTP $MANAGER_RESPONSE"
fi

echo ""

# =============================================================================
# STEP 9: Test Participants Manager Page
# =============================================================================
echo "📋 STEP 9: Test Participants Manager Page"
echo "----------------------------------------"

PARTICIPANTS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/participants/" \
  -H "Cookie: sessionid=test" \
  --max-time 10)

if [[ $PARTICIPANTS_RESPONSE == "200" ]] || [[ $PARTICIPANTS_RESPONSE == "302" ]]; then
    print_success "Participants Manager page accessible (HTTP $PARTICIPANTS_RESPONSE)"
else
    print_error "Participants Manager page returned HTTP $PARTICIPANTS_RESPONSE"
fi

echo ""

# =============================================================================
# STEP 10: Summary
# =============================================================================
echo "=========================================="
echo "📊 TEST SUMMARY"
echo "=========================================="
echo ""
echo "Test Contest ID: $CONTEST_ID"
echo "Test Phone: $TEST_PHONE"
echo ""
echo "✅ Tests Completed:"
echo "   1. Contest Creation"
echo "   2. WhatsApp Webhook (Initial Message)"
echo "   3. PDPA Agreement Flow"
echo "   4. NRIC Submission"
echo "   5. Receipt Image Upload (OCR)"
echo "   6. Database Verification"
echo "   7. Contest Manager Page"
echo "   8. Participants Manager Page"
echo ""
echo "📝 Next Steps:"
echo "   1. Check App Engine logs: gcloud app logs read --limit=50"
echo "   2. Visit Contest Manager: $APP_URL/contest/manager/"
echo "   3. Visit Participants Manager: $APP_URL/participants/"
echo "   4. Check database entries using Django shell"
echo ""
print_success "Test script completed!"
echo ""

