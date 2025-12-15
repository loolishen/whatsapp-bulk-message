@echo off
REM ============================================================================
REM Local Windows Deployment Script for Google App Engine
REM 
REM This script deploys your Django app from Windows and uploads source code
REM to Cloud Storage for use by the Cloud Shell migration script.
REM
REM Usage: deploy_local.bat
REM ============================================================================

setlocal enabledelayedexpansion

REM ============================================================================
REM CONFIGURATION - EDIT THESE VALUES
REM ============================================================================

set PROJECT_ID=whatsapp-bulk-messaging-480620
set GCS_BUCKET=staging.%PROJECT_ID%.appspot.com

REM ============================================================================
REM COLORS (Windows 10+)
REM ============================================================================

REM ANSI colors don't work well in Windows CMD, so we'll use simple text

REM ============================================================================
REM FUNCTIONS
REM ============================================================================

goto :MAIN

:print_header
echo.
echo ======================================================================
echo %~1
echo ======================================================================
goto :eof

:print_success
echo [OK] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

:print_info
echo [INFO] %~1
goto :eof

:print_warning
echo [WARN] %~1
goto :eof

REM ============================================================================
REM MAIN SCRIPT
REM ============================================================================

:MAIN

call :print_header "DJANGO APP ENGINE - LOCAL DEPLOYMENT"

REM ----------------------------------------------------------------------------
REM Step 1: Verify gcloud is installed
REM ----------------------------------------------------------------------------

call :print_header "STEP 1: Verifying gcloud CLI"

where gcloud >nul 2>nul
if %errorlevel% neq 0 (
    call :print_error "gcloud CLI not found! Please install Google Cloud SDK."
    echo.
    echo Download from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

call :print_success "gcloud CLI found"

REM ----------------------------------------------------------------------------
REM Step 2: Verify app.yaml exists
REM ----------------------------------------------------------------------------

call :print_header "STEP 2: Checking Configuration"

if not exist "app.yaml" (
    call :print_error "app.yaml not found in current directory!"
    echo.
    echo Please run this script from your project root directory.
    pause
    exit /b 1
)

call :print_success "app.yaml found"

if not exist "main.py" (
    call :print_error "main.py not found! App Engine won't know how to start your app."
    pause
    exit /b 1
)

call :print_success "main.py found"

if not exist "requirements.txt" (
    call :print_warning "requirements.txt not found!"
)

REM ----------------------------------------------------------------------------
REM Step 3: Upload source code to Cloud Storage
REM ----------------------------------------------------------------------------

call :print_header "STEP 3: Uploading Source Code to Cloud Storage"

call :print_info "Uploading to gs://%GCS_BUCKET%/"

REM Use .gcloudignore for exclusions instead of -x flag
gsutil -m rsync -r -d . gs://%GCS_BUCKET%/

if %errorlevel% neq 0 (
    call :print_error "Failed to upload source code to Cloud Storage"
    pause
    exit /b 1
)

call :print_success "Source code uploaded"

REM ----------------------------------------------------------------------------
REM Step 4: Deploy to App Engine
REM ----------------------------------------------------------------------------

call :print_header "STEP 4: Deploying to App Engine"

call :print_info "Deploying to project: %PROJECT_ID%"
echo.
echo This may take several minutes...
echo.

gcloud app deploy --project=%PROJECT_ID% --quiet

if %errorlevel% neq 0 (
    call :print_error "Deployment failed!"
    pause
    exit /b 1
)

call :print_success "Deployment completed!"

REM ----------------------------------------------------------------------------
REM Step 5: Instructions for Cloud Shell
REM ----------------------------------------------------------------------------

call :print_header "STEP 5: Next Steps - Run in Cloud Shell"

echo.
echo Your app is deployed, but you need to run database migrations!
echo.
echo Open Google Cloud Shell and run:
echo.
echo   wget https://raw.githubusercontent.com/YOUR_REPO/deploy_to_gcp.sh
echo   chmod +x deploy_to_gcp.sh
echo   ./deploy_to_gcp.sh
echo.
echo OR manually run:
echo.
echo   cd ~/ ^&^& rm -rf app-full ^&^& mkdir app-full ^&^& cd app-full
echo   gsutil -m rsync -r gs://%GCS_BUCKET%/ .
echo   cloud-sql-proxy %PROJECT_ID%:asia-southeast1:whatsapp-bulk-db --port=5432 ^&
echo   sleep 5
echo   pip3 install --user django psycopg2-binary
echo   python3 migrate_db.py
echo   pkill cloud-sql-proxy
echo.

REM ----------------------------------------------------------------------------
REM DEPLOYMENT COMPLETE
REM ----------------------------------------------------------------------------

call :print_header "LOCAL DEPLOYMENT COMPLETE!"

echo.
echo [OK] App deployed to: https://%PROJECT_ID%.as.r.appspot.com
echo.
echo Next: Run database migrations in Cloud Shell (see instructions above)
echo.
echo ======================================================================
echo.

pause
exit /b 0



