#!/bin/bash
# Comprehensive Test Script for Contest Flow
# Tests: Contest Creation -> WhatsApp Webhook -> Auto Reply -> OCR -> Data Saving

set -e  # Exit on error

PROJECT_ID="whatsapp-bulk-messaging-480620"
APP_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
TEST_PHONE="60123456789"  # Change this to your test phone number
TEST_KEYWORD="JOIN"  # Change this to your contest keyword

echo "=========================================="
echo "Contest Flow Comprehensive Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Check if we can access the app
echo "Step 1: Testing App Accessibility"
echo "-----------------------------------"
if curl -s -o /dev/null -w "%{http_code}" "$APP_URL" | grep -q "200\|302"; then
    print_success "App is accessible"
else
    print_error "App is not accessible"
    exit 1
fi
echo ""

# Step 2: Test Contest Creation (via API or check existing)
echo "Step 2: Testing Contest Creation"
echo "-----------------------------------"
print_info "Checking for existing contests..."

# You'll need to create a contest manually first or via API
# For now, we'll assume a contest exists with keyword "JOIN"
print_info "Please ensure a contest exists with keyword: $TEST_KEYWORD"
print_info "You can create one at: $APP_URL/contest/create/"
read -p "Press Enter after creating a contest..."
echo ""

# Step 3: Test WhatsApp Webhook - Initial Message
echo "Step 3: Testing WhatsApp Webhook - Initial Message"
echo "-----------------------------------"
print_info "Sending initial message with keyword: $TEST_KEYWORD"

WEBHOOK_URL="$APP_URL/webhook/whatsapp/"
TIMESTAMP=$(date +%s)

# Create a test image URL (you can use a real receipt image URL)
TEST_RECEIPT_URL="https://via.placeholder.com/800x600.png?text=Test+Receipt"

# Initial message payload
INITIAL_PAYLOAD=$(cat <<EOF
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "$TEST_PHONE",
          "id": "wamid.test_$(date +%s)",
          "timestamp": "$TIMESTAMP",
          "text": {
            "body": "$TEST_KEYWORD"
          },
          "type": "text"
        }],
        "contacts": [{
          "profile": {
            "name": "Test User"
          },
          "wa_id": "$TEST_PHONE"
        }]
      }
    }]
  }]
}
EOF
)

print_info "Sending webhook payload..."
RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$INITIAL_PAYLOAD")

if echo "$RESPONSE" | grep -q "200\|success"; then
    print_success "Initial webhook message sent successfully"
    echo "Response: $RESPONSE"
else
    print_error "Webhook failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 4: Test PDPA Response
echo "Step 4: Testing PDPA Response"
echo "-----------------------------------"
print_info "Sending PDPA agreement (YES)"
sleep 2

PDPA_PAYLOAD=$(cat <<EOF
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "$TEST_PHONE",
          "id": "wamid.test_pdpa_$(date +%s)",
          "timestamp": "$TIMESTAMP",
          "text": {
            "body": "YES"
          },
          "type": "text"
        }],
        "contacts": [{
          "profile": {
            "name": "Test User"
          },
          "wa_id": "$TEST_PHONE"
        }]
      }
    }]
  }]
}
EOF
)

RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PDPA_PAYLOAD")

if echo "$RESPONSE" | grep -q "200\|success"; then
    print_success "PDPA response sent successfully"
else
    print_error "PDPA response failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 5: Test NRIC Submission
echo "Step 5: Testing NRIC Submission"
echo "-----------------------------------"
print_info "Sending NRIC number"
sleep 2

NRIC_PAYLOAD=$(cat <<EOF
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "$TEST_PHONE",
          "id": "wamid.test_nric_$(date +%s)",
          "timestamp": "$TIMESTAMP",
          "text": {
            "body": "123456789012"
          },
          "type": "text"
        }],
        "contacts": [{
          "profile": {
            "name": "Test User"
          },
          "wa_id": "$TEST_PHONE"
        }]
      }
    }]
  }]
}
EOF
)

RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$NRIC_PAYLOAD")

if echo "$RESPONSE" | grep -q "200\|success"; then
    print_success "NRIC submission sent successfully"
