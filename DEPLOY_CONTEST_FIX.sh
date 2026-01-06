#!/bin/bash
# Quick deployment script for contest dropdown fix
# Run this in Google Cloud Shell

set -e

PROJECT_ID="whatsapp-bulk-messaging-480620"
BUCKET="staging.${PROJECT_ID}.appspot.com"

echo "🚀 Deploying Contest Dropdown Fix"
echo "=================================="
echo ""

# Step 1: Upload files to Cloud Storage
echo "📤 Step 1: Uploading files to Cloud Storage..."
echo ""

# Upload views.py
echo "  Uploading messaging/views.py..."
gsutil cp messaging/views.py gs://${BUCKET}/messaging/views.py

# Upload template
echo "  Uploading templates/messaging/participants_manager.html..."
gsutil cp templates/messaging/participants_manager.html gs://${BUCKET}/templates/messaging/participants_manager.html

echo ""
echo "✅ Files uploaded to Cloud Storage"
echo ""

# Step 2: Download to Cloud Shell workspace
echo "📥 Step 2: Downloading to Cloud Shell workspace..."
echo ""

cd ~/app-full 2>/dev/null || mkdir -p ~/app-full && cd ~/app-full

# Download the files we just uploaded
gsutil cp gs://${BUCKET}/messaging/views.py messaging/views.py
gsutil cp gs://${BUCKET}/templates/messaging/participants_manager.html templates/messaging/participants_manager.html

echo "✅ Files downloaded to Cloud Shell"
echo ""

# Step 3: Deploy to App Engine
echo "🚀 Step 3: Deploying to App Engine..."
echo ""

gcloud app deploy app.yaml --quiet --project=${PROJECT_ID}

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your site: https://${PROJECT_ID}.as.r.appspot.com"
echo ""
echo "📋 Changes deployed:"
echo "  ✓ Updated participants_manager view with contest dropdown fix"
echo "  ✓ Added fallback mechanism for contests loading"
echo "  ✓ Added debug logging"
echo "  ✓ Updated template with debug comment"
echo ""
echo "🔍 To verify:"
echo "  1. Visit: https://${PROJECT_ID}.as.r.appspot.com/participants/"
echo "  2. Check the Contest dropdown - should show all 7 contests"
echo "  3. View page source (Ctrl+U) and search for 'Debug: contests count'"
echo ""
echo "📊 View logs:"
echo "  gcloud app logs read --limit=50 --project=${PROJECT_ID} | grep -i contest"




# Quick deployment script for contest dropdown fix
# Run this in Google Cloud Shell

set -e

PROJECT_ID="whatsapp-bulk-messaging-480620"
BUCKET="staging.${PROJECT_ID}.appspot.com"

echo "🚀 Deploying Contest Dropdown Fix"
echo "=================================="
echo ""

# Step 1: Upload files to Cloud Storage
echo "📤 Step 1: Uploading files to Cloud Storage..."
echo ""

# Upload views.py
echo "  Uploading messaging/views.py..."
gsutil cp messaging/views.py gs://${BUCKET}/messaging/views.py

# Upload template
echo "  Uploading templates/messaging/participants_manager.html..."
gsutil cp templates/messaging/participants_manager.html gs://${BUCKET}/templates/messaging/participants_manager.html

echo ""
echo "✅ Files uploaded to Cloud Storage"
echo ""

# Step 2: Download to Cloud Shell workspace
echo "📥 Step 2: Downloading to Cloud Shell workspace..."
echo ""

cd ~/app-full 2>/dev/null || mkdir -p ~/app-full && cd ~/app-full

# Download the files we just uploaded
gsutil cp gs://${BUCKET}/messaging/views.py messaging/views.py
gsutil cp gs://${BUCKET}/templates/messaging/participants_manager.html templates/messaging/participants_manager.html

echo "✅ Files downloaded to Cloud Shell"
echo ""

# Step 3: Deploy to App Engine
echo "🚀 Step 3: Deploying to App Engine..."
echo ""

gcloud app deploy app.yaml --quiet --project=${PROJECT_ID}

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your site: https://${PROJECT_ID}.as.r.appspot.com"
echo ""
echo "📋 Changes deployed:"
echo "  ✓ Updated participants_manager view with contest dropdown fix"
echo "  ✓ Added fallback mechanism for contests loading"
echo "  ✓ Added debug logging"
echo "  ✓ Updated template with debug comment"
echo ""
echo "🔍 To verify:"
echo "  1. Visit: https://${PROJECT_ID}.as.r.appspot.com/participants/"
echo "  2. Check the Contest dropdown - should show all 7 contests"
echo "  3. View page source (Ctrl+U) and search for 'Debug: contests count'"
echo ""
echo "📊 View logs:"
echo "  gcloud app logs read --limit=50 --project=${PROJECT_ID} | grep -i contest"






