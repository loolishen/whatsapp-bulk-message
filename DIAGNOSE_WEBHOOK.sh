#!/bin/bash
# =============================================================================
# DIAGNOSE WEBHOOK ISSUES
# This script helps diagnose why WABot messages aren't reaching the webhook
# =============================================================================

echo "🔍 WEBHOOK DIAGNOSTIC TOOL"
echo "=========================="
echo ""

WEBHOOK_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"

# Test 1: Check if webhook is accessible
echo "📋 Test 1: Webhook Accessibility (GET)"
echo "--------------------------------------"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$WEBHOOK_URL")
http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

if [ "$http_code" = "200" ]; then
    echo "✅ Webhook URL is accessible"
else
    echo "❌ Webhook URL returned HTTP $http_code"
fi
echo "Response: $body"
echo ""

# Test 2: Check recent logs for ANY webhook activity
echo "📋 Test 2: Recent Webhook Activity in Logs"
echo "------------------------------------------"
echo "Checking last 200 log entries for webhook activity..."
echo ""

gcloud app logs read --limit=200 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|POST.*whatsapp\|WEBHOOK REQUEST" | tail -20

if [ $? -ne 0 ]; then
    echo "⚠️  No webhook activity found in recent logs"
    echo "   This means WABot is NOT sending messages to your webhook"
fi
echo ""

# Test 3: Check for ALL POST requests to webhook
echo "📋 Test 3: All POST Requests to /webhook/whatsapp/"
echo "-----------------------------------------------"
gcloud app logs read --limit=500 --project=whatsapp-bulk-messaging-480620 | grep "POST.*webhook/whatsapp" | tail -10

if [ $? -ne 0 ]; then
    echo "⚠️  No POST requests found to /webhook/whatsapp/"
fi
echo ""

# Test 4: Simulate a WABot message
echo "📋 Test 4: Simulate WABot Message Format"
echo "----------------------------------------"
echo "Sending test message in WABot format..."

test_payload='{
  "type": "message",
  "data": {
    "from": "60123456789",
    "message": "TEST",
    "id": "test_001",
    "timestamp": "1640995200"
  }
}'

response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    -w "\nHTTP_CODE:%{http_code}")

http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 5: Check logs immediately after test
echo "📋 Test 5: Check Logs After Test Message"
echo "-----------------------------------------"
echo "Waiting 3 seconds for logs to appear..."
sleep 3
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|test_001" | tail -10
echo ""

# Summary
echo "📊 DIAGNOSIS SUMMARY"
echo "==================="
echo ""
echo "If you see:"
echo "  ✅ Webhook accessible + POST requests in logs = Webhook is working"
echo "  ❌ No POST requests in logs = WABot is not sending to your webhook"
echo ""
echo "Common Issues:"
echo "  1. WABot webhook URL not set correctly"
echo "  2. WABot 'Forward Data to Webhook' not enabled"
echo "  3. WABot instance not connected/active"
echo "  4. WABot webhook events not configured (need 'message' event)"
echo ""
echo "Next Steps:"
echo "  1. Verify in WABot Dashboard:"
echo "     - Webhook URL is set correctly"
echo "     - 'Forward Data to Webhook' is ENABLED"
echo "     - 'Message' events are enabled"
echo "  2. Check WABot instance status (should be 'Connected')"
echo "  3. Try sending a test message from WABot dashboard"
echo ""




# =============================================================================
# DIAGNOSE WEBHOOK ISSUES
# This script helps diagnose why WABot messages aren't reaching the webhook
# =============================================================================

echo "🔍 WEBHOOK DIAGNOSTIC TOOL"
echo "=========================="
echo ""

WEBHOOK_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"

# Test 1: Check if webhook is accessible
echo "📋 Test 1: Webhook Accessibility (GET)"
echo "--------------------------------------"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$WEBHOOK_URL")
http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

if [ "$http_code" = "200" ]; then
    echo "✅ Webhook URL is accessible"
else
    echo "❌ Webhook URL returned HTTP $http_code"
fi
echo "Response: $body"
echo ""

# Test 2: Check recent logs for ANY webhook activity
echo "📋 Test 2: Recent Webhook Activity in Logs"
echo "------------------------------------------"
echo "Checking last 200 log entries for webhook activity..."
echo ""

gcloud app logs read --limit=200 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|POST.*whatsapp\|WEBHOOK REQUEST" | tail -20

if [ $? -ne 0 ]; then
    echo "⚠️  No webhook activity found in recent logs"
    echo "   This means WABot is NOT sending messages to your webhook"
fi
echo ""

# Test 3: Check for ALL POST requests to webhook
echo "📋 Test 3: All POST Requests to /webhook/whatsapp/"
echo "-----------------------------------------------"
gcloud app logs read --limit=500 --project=whatsapp-bulk-messaging-480620 | grep "POST.*webhook/whatsapp" | tail -10

if [ $? -ne 0 ]; then
    echo "⚠️  No POST requests found to /webhook/whatsapp/"
fi
echo ""

# Test 4: Simulate a WABot message
echo "📋 Test 4: Simulate WABot Message Format"
echo "----------------------------------------"
echo "Sending test message in WABot format..."

test_payload='{
  "type": "message",
  "data": {
    "from": "60123456789",
    "message": "TEST",
    "id": "test_001",
    "timestamp": "1640995200"
  }
}'

response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    -w "\nHTTP_CODE:%{http_code}")

http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

echo "HTTP Status: $http_code"
echo "Response: $body"
echo ""

# Test 5: Check logs immediately after test
echo "📋 Test 5: Check Logs After Test Message"
echo "-----------------------------------------"
echo "Waiting 3 seconds for logs to appear..."
sleep 3
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|test_001" | tail -10
echo ""

# Summary
echo "📊 DIAGNOSIS SUMMARY"
echo "==================="
echo ""
echo "If you see:"
echo "  ✅ Webhook accessible + POST requests in logs = Webhook is working"
echo "  ❌ No POST requests in logs = WABot is not sending to your webhook"
echo ""
echo "Common Issues:"
echo "  1. WABot webhook URL not set correctly"
echo "  2. WABot 'Forward Data to Webhook' not enabled"
echo "  3. WABot instance not connected/active"
echo "  4. WABot webhook events not configured (need 'message' event)"
echo ""
echo "Next Steps:"
echo "  1. Verify in WABot Dashboard:"
echo "     - Webhook URL is set correctly"
echo "     - 'Forward Data to Webhook' is ENABLED"
echo "     - 'Message' events are enabled"
echo "  2. Check WABot instance status (should be 'Connected')"
echo "  3. Try sending a test message from WABot dashboard"
echo ""






