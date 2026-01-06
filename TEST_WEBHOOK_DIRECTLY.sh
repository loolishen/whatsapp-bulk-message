#!/bin/bash
# =============================================================================
# TEST WEBHOOK DIRECTLY
# This tests if your webhook endpoint is working and accessible
# =============================================================================

echo "🧪 TESTING WEBHOOK ENDPOINT DIRECTLY"
echo "===================================="
echo ""

WEBHOOK_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"

# Test 1: GET request (validation)
echo "📋 Test 1: GET Request (Webhook Validation)"
echo "-------------------------------------------"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$WEBHOOK_URL")
http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ GET request successful - webhook is accessible"
else
    echo "❌ GET request failed (HTTP $http_code)"
    echo "   Your webhook endpoint is not accessible!"
    exit 1
fi

# Test 2: POST request with WABot format
echo ""
echo "📋 Test 2: POST Request (WABot Message Format)"
echo "--------------------------------------------"
test_payload='{
  "type": "message",
  "data": {
    "from": "60123456789",
    "message": "TEST",
    "id": "test_direct_001",
    "timestamp": "1640995200"
  }
}'

echo "Sending test message..."
response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    -w "\nHTTP_CODE:%{http_code}")

http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

if [ "$http_code" = "200" ]; then
    echo "✅ POST request successful - webhook can receive messages"
else
    echo "❌ POST request failed (HTTP $http_code)"
fi

# Test 3: Check logs immediately
echo ""
echo "📋 Test 3: Checking Logs for Test Message"
echo "------------------------------------------"
echo "Waiting 3 seconds for logs to appear..."
sleep 3

echo ""
echo "Recent webhook logs:"
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "WEBHOOK REQUEST\|test_direct_001\|webhook" | tail -10

if [ $? -ne 0 ]; then
    echo "⚠️  No webhook logs found"
fi

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
echo "If both GET and POST return 200:"
echo "  ✅ Your webhook endpoint is WORKING"
echo "  ❌ The problem is in WABot configuration"
echo ""
echo "Next Steps:"
echo "  1. Go to WABot Dashboard"
echo "  2. Check Webhook Settings:"
echo "     - URL: $WEBHOOK_URL"
echo "     - 'Forward Data to Webhook' = ENABLED ✓"
echo "     - 'Message' events = ENABLED ✓"
echo "  3. Check Instance Status:"
echo "     - Should show 'Connected' (green)"
echo "     - If disconnected, reconnect your WhatsApp"
echo "  4. Try 'Test Webhook' button in WABot dashboard"
echo ""