else
    print_error "NRIC submission failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 6: Test Receipt Image (OCR)
echo "Step 6: Testing Receipt Image Upload (OCR)"
echo "-----------------------------------"
print_info "Sending receipt image for OCR processing"

# Create a test image (base64 encoded small image)
# In production, you'd use a real receipt image URL
RECEIPT_IMAGE_ID="test_receipt_$(date +%s)"

RECEIPT_PAYLOAD=$(cat <<EOF
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "$TEST_PHONE",
          "id": "wamid.test_receipt_$(date +%s)",
          "timestamp": "$TIMESTAMP",
          "image": {
            "id": "$RECEIPT_IMAGE_ID",
            "mime_type": "image/jpeg",
            "sha256": "test_hash",
            "caption": "Test Receipt"
          },
          "type": "image"
        }],
        "contacts": [{
          "profile": {
            "name": "Test User"
          },
          "wa_id": "$TEST_PHONE"
        }]
      }
    }]
  }]
}
EOF
)

RESPONSE=$(curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$RECEIPT_PAYLOAD")

if echo "$RESPONSE" | grep -q "200\|success"; then
    print_success "Receipt image sent successfully"
    print_info "OCR processing should happen automatically"
else
    print_error "Receipt image upload failed"
    echo "Response: $RESPONSE"
fi
echo ""

# Step 7: Verify Data in Database
echo "Step 7: Verifying Data in Database"
echo "-----------------------------------"
print_info "Checking if data was saved..."

# Note: This requires database access. If you have Cloud SQL Proxy running:
# python3 << 'PYTHON_EOF'
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
# django.setup()
# 
# from messaging.models import ContestEntry, Contest, Customer
# 
# # Find the test entry
# entries = ContestEntry.objects.filter(contestant_phone__contains='123456789')
# print(f"Found {entries.count()} entries")
# for entry in entries:
#     print(f"Entry ID: {entry.entry_id}")
#     print(f"Status: {entry.status}")
#     print(f"Verified: {entry.is_verified}")
#     print(f"Store: {entry.store_name}")
#     print(f"Amount: {entry.receipt_amount}")
# PYTHON_EOF

print_info "To verify data, check:"
print_info "1. Contest Manager: $APP_URL/contest/manager/"
print_info "2. Participants Manager: $APP_URL/participants/"
echo ""

# Step 8: Test Contest Manager Page
echo "Step 8: Testing Contest Manager Page"
echo "-----------------------------------"
print_info "Checking contest manager accessibility..."

CONTEST_MANAGER_URL="$APP_URL/contest/manager/"
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$CONTEST_MANAGER_URL")

if [ "$STATUS_CODE" = "200" ]; then
    print_success "Contest Manager page is accessible (HTTP $STATUS_CODE)"
elif [ "$STATUS_CODE" = "302" ]; then
    print_info "Contest Manager requires login (HTTP $STATUS_CODE - redirect)"
else
    print_error "Contest Manager returned HTTP $STATUS_CODE"
fi
echo ""

# Step 9: Test Participants Manager Page
echo "Step 9: Testing Participants Manager Page"
echo "-----------------------------------"
print_info "Checking participants manager accessibility..."

PARTICIPANTS_URL="$APP_URL/participants/"
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$PARTICIPANTS_URL")

if [ "$STATUS_CODE" = "200" ]; then
    print_success "Participants Manager page is accessible (HTTP $STATUS_CODE)"
elif [ "$STATUS_CODE" = "302" ]; then
    print_info "Participants Manager requires login (HTTP $STATUS_CODE - redirect)"
else
    print_error "Participants Manager returned HTTP $STATUS_CODE"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
print_info "Test completed!"
print_info "Next steps:"
print_info "1. Check WhatsApp for automated replies"
print_info "2. Verify data in Contest Manager: $APP_URL/contest/manager/"
print_info "3. Verify data in Participants Manager: $APP_URL/participants/"
print_info "4. Check application logs: gcloud app logs read --limit=50"
echo ""

echo "To view detailed logs:"
echo "gcloud app logs tail --project=$PROJECT_ID"
echo ""

