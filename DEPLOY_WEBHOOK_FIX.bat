@echo off
REM =============================================================================
REM DEPLOY WEBHOOK LOGGING FIX
REM This deploys the enhanced webhook logging with print statements
REM =============================================================================

echo.
echo =============================================================================
echo DEPLOYING WEBHOOK LOGGING FIX
echo =============================================================================
echo.

REM Get current directory
set pwd=%CD%

echo [1/4] Uploading whatsapp_webhook.py to Cloud Storage...
gsutil cp "file:///%pwd%/messaging/whatsapp_webhook.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload whatsapp_webhook.py
    pause
    exit /b 1
)

echo [2/4] Uploading settings_production.py to Cloud Storage...
gsutil cp "file:///%pwd%/settings_production.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/settings_production.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload settings_production.py
    pause
    exit /b 1
)

echo.
echo [3/4] Files uploaded successfully!
echo.
echo [4/4] Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/settings_production.py settings_production.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo DEPLOYMENT READY
echo =============================================================================
echo.
echo After deployment, test with:
echo   1. Send a test POST: curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ -H "Content-Type: application/json" -d "{\"type\":\"message\",\"data\":{\"from\":\"60123456789\",\"message\":\"TEST\",\"id\":\"test123\",\"timestamp\":\"123\"}}"
echo   2. Check logs: gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 ^| grep -i "WEBHOOK"
echo.
pause

    echo.
    echo ERROR: Failed to upload settings_production.py
    pause
    exit /b 1
)

echo.
echo [3/4] Files uploaded successfully!
echo.
echo [4/4] Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/settings_production.py settings_production.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo DEPLOYMENT READY
echo =============================================================================
echo.
echo After deployment, test with:
echo   1. Send a test POST: curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ -H "Content-Type: application/json" -d "{\"type\":\"message\",\"data\":{\"from\":\"60123456789\",\"message\":\"TEST\",\"id\":\"test123\",\"timestamp\":\"123\"}}"
echo   2. Check logs: gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 ^| grep -i "WEBHOOK"
echo.
pause
