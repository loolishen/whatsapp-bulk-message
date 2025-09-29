@echo off
REM GCP Deployment Script for WhatsApp Bulk Messaging App
REM Make sure you have gcloud CLI installed and authenticated

echo 🚀 Starting GCP deployment process...

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Google Cloud CLI is not installed. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Check if user is authenticated
gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Please authenticate with Google Cloud first:
    echo Run: gcloud auth login
    pause
    exit /b 1
)

REM Set project ID (replace with your project ID)
set PROJECT_ID=your-project-id
echo 📋 Using project: %PROJECT_ID%

REM Set the project
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs...
gcloud services enable appengine.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable secretmanager.googleapis.com

REM Create App Engine app (if not exists)
echo 🏗️  Setting up App Engine...
gcloud app create --region=us-central --quiet
if %ERRORLEVEL% NEQ 0 (
    echo App Engine app already exists
)

REM Collect static files
echo 📦 Collecting static files...
python manage.py collectstatic --noinput --settings=whatsapp_bulk.settings_gcp

REM Run database migrations
echo 🗄️  Running database migrations...
python manage.py migrate --settings=whatsapp_bulk.settings_gcp

REM Deploy to App Engine
echo 🚀 Deploying to App Engine...
gcloud app deploy --quiet

REM Get the app URL
for /f "tokens=*" %%i in ('gcloud app describe --format="value(defaultHostname)"') do set APP_URL=%%i
echo ✅ Deployment complete!
echo 🌐 Your app is available at: https://%APP_URL%
echo 🔗 App Engine Console: https://console.cloud.google.com/appengine

REM Optional: Open the app in browser
set /p choice="Would you like to open the app in your browser? (y/n): "
if /i "%choice%"=="y" (
    gcloud app browse
)

echo 🎉 Deployment finished successfully!
echo.
echo Next steps:
echo 1. Set up Cloud SQL database
echo 2. Configure environment variables in app.yaml
echo 3. Set up Cloud Storage bucket for media files
echo 4. Configure your WhatsApp API webhook URL
echo 5. Test all functionality
pause
