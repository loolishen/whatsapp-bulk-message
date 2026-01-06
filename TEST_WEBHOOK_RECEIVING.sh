#!/bin/bash
# =============================================================================
# TEST IF WEBHOOK IS RECEIVING MESSAGES
# Run this to check if webhook is working
# =============================================================================

echo "🔍 Testing Webhook Reception"
echo "============================"
echo ""

# Check recent webhook logs
echo "📋 Checking last 50 logs for webhook activity..."
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|wabot\|message" | head -20

echo ""
echo "📋 If you see 'Received WABOT webhook data' above, webhook is working!"
echo "📋 If you see nothing, webhook is NOT receiving messages."
echo ""
echo "🔧 WABot Configuration Checklist:"
echo "  1. Webhook URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"
echo "  2. Event Type: 'message' should be enabled"
echo "  3. Webhook Status: Should be 'Active' or 'Enabled'"
echo ""
echo "💡 In WABot Dashboard:"
echo "  - Go to: Settings → Webhook"
echo "  - Make sure 'Forward Data to Webhook' is ON"
echo "  - Make sure 'message' event is enabled"
echo "  - Test webhook button should work"




# =============================================================================
# TEST IF WEBHOOK IS RECEIVING MESSAGES
# Run this to check if webhook is working
# =============================================================================

echo "🔍 Testing Webhook Reception"
echo "============================"
echo ""

# Check recent webhook logs
echo "📋 Checking last 50 logs for webhook activity..."
gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "webhook\|wabot\|message" | head -20

echo ""
echo "📋 If you see 'Received WABOT webhook data' above, webhook is working!"
echo "📋 If you see nothing, webhook is NOT receiving messages."
echo ""
echo "🔧 WABot Configuration Checklist:"
echo "  1. Webhook URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"
echo "  2. Event Type: 'message' should be enabled"
echo "  3. Webhook Status: Should be 'Active' or 'Enabled'"
echo ""
echo "💡 In WABot Dashboard:"
echo "  - Go to: Settings → Webhook"
echo "  - Make sure 'Forward Data to Webhook' is ON"
echo "  - Make sure 'message' event is enabled"
echo "  - Test webhook button should work"






