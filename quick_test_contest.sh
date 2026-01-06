#!/bin/bash
# Quick Test Script - Run this in Cloud Shell

APP_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
WEBHOOK="$APP_URL/webhook/whatsapp/"
PHONE="60123456789"  # CHANGE THIS
KEYWORD="JOIN"  # CHANGE THIS

echo "🧪 Testing Contest Flow..."
echo ""

# Test 1: Initial Keyword
echo "1️⃣ Sending keyword: $KEYWORD"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"$PHONE\",\"id\":\"test1\",\"timestamp\":\"$(date +%s)\",\"text\":{\"body\":\"$KEYWORD\"},\"type\":\"text\"}],\"contacts\":[{\"profile\":{\"name\":\"Test\"},\"wa_id\":\"$PHONE\"}]}}]}]}" \
  && echo " ✅ Sent" || echo " ❌ Failed"
sleep 3

# Test 2: PDPA YES
echo "2️⃣ Sending PDPA: YES"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"$PHONE\",\"id\":\"test2\",\"timestamp\":\"$(date +%s)\",\"text\":{\"body\":\"YES\"},\"type\":\"text\"}],\"contacts\":[{\"profile\":{\"name\":\"Test\"},\"wa_id\":\"$PHONE\"}]}}]}]}" \
  && echo " ✅ Sent" || echo " ❌ Failed"
sleep 3

# Test 3: NRIC
echo "3️⃣ Sending NRIC: 123456789012"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"$PHONE\",\"id\":\"test3\",\"timestamp\":\"$(date +%s)\",\"text\":{\"body\":\"123456789012\"},\"type\":\"text\"}],\"contacts\":[{\"profile\":{\"name\":\"Test\"},\"wa_id\":\"$PHONE\"}]}}]}]}" \
  && echo " ✅ Sent" || echo " ❌ Failed"
sleep 3

# Test 4: Receipt Image
echo "4️⃣ Sending Receipt Image (OCR)"
curl -s -X POST "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"entry\":[{\"changes\":[{\"value\":{\"messages\":[{\"from\":\"$PHONE\",\"id\":\"test4\",\"timestamp\":\"$(date +%s)\",\"image\":{\"id\":\"img_test\",\"mime_type\":\"image/jpeg\"},\"type\":\"image\"}],\"contacts\":[{\"profile\":{\"name\":\"Test\"},\"wa_id\":\"$PHONE\"}]}}]}]}" \
  && echo " ✅ Sent" || echo " ❌ Failed"

echo ""
echo "✅ Test complete! Check:"
echo "   📊 Contest Manager: $APP_URL/contest/manager/"
echo "   👥 Participants: $APP_URL/participants/"
echo "   📱 WhatsApp for replies"

