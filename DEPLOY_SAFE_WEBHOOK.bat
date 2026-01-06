@echo off
REM =============================================================================
REM DEPLOY ULTRA-SAFE WEBHOOK (Always returns 200)
REM This version will never crash - always returns 200 OK
REM =============================================================================

echo.
echo =============================================================================
echo DEPLOYING ULTRA-SAFE WEBHOOK
echo =============================================================================
echo.

set pwd=%CD%

echo [1/2] Uploading whatsapp_webhook.py to Cloud Storage...
gsutil cp "file:///%pwd%/messaging/whatsapp_webhook.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload file
    pause
    exit /b 1
)

echo.
echo [2/2] File uploaded successfully!
echo.
echo Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo KEY CHANGES:
echo =============================================================================
echo 1. Webhook ALWAYS returns 200 OK (never crashes)
echo 2. Minimal logging (print to stderr)
echo 3. All processing wrapped in try-except
echo 4. Lazy imports for heavy services
echo.
echo After deployment, test with:
echo    curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ -H "Content-Type: application/json" -d "{\"type\":\"message\",\"data\":{\"from\":\"60123456789\",\"message\":\"TEST\",\"id\":\"test123\",\"timestamp\":\"123\"}}"
echo.
echo Check logs:
echo    gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 ^| grep -i "WEBHOOK\|🔥\|✅"
echo.
pause




REM =============================================================================
REM DEPLOY ULTRA-SAFE WEBHOOK (Always returns 200)
REM This version will never crash - always returns 200 OK
REM =============================================================================

echo.
echo =============================================================================
echo DEPLOYING ULTRA-SAFE WEBHOOK
echo =============================================================================
echo.

set pwd=%CD%

echo [1/2] Uploading whatsapp_webhook.py to Cloud Storage...
gsutil cp "file:///%pwd%/messaging/whatsapp_webhook.py" gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to upload file
    pause
    exit /b 1
)

echo.
echo [2/2] File uploaded successfully!
echo.
echo Now run these commands in Cloud Shell:
echo.
echo    cd ~/app-full
echo    gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/whatsapp_webhook.py messaging/whatsapp_webhook.py
echo    gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620
echo.
echo =============================================================================
echo KEY CHANGES:
echo =============================================================================
echo 1. Webhook ALWAYS returns 200 OK (never crashes)
echo 2. Minimal logging (print to stderr)
echo 3. All processing wrapped in try-except
echo 4. Lazy imports for heavy services
echo.
echo After deployment, test with:
echo    curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ -H "Content-Type: application/json" -d "{\"type\":\"message\",\"data\":{\"from\":\"60123456789\",\"message\":\"TEST\",\"id\":\"test123\",\"timestamp\":\"123\"}}"
echo.
echo Check logs:
echo    gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 ^| grep -i "WEBHOOK\|🔥\|✅"
echo.
pause






