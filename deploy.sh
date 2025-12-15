#!/bin/bash
# Deployment script with automatic migrations for GCP App Engine

set -e  # Exit on error

PROJECT_ID="whatsapp-bulk-messaging-480620"
CLOUD_SQL_CONNECTION="whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db"

echo "=========================================="
echo "DEPLOYING TO GCP APP ENGINE"
echo "=========================================="

# Step 1: Deploy the application
echo ""
echo "Step 1: Deploying application..."
gcloud app deploy app.yaml --project=$PROJECT_ID --promote --quiet

# Wait for deployment to stabilize
echo ""
echo "Waiting for deployment to stabilize..."
sleep 10

# Step 2: Run migrations via Cloud Shell or Cloud Build
echo ""
echo "Step 2: Running database migrations..."
echo ""
echo "To run migrations, execute this in Cloud Shell:"
echo ""
echo "  cloud-sql-proxy $CLOUD_SQL_CONNECTION --port=5432 &"
echo "  sleep 3"
echo "  python3 migrate_db.py"
echo "  pkill cloud-sql-proxy"
echo ""
echo "Or deploy with Cloud Build:"
echo "  gcloud builds submit --config=cloudbuild.yaml ."
echo ""

echo "=========================================="
echo "✅ DEPLOYMENT COMPLETED!"
echo "=========================================="
echo ""
echo "🌐 Application URL:"
echo "   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/"
echo ""
echo "📋 Next steps:"
echo "   1. Run migrations (see commands above)"
echo "   2. Login with: tenant / Tenant123!"
echo ""
echo "=========================================="






