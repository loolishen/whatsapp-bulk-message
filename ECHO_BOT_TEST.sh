#!/bin/bash
# =============================================================================
# ECHO BOT TEST - Verify WABot Send Message API
# =============================================================================

echo "🧪 TESTING WABOT SEND MESSAGE API"
echo "===================================="
echo ""

# Test 1: Verify WhatsApp service is importable
echo "📋 Test 1: Check WhatsApp Service"
echo "-----------------------------------"
cd ~/app-full
python3 << 'EOF'
try:
    from messaging.whatsapp_service import WhatsAppAPIService
    service = WhatsAppAPIService()
    print(f"✅ Service loaded")
    print(f"   Instance ID: {service.instance_id}")
    print(f"   API URL: {service.base_url}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)
EOF

echo ""
echo "📋 Test 2: Send Test Message via WABot API"
echo "-------------------------------------------"
python3 test_wabot_send.py

echo ""
echo "📋 Test 3: Monitor Logs for Send Attempts"
echo "-------------------------------------------"
echo "Run this command to see if messages are being sent:"
echo ""
echo "  gcloud app logs tail -s default --project=whatsapp-bulk-messaging-480620 | grep -i 'send\|whatsapp\|message'"
echo ""
echo "📱 Now send a WhatsApp message to 60162107682 and watch the logs!"

