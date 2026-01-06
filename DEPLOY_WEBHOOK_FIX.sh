#!/bin/bash
# =============================================================================
# DEPLOY WEBHOOK FIX FOR WABOT VERIFICATION
# This deploys the updated webhook handler that supports WABot verification
# =============================================================================

echo "🚀 Deploying Webhook Fix"
echo "======================="
echo ""

# Upload the updated webhook file
echo "📤 Uploading updated webhook handler..."
gsutil cp messaging/whatsapp_webhook.py gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/

# Deploy to App Engine
echo "🚀 Deploying to App Engine..."
gcloud app deploy app.yaml --project=whatsapp-bulk-messaging-480620 --quiet

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Wait 1-2 minutes for deployment to complete"
echo "  2. Test webhook: bash TEST_WEBHOOK_ACCESS.sh"
echo "  3. Try setting webhook URL in WABot again"
echo "  4. URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/"

