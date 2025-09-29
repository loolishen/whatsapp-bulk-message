#!/bin/bash

# GCP Deployment Script for WhatsApp Bulk Messaging App
# Make sure you have gcloud CLI installed and authenticated

echo "🚀 Starting GCP deployment process..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Please authenticate with Google Cloud first:"
    echo "Run: gcloud auth login"
    exit 1
fi

# Set project ID (replace with your project ID)
PROJECT_ID="your-project-id"
echo "📋 Using project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create App Engine app (if not exists)
echo "🏗️  Setting up App Engine..."
gcloud app create --region=us-central --quiet || echo "App Engine app already exists"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --settings=whatsapp_bulk.settings_gcp

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --settings=whatsapp_bulk.settings_gcp

# Deploy to App Engine
echo "🚀 Deploying to App Engine..."
gcloud app deploy --quiet

# Get the app URL
APP_URL=$(gcloud app describe --format="value(defaultHostname)")
echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://$APP_URL"
echo "🔗 App Engine Console: https://console.cloud.google.com/appengine"

# Optional: Open the app in browser
read -p "Would you like to open the app in your browser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    gcloud app browse
fi

echo "🎉 Deployment finished successfully!"
echo ""
echo "Next steps:"
echo "1. Set up Cloud SQL database"
echo "2. Configure environment variables in app.yaml"
echo "3. Set up Cloud Storage bucket for media files"
echo "4. Configure your WhatsApp API webhook URL"
echo "5. Test all functionality"
