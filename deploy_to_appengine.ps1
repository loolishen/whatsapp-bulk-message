# Automated App Engine Deployment Script (PowerShell)
# This script deploys your WhatsApp Bulk Message application to Google App Engine
#
# Usage: .\deploy_to_appengine.ps1 [-NoBackup] [-NoMigration] [-Quick]
#

param(
    [switch]$NoBackup,
    [switch]$NoMigration,
    [switch]$Quick
)

# Configuration
$PROJECT_ID = "whatsapp-bulk-messaging-480620"
$BUCKET_NAME = "staging.$PROJECT_ID.appspot.com"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

# Apply Quick flag
if ($Quick) {
    $NoBackup = $true
    $NoMigration = $true
}

# Helper functions
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Main deployment process
Write-Header "🚀 Starting Deployment to App Engine"

# Step 1: Check if we're in the right directory
Write-Header "📁 Step 1: Validating current directory"
if (-not (Test-Path "app.yaml")) {
    Write-ErrorMsg "app.yaml not found in current directory!"
    Write-Host "Please run this script from your project root directory."
    exit 1
}
Write-Success "Found app.yaml in current directory"

# Step 2: Backup current version (optional)
if (-not $NoBackup) {
    Write-Header "💾 Step 2: Backing up current version"
    Write-Host "Creating backup snapshot in Cloud Storage..."
    
    try {
        gsutil -m cp -r `
            messaging/*.py `
            templates/messaging/*.html `
            app.yaml `
            gs://$BUCKET_NAME/backups/$TIMESTAMP/ 2>$null
        
        Write-Success "Backup saved to: gs://$BUCKET_NAME/backups/$TIMESTAMP/"
    }
    catch {
        Write-Warning "Backup failed, but continuing..."
    }
}
else {
    Write-Warning "Skipping backup step"
}

# Step 3: Check for migration files
if (-not $NoMigration) {
    Write-Header "🗄️  Step 3: Checking database migrations"
    
    if (Test-Path "messaging/migrations") {
        $MigrationCount = (Get-ChildItem "messaging/migrations" -Filter "*.py" | 
                          Where-Object { $_.Name -ne "__init__.py" }).Count
        Write-Host "Found $MigrationCount migration files"
        
        Write-Warning "Remember to run migrations after deployment:"
        Write-Host "  python manage.py migrate"
    }
}
else {
    Write-Warning "Skipping migration check"
}

# Step 4: Validate critical files
Write-Header "✅ Step 4: Validating deployment files"

$CriticalFiles = @(
    "app.yaml",
    "manage.py",
    "messaging\models.py",
    "messaging\views.py",
    "messaging\whatsapp_webhook.py",
    "messaging\conversation_flow_service.py"
)

$AllFilesExist = $true
foreach ($File in $CriticalFiles) {
    if (Test-Path $File) {
        Write-Success "Found: $File"
    }
    else {
        Write-ErrorMsg "Missing critical file: $File"
        $AllFilesExist = $false
    }
}

if (-not $AllFilesExist) {
    Write-ErrorMsg "Some critical files are missing. Aborting deployment."
    exit 1
}

# Step 5: Deploy to App Engine
Write-Header "🚀 Step 5: Deploying to App Engine"
Write-Host "Starting deployment to project: $PROJECT_ID"
Write-Host "This may take 5-10 minutes..."
Write-Host ""

$DeployVersion = Get-Date -Format "yyyyMMdd-t-HHmmss"

try {
    gcloud app deploy app.yaml `
        --quiet `
        --project="$PROJECT_ID" `
        --version=$DeployVersion
    
    Write-Success "Deployment completed successfully!"
}
catch {
    Write-ErrorMsg "Deployment failed!"
    Write-Host $_.Exception.Message
    exit 1
}

# Step 6: Verify deployment
Write-Header "🔍 Step 6: Verifying deployment"
$AppURL = "https://$PROJECT_ID.as.r.appspot.com"
Write-Host "Application URL: $AppURL"
Write-Host ""

Write-Success "Fetching latest logs to verify..."
Start-Sleep -Seconds 5

try {
    gcloud app logs read `
        --limit=10 `
        --project="$PROJECT_ID" `
        --format="table(timestamp,severity,textPayload)"
}
catch {
    Write-Warning "Could not fetch logs, but deployment may still be successful"
}

# Step 7: Migration reminder
if (-not $NoMigration) {
    Write-Header "📋 Step 7: Post-Deployment Tasks"
    Write-Host ""
    Write-Host "If you added new models or database changes, run migrations:"
    Write-Host ""
    Write-Host "  1. Connect to Cloud SQL:"
    Write-Host "     cloud_sql_proxy -instances=whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-db=tcp:5432"
    Write-Host ""
    Write-Host "  2. Run migrations:"
    Write-Host "     python manage.py migrate"
    Write-Host ""
}

# Final summary
Write-Header "🎉 Deployment Summary"
Write-Host "Project: $PROJECT_ID"
Write-Host "Version: $DeployVersion"
Write-Host "Timestamp: $TIMESTAMP"
Write-Host "URL: $AppURL"
Write-Host ""
Write-Success "Deployment completed successfully!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Test your application at: $AppURL"
Write-Host "  2. Monitor logs: gcloud app logs tail -s default"
Write-Host "  3. Check App Engine dashboard: https://console.cloud.google.com/appengine?project=$PROJECT_ID"
Write-Host ""

