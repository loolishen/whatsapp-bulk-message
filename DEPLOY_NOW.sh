#!/bin/bash
# Deploy DeepSeek OCR fixes to App Engine
# Run this in Cloud Shell

set -e

echo "🚀 Deploying DeepSeek OCR Integration"
echo "======================================"

cd ~/app-full

# Download all fixed files from staging
echo "📥 Downloading fixed files..."
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/app.yaml .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/requirements.txt .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/wsgi.py .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/deepseek_ocr_wrapper.py messaging/
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/receipt_ocr_service.py messaging/

echo "✅ Files downloaded"

# Deploy to App Engine
echo ""
echo "🚀 Deploying to App Engine..."
gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your site: https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
echo ""
echo "📋 Changes deployed:"
echo "  ✓ Removed PaddleOCR (no more 'model connectivity' hangs)"
echo "  ✓ Added DeepSeek Vision API for OCR"
echo "  ✓ Added your DeepSeek API key"
echo "  ✓ Fixed CSV warnings"
echo ""
echo "Monitor logs with:"
echo "  gcloud app logs tail -s default"

