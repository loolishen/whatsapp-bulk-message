#!/bin/bash
# =============================================================================
# TEST WEBHOOK ACCESSIBILITY
# This tests if your webhook URL is accessible and responding correctly
# =============================================================================

WEBHOOK_URL="https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"

echo "🔍 Testing Webhook Accessibility"
echo "================================"
echo ""
echo "📋 Webhook URL: $WEBHOOK_URL"
echo ""

# Test 1: GET request (verification)
echo "📋 Test 1: GET Request (Webhook Verification)"
echo "--------------------------------------------"
response=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL")
if [ "$response" = "200" ] || [ "$response" = "200" ]; then
    echo "✅ GET request successful (HTTP $response)"
    echo "   Webhook is accessible and responding!"
else
    echo "❌ GET request failed (HTTP $response)"
    echo "   Webhook may not be accessible"
fi
echo ""

# Test 2: POST request (actual webhook)
echo "📋 Test 2: POST Request (Webhook Message)"
echo "-----------------------------------------"
test_payload='{"type":"message","data":{"from":"60123456789","message":"TEST","id":"test_001","timestamp":"1640995200"}}'
response=$(curl -s -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -d "$test_payload" \
    -w "\nHTTP_CODE:%{http_code}")

http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')

if [ "$http_code" = "200" ]; then
    echo "✅ POST request successful (HTTP $http_code)"
    echo "   Response: $body"
else
    echo "❌ POST request failed (HTTP $http_code)"
    echo "   Response: $body"
fi
echo ""

# Test 3: Check if endpoint is reachable
echo "📋 Test 3: Endpoint Reachability"
echo "--------------------------------"
if curl -s --head --fail "$WEBHOOK_URL" > /dev/null 2>&1; then
    echo "✅ Endpoint is reachable"
else
    echo "❌ Endpoint is NOT reachable"
    echo "   Check your deployment and URL"
fi
echo ""

echo "📝 WABot Configuration:"
echo "   Webhook URL: $WEBHOOK_URL"
echo "   Method: POST (for messages)"
echo "   Method: GET (for verification)"
echo ""
echo "💡 If all tests pass, your webhook should work in WABot!"
echo "💡 If tests fail, check:"
echo "   1. App is deployed: gcloud app versions list"
echo "   2. URL is correct (no typos)"
echo "   3. App is running: gcloud app browse"

