#!/bin/bash

# Setup script for Google Cloud Shell
# This script will prepare your environment for GCP deployment

echo "🚀 Setting up WhatsApp Bulk Messaging on Google Cloud Shell..."

# Set project ID
PROJECT_ID="whatsapp-bulk-messaging-473607"
echo "📋 Using project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create App Engine app (if not exists)
echo "🏗️  Setting up App Engine..."
gcloud app create --region=us-central --quiet || echo "App Engine app already exists"

# Clone the repository
echo "📥 Cloning repository..."
if [ ! -d "whatsapp-bulk-message" ]; then
    git clone https://github.com/loolishen/whatsapp-bulk-message.git
    cd whatsapp-bulk-message
else
    cd whatsapp-bulk-message
    git pull origin main
fi

# Verify app.yaml exists
if [ ! -f "app.yaml" ]; then
    echo "❌ app.yaml not found! Please make sure you're in the correct directory."
    exit 1
fi

echo "✅ app.yaml found!"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput --settings=whatsapp_bulk.settings_gcp

# Deploy to App Engine
echo "🚀 Deploying to App Engine..."
gcloud app deploy --quiet

# Get the app URL
APP_URL=$(gcloud app describe --format="value(defaultHostname)")
echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://$APP_URL"
echo "🔗 App Engine Console: https://console.cloud.google.com/appengine"

echo ""
echo "🎉 Setup complete! Your app is now deployed to GCP."
echo ""
echo "Next steps:"
echo "1. Set up Cloud SQL database"
echo "2. Configure environment variables in app.yaml"
echo "3. Set up Cloud Storage bucket for media files"
echo "4. Configure your WhatsApp API webhook URL"
echo "5. Test all functionality"
