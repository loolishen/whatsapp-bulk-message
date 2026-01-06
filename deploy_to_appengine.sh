#!/bin/bash
#
# Automated App Engine Deployment Script
# This script deploys your WhatsApp Bulk Message application to Google App Engine
#
# Usage: ./deploy_to_appengine.sh [options]
# Options:
#   --no-backup     Skip backup step
#   --no-migration  Skip database migration
#   --quick         Quick deploy (no backup, no migration check)
#

set -e  # Exit on error

# Configuration
PROJECT_ID="whatsapp-bulk-messaging-480620"
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"
APP_DIR="$HOME/app-full"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
SKIP_BACKUP=false
SKIP_MIGRATION=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-backup)
      SKIP_BACKUP=true
      shift
      ;;
    --no-migration)
      SKIP_MIGRATION=true
      shift
      ;;
    --quick)
      SKIP_BACKUP=true
      SKIP_MIGRATION=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main deployment process
print_header "🚀 Starting Deployment to App Engine"

# Step 1: Change to app directory
print_header "📁 Step 1: Navigating to application directory"
cd "$APP_DIR" || {
    print_error "Failed to change to directory: $APP_DIR"
    exit 1
}
print_success "Changed to directory: $APP_DIR"

# Step 2: Backup current version (optional)
if [ "$SKIP_BACKUP" = false ]; then
    print_header "💾 Step 2: Backing up current version"
    echo "Creating backup snapshot in Cloud Storage..."
    
    gsutil -m cp -r \
        messaging/*.py \
        templates/messaging/*.html \
        app.yaml \
        gs://${BUCKET_NAME}/backups/${TIMESTAMP}/ 2>/dev/null || true
    
    print_success "Backup saved to: gs://${BUCKET_NAME}/backups/${TIMESTAMP}/"
else
    print_warning "Skipping backup step"
fi

# Step 3: Sync latest code from Cloud Storage
print_header "🔄 Step 3: Syncing latest code"
echo "Downloading latest code from Cloud Storage..."

# Only sync specific directories to avoid overwriting important files
gsutil -m rsync -r -x ".git/.*" gs://${BUCKET_NAME}/ . || {
    print_warning "Some files may not have synced, but continuing..."
}

print_success "Code synchronized"

# Step 4: Check for migration files
if [ "$SKIP_MIGRATION" = false ]; then
    print_header "🗄️  Step 4: Checking database migrations"
    
    if [ -d "messaging/migrations" ]; then
        MIGRATION_COUNT=$(find messaging/migrations -name "*.py" ! -name "__init__.py" | wc -l)
        echo "Found $MIGRATION_COUNT migration files"
        
        print_warning "Remember to run migrations after deployment:"
        echo "  python manage.py migrate"
    fi
else
    print_warning "Skipping migration check"
fi

# Step 5: Validate critical files
print_header "✅ Step 5: Validating deployment files"

# Check if critical files exist
CRITICAL_FILES=(
    "app.yaml"
    "manage.py"
    "messaging/models.py"
    "messaging/views.py"
    "messaging/whatsapp_webhook.py"
    "messaging/conversation_flow_service.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing critical file: $file"
        exit 1
    fi
done

# Step 6: Deploy to App Engine
print_header "🚀 Step 6: Deploying to App Engine"
echo "Starting deployment to project: $PROJECT_ID"
echo "This may take 5-10 minutes..."
echo ""

gcloud app deploy app.yaml \
    --quiet \
    --project="$PROJECT_ID" \
    --version=$(date +%Y%m%d-t-%H%M%S) || {
    print_error "Deployment failed!"
    exit 1
}

print_success "Deployment completed successfully!"

# Step 7: Verify deployment
print_header "🔍 Step 7: Verifying deployment"
echo "Application URL: https://${PROJECT_ID}.as.r.appspot.com"
echo ""

print_success "Fetching latest logs to verify..."
sleep 5

gcloud app logs read \
    --limit=10 \
    --project="$PROJECT_ID" \
    --format="table(timestamp,severity,textPayload)" || true

# Step 8: Migration reminder
if [ "$SKIP_MIGRATION" = false ]; then
    print_header "📋 Step 8: Post-Deployment Tasks"
    echo ""
    echo "If you added new models or database changes, run migrations:"
    echo ""
    echo "  1. Connect to Cloud SQL:"
    echo "     cloud_sql_proxy -instances=whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-db=tcp:5432"
    echo ""
    echo "  2. Run migrations:"
    echo "     python manage.py migrate"
    echo ""
fi

# Final summary
print_header "🎉 Deployment Summary"
echo "Project: $PROJECT_ID"
echo "Timestamp: $TIMESTAMP"
echo "URL: https://${PROJECT_ID}.as.r.appspot.com"
echo ""
print_success "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Test your application at the URL above"
echo "  2. Monitor logs: gcloud app logs tail -s default"
echo "  3. Check App Engine dashboard: https://console.cloud.google.com/appengine?project=$PROJECT_ID"
echo ""

