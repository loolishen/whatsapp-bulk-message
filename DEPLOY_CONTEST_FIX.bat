@echo off
REM Quick deployment script for contest dropdown fix
REM Run this from your LOCAL Windows machine (PowerShell)

set PROJECT_ID=whatsapp-bulk-messaging-480620
set BUCKET=staging.%PROJECT_ID%.appspot.com

echo.
echo 🚀 Deploying Contest Dropdown Fix
echo ==================================
echo.

REM Step 1: Upload files to Cloud Storage
echo 📤 Step 1: Uploading files to Cloud Storage...
echo.

echo   Uploading messaging/views.py...
gsutil cp messaging\views.py gs://%BUCKET%/messaging/views.py

echo   Uploading templates/messaging/participants_manager.html...
gsutil cp templates\messaging\participants_manager.html gs://%BUCKET%/templates/messaging/participants_manager.html

echo.
echo ✅ Files uploaded to Cloud Storage
echo.

echo.
echo 📋 Next Steps:
echo.
echo 1. Go to Google Cloud Shell
echo 2. Run this command:
echo    cd ~/app-full ^&^& gsutil cp gs://%BUCKET%/messaging/views.py messaging/views.py ^&^& gsutil cp gs://%BUCKET%/templates/messaging/participants_manager.html templates/messaging/participants_manager.html ^&^& gcloud app deploy app.yaml --quiet --project=%PROJECT_ID%
echo.
echo OR use the Cloud Shell script:
echo    gsutil cp gs://%BUCKET%/DEPLOY_CONTEST_FIX.sh . ^&^& chmod +x DEPLOY_CONTEST_FIX.sh ^&^& ./DEPLOY_CONTEST_FIX.sh
echo.

pause




REM Quick deployment script for contest dropdown fix
REM Run this from your LOCAL Windows machine (PowerShell)

set PROJECT_ID=whatsapp-bulk-messaging-480620
set BUCKET=staging.%PROJECT_ID%.appspot.com

echo.
echo 🚀 Deploying Contest Dropdown Fix
echo ==================================
echo.

REM Step 1: Upload files to Cloud Storage
echo 📤 Step 1: Uploading files to Cloud Storage...
echo.

echo   Uploading messaging/views.py...
gsutil cp messaging\views.py gs://%BUCKET%/messaging/views.py

echo   Uploading templates/messaging/participants_manager.html...
gsutil cp templates\messaging\participants_manager.html gs://%BUCKET%/templates/messaging/participants_manager.html

echo.
echo ✅ Files uploaded to Cloud Storage
echo.

echo.
echo 📋 Next Steps:
echo.
echo 1. Go to Google Cloud Shell
echo 2. Run this command:
echo    cd ~/app-full ^&^& gsutil cp gs://%BUCKET%/messaging/views.py messaging/views.py ^&^& gsutil cp gs://%BUCKET%/templates/messaging/participants_manager.html templates/messaging/participants_manager.html ^&^& gcloud app deploy app.yaml --quiet --project=%PROJECT_ID%
echo.
echo OR use the Cloud Shell script:
echo    gsutil cp gs://%BUCKET%/DEPLOY_CONTEST_FIX.sh . ^&^& chmod +x DEPLOY_CONTEST_FIX.sh ^&^& ./DEPLOY_CONTEST_FIX.sh
echo.

pause






