# Deploy DeepSeek OCR to App Engine

## What Was Changed

### ✅ **Removed PaddleOCR** (causing the errors)
- Removed `paddleocr`, `paddlepaddle`, `paddlex` from requirements.txt
- These packages were causing "Checking connectivity to model hosters" hangs
- Created new DeepSeek API-based OCR system instead

### ✅ **Added DeepSeek Vision API**
- New file: `messaging/deepseek_ocr_wrapper.py` - API-based OCR
- Uses your DeepSeek API key (already added to `app.yaml`)
- Much faster and more reliable than local models
- No GPU required, runs on App Engine Standard

### ✅ **Updated Configuration**
- `app.yaml` - Added DeepSeek API key and environment variables
- `wsgi.py` - Added offline mode flags to prevent model downloads
- `requirements.txt` - Removed PaddleOCR dependencies
- `messaging/receipt_ocr_service.py` - Now uses DeepSeek API wrapper

## How to Deploy

Run these commands in **Cloud Shell**:

```bash
cd ~/app-full

# Download the updated files
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/app.yaml .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/requirements.txt .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/wsgi.py .
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/deepseek_ocr_wrapper.py messaging/
gsutil cp gs://staging.whatsapp-bulk-messaging-480620.appspot.com/messaging/receipt_ocr_service.py messaging/

# Deploy to App Engine
gcloud app deploy app.yaml --quiet --project=whatsapp-bulk-messaging-480620

# Monitor logs to verify deployment
gcloud app logs tail -s default
```

## What to Look For

### ✅ **Success Indicators:**
- No more "Checking connectivity to the model hosters" messages
- No more "Warning: CSV file not found" spam
- Workers start and stay running (no constant restarts)
- Site loads without 500 errors
- DeepSeek API calls in logs when receipts are processed

### ❌ **If You See Errors:**
- **"DeepSeek API key not configured"** → API key didn't load (check env vars)
- **"OpenAI import error"** → Need to install `openai` package (should be in requirements.txt)
- **"Rate limit exceeded"** → DeepSeek API rate limit (wait or upgrade plan)

## Testing the OCR

Once deployed, you can test by:
1. Creating a contest with the conversation flow
2. Sending "JOIN" keyword
3. Following the flow and uploading a receipt image
4. The system will call DeepSeek API to process the receipt
5. Check logs for OCR results

## Environment Variables Added

```yaml
DEEPSEEK_API_KEY: "sk-a1f8f0629a8e46c193c9ae6d6143b3db"
DEEPSEEK_BASE_URL: "https://api.deepseek.com"
DEEPSEEK_MODEL: "deepseek-chat"
DISABLE_MODEL_SOURCE_CHECK: "True"
HF_HUB_OFFLINE: "1"
TRANSFORMERS_OFFLINE: "1"
```

## Files Changed

1. **messaging/deepseek_ocr_wrapper.py** (NEW) - DeepSeek API integration
2. **messaging/receipt_ocr_service.py** (UPDATED) - Uses DeepSeek wrapper
3. **app.yaml** (UPDATED) - Added DeepSeek API credentials
4. **requirements.txt** (UPDATED) - Removed PaddleOCR dependencies
5. **wsgi.py** (UPDATED) - Added offline mode flags

## Benefits of DeepSeek API

✅ No model downloads (fast startup)
✅ No GPU required (works on App Engine Standard)
✅ No PaddleOCR dependency issues
✅ Better OCR accuracy (vision model)
✅ Structured JSON parsing built-in
✅ Handles Malaysian receipts well

## Troubleshooting

If deployment fails:
```bash
# Check app logs
gcloud app logs read --limit=100 --project=whatsapp-bulk-messaging-480620 | grep -i error

# Check deployment status
gcloud app versions list --project=whatsapp-bulk-messaging-480620

# Rollback if needed
gcloud app versions list --service=default --project=whatsapp-bulk-messaging-480620
gcloud app services set-traffic default --splits=PREVIOUS_VERSION=1 --project=whatsapp-bulk-messaging-480620
```

