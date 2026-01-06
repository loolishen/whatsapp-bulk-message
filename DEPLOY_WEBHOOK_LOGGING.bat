@echo off
REM =============================================================================
REM DEPLOY WEBHOOK LOGGING FIX
REM This deploys the enhanced webhook logging to help diagnose WABot issues
REM =============================================================================

echo.
echo =============================================================================
echo DEPLOYING WEBHOOK LOGGING FIX
echo =============================================================================
echo.

REM Get current directory
set pwd=%CD%

echo [1/3] Uploading whatsapp_webhook.py to Cloud Storage...
gsutil cp "file:///%pwd%/messaging/whatsapp_webhook.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload file to Cloud Storage
    echo Please check your gsutil configuration and try again.
    pause
    exit /b 1
)

echo.
echo [2/3] File uploaded successfully!
echo.
echo [3/3] Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo DEPLOYMENT READY
echo =============================================================================
echo.
echo After deployment, test with:
echo   1. Send a "TEST" message to your WhatsApp number
echo   2. Check logs: gcloud app logs read --limit=100 --project=whatsapp-bulk-messaging-480620 ^| grep -i "webhook"
echo.
pause




REM =============================================================================
REM DEPLOY WEBHOOK LOGGING FIX
REM This deploys the enhanced webhook logging to help diagnose WABot issues
REM =============================================================================

echo.
echo =============================================================================
echo DEPLOYING WEBHOOK LOGGING FIX
echo =============================================================================
echo.

REM Get current directory
set pwd=%CD%

echo [1/3] Uploading whatsapp_webhook.py to Cloud Storage...
gsutil cp "file:///%pwd%/messaging/whatsapp_webhook.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload file to Cloud Storage
    echo Please check your gsutil configuration and try again.
    pause
    exit /b 1
)

echo.
echo [2/3] File uploaded successfully!
echo.
echo [3/3] Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo DEPLOYMENT READY
echo =============================================================================
echo.
echo After deployment, test with:
echo   1. Send a "TEST" message to your WhatsApp number
echo   2. Check logs: gcloud app logs read --limit=100 --project=whatsapp-bulk-messaging-480620 ^| grep -i "webhook"
echo.
pause






