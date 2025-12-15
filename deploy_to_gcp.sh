#!/bin/bash

###############################################################################
# Django App Engine Standard Deployment Script
# 
# This script automates the deployment of Django apps to Google App Engine
# Standard with Cloud SQL PostgreSQL database migration.
#
# Usage:
#   1. Run from LOCAL machine: gcloud app deploy --project=PROJECT_ID
#   2. Then run THIS script in Cloud Shell
#
# Prerequisites:
#   - App already deployed via gcloud app deploy
#   - Source code uploaded to Cloud Storage bucket
#   - Cloud SQL instance created and running
###############################################################################

set -e  # Exit on any error

# =============================================================================
# CONFIGURATION - EDIT THESE VALUES
# =============================================================================

PROJECT_ID="whatsapp-bulk-messaging-480620"
REGION="asia-southeast1"
INSTANCE_NAME="whatsapp-bulk-db"
DB_NAME="whatsapp_bulk"
DB_USER="whatsapp_user"
DB_PASSWORD="P@##w0rd"
GCS_BUCKET="staging.${PROJECT_ID}.appspot.com"
APP_DIR="$HOME/app-full"

# =============================================================================
# COLORS
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FUNCTIONS
# =============================================================================

print_header() {
    echo ""
    echo "======================================================================"
    echo -e "${BLUE}$1${NC}"
    echo "======================================================================"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

print_header "DJANGO APP ENGINE DEPLOYMENT & MIGRATION"

# -----------------------------------------------------------------------------
# Step 1: Clean previous deployment files
# -----------------------------------------------------------------------------

print_header "STEP 1: Cleaning Previous Files"

if [ -d "$APP_DIR" ]; then
    print_info "Removing old app directory..."
    rm -rf "$APP_DIR"
fi

mkdir -p "$APP_DIR"
cd "$APP_DIR"

print_success "Clean workspace ready"

# -----------------------------------------------------------------------------
# Step 2: Download source code from Cloud Storage
# -----------------------------------------------------------------------------

print_header "STEP 2: Downloading Source Code"

print_info "Syncing from gs://${GCS_BUCKET}/"

if gsutil -m rsync -r gs://${GCS_BUCKET}/ . 2>/dev/null; then
    print_success "Source code downloaded"
else
    print_warning "Direct sync failed, trying alternate method..."
    
    # Try downloading individual critical files
    gsutil cp gs://${GCS_BUCKET}/migrate_db.py . 2>/dev/null || print_warning "migrate_db.py not found"
    gsutil cp -r gs://${GCS_BUCKET}/messaging . 2>/dev/null || print_warning "messaging folder not found"
    gsutil cp gs://${GCS_BUCKET}/settings_production.py . 2>/dev/null || print_warning "settings_production.py not found"
fi

# Verify critical files exist
if [ ! -f "migrate_db.py" ]; then
    print_error "migrate_db.py not found! Cannot proceed."
    exit 1
fi

if [ ! -d "messaging" ]; then
    print_error "messaging app not found! Cannot proceed."
    exit 1
fi

print_success "Required files verified"

# -----------------------------------------------------------------------------
# Step 3: Install Python dependencies
# -----------------------------------------------------------------------------

print_header "STEP 3: Installing Dependencies"

print_info "Installing Django and PostgreSQL adapter..."

pip3 install --user --quiet django psycopg2-binary

print_success "Dependencies installed"

# -----------------------------------------------------------------------------
# Step 4: Start Cloud SQL Proxy
# -----------------------------------------------------------------------------

print_header "STEP 4: Starting Cloud SQL Proxy"

# Kill any existing proxy
pkill cloud-sql-proxy 2>/dev/null || true
sleep 2

print_info "Starting proxy for ${PROJECT_ID}:${REGION}:${INSTANCE_NAME}..."

cloud-sql-proxy ${PROJECT_ID}:${REGION}:${INSTANCE_NAME} --port=5432 &

PROXY_PID=$!
sleep 5

# Check if proxy is running
if ! ps -p $PROXY_PID > /dev/null; then
    print_error "Cloud SQL Proxy failed to start"
    exit 1
fi

print_success "Cloud SQL Proxy running (PID: $PROXY_PID)"

# -----------------------------------------------------------------------------
# Step 5: Run Database Migrations
# -----------------------------------------------------------------------------

print_header "STEP 5: Running Database Migrations"

print_info "Executing migrate_db.py..."

if python3 migrate_db.py; then
    print_success "Migrations completed successfully!"
else
    print_error "Migration failed!"
    print_warning "Stopping proxy..."
    kill $PROXY_PID 2>/dev/null || pkill cloud-sql-proxy
    exit 1
fi

# -----------------------------------------------------------------------------
# Step 6: Verify Database Tables
# -----------------------------------------------------------------------------

print_header "STEP 6: Verifying Database"

print_info "Checking database tables..."

python3 << EOF
import psycopg2

try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        database='${DB_NAME}',
        user='${DB_USER}',
        password='${DB_PASSWORD}'
    )
    cur = conn.cursor()
    
    # Count messaging tables
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'messaging_%';")
    count = cur.fetchone()[0]
    
    print(f"✅ Found {count} messaging tables")
    
    # Check for user
    cur.execute("SELECT username FROM auth_user WHERE username = 'tenant' LIMIT 1;")
    user = cur.fetchone()
    
    if user:
        print(f"✅ User 'tenant' exists")
    else:
        print(f"⚠️  User 'tenant' not found")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database check failed: {e}")
    exit(1)
EOF

# -----------------------------------------------------------------------------
# Step 7: Cleanup
# -----------------------------------------------------------------------------

print_header "STEP 7: Cleanup"

print_info "Stopping Cloud SQL Proxy..."
kill $PROXY_PID 2>/dev/null || pkill cloud-sql-proxy
sleep 2

print_success "Proxy stopped"

# -----------------------------------------------------------------------------
# Step 8: Deploy to App Engine
# -----------------------------------------------------------------------------

print_header "STEP 8: Deploying to App Engine"

print_info "This will deploy your updated code to production..."
echo ""
echo "The deployment includes:"
echo "  ✅ Keywords integrated into Contest model"
echo "  ✅ Updated contest creation form"
echo "  ✅ New database migrations"
echo ""

# Deploy to App Engine
if gcloud app deploy app.yaml --quiet --project=${PROJECT_ID}; then
    print_success "App Engine deployment completed!"
else
    print_error "App Engine deployment failed!"
    exit 1
fi

# -----------------------------------------------------------------------------
# DEPLOYMENT COMPLETE
# -----------------------------------------------------------------------------

print_header "🎉 DEPLOYMENT COMPLETE!"

echo ""
echo -e "${GREEN}Your application is now live!${NC}"
echo ""
echo "🔐 Login URL: https://${PROJECT_ID}.as.r.appspot.com/login/"
echo "   Username: tenant"
echo "   Password: Tenant123!"
echo ""
echo "📊 View logs: gcloud app logs read --limit=50 --project=${PROJECT_ID}"
echo "🌐 Browse app: gcloud app browse --project=${PROJECT_ID}"
echo ""
echo "======================================================================"

exit 0




