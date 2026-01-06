# 🔧 OCR Setup Guide - Google Cloud Vision API

## ✅ Why Google Cloud Vision?

**Perfect for App Engine:**
- ✅ Native GCP integration (no API key needed)
- ✅ Uses your project's service account automatically
- ✅ Works on App Engine Standard (no GPU needed)
- ✅ Excellent OCR performance
- ✅ **Integrated with custom parsers + hints** from `ocr/` folder

**Benefits over other solutions:**
- **vs DeepSeek API:** DeepSeek doesn't support vision/images (text-only)
- **vs OpenAI Vision:** No extra API key/billing needed
- **vs HuggingFace models:** No GPU required, no large model downloads

---

## 🎯 Custom Parsers + Hints Integration

The OCR system uses **curated hints** to improve accuracy:

### 📦 Store Hints (`ocr/app/store_hints_w4.py`)
- 64 Malaysian store names (AEON, KHIND, HomePro, etc.)
- Prioritizes known stores for accurate matching

### 🛒 Product Hints (`ocr/app/product_hints_w4.py`)
- 150+ KHIND product patterns (rice cookers, fans, appliances)
- Model numbers, common typos, variations
- Helps identify items even with OCR errors

### 📍 Location Map (`ocr/app/store_loc_map_w4.py`)
- Store → City/State mapping
- Auto-fills location based on detected store

### 🔍 Smart Parsers (`ocr/app/parsers.py`)
- `extract_store_name()` - Uses fuzzy matching + hints
- `extract_location()` - Looks up location from map
- `extract_amount()` - Multiple pattern matching for totals
- `extract_products()` - Prioritizes hint-matched items

---

## 📋 Setup Steps

### 1. Enable Google Cloud Vision API

```bash
gcloud services enable vision.googleapis.com --project=whatsapp-bulk-messaging-480620
```

### 2. Verify Permissions

App Engine service account automatically has Vision API access. To verify:

```bash
gcloud projects get-iam-policy whatsapp-bulk-messaging-480620 \
  --flatten="bindings[].members" \
  --filter="bindings.members:*@appspot.gserviceaccount.com"
```

### 3. Deploy

```powershell
$GCLOUD = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
& $GCLOUD app deploy app.yaml --project whatsapp-bulk-messaging-480620 --quiet
```

---

## 💰 Pricing (Dec 2024)

| Feature | First 1,000 units/month | Additional units |
|---------|-------------------------|------------------|
| **Document Text Detection** | FREE | $1.50 per 1,000 |
| Text Detection | FREE | $1.50 per 1,000 |

**Typical receipt processing:**
- 1 receipt = 1 API call
- **First 1,000 receipts/month:** FREE
- **After that:** ~$0.0015 per receipt

**Much cheaper than OpenAI Vision** (~$0.001 per receipt with gpt-4o-mini)

---

## 🔧 What Changed in the Code?

### `messaging/deepseek_ocr_wrapper.py`

**Now uses:**
1. **Google Cloud Vision API** for text extraction
2. **Custom parsers** from `ocr/app/parsers.py`
3. **Store/Product hints** for accurate matching

**Key improvements:**
```python
# Before: Called OpenAI API with image_url
response = client.chat.completions.create(...)

# After: Uses Google Cloud Vision + custom parsers
response = vision_client.document_text_detection(image=image)
text_lines = [line.strip() for line in full_text.split('\n')]

# Parse with hints
store_name = extract_store_name(text_lines, preferred_stores=STORE_HINTS)
products = extract_products(text_lines, preferred_items=PRODUCT_HINTS)
```

### `requirements.txt`

Added:
```
google-cloud-vision>=3.4.0
```

### `app.yaml`

Removed OpenAI/DeepSeek API keys (no longer needed).

---

## ✅ Testing After Deploy

### 1. Check Vision API is enabled

```bash
gcloud services list --enabled --filter="name:vision.googleapis.com" --project=whatsapp-bulk-messaging-480620
```

Should show:
```
NAME                    TITLE
vision.googleapis.com   Cloud Vision API
```

### 2. Test the full flow

1. Send **"TEST"** to your WhatsApp bot
2. Complete PDPA → Name → Email → IC
3. Send a **receipt photo** (not document)
4. Check logs:

```bash
gcloud app logs tail --project whatsapp-bulk-messaging-480620 | grep -E "(Vision|OCR|parsers)"
```

**Expected logs:**
```
[INFO] Google Cloud Vision API initialized successfully
[INFO] OCR parsers loaded: 64 store hints, 150 product hints
[INFO] Vision API extracted 45 lines of text
[INFO] Parsed with hints: store=KHIND MARKETING, location=SHAH ALAM, SELANGOR, amount=RM89.90, items=3
[INFO] GCP Vision OCR processed: KHIND MARKETING, RM89.90, 3 items
```

**NOT expected:**
```
[ERROR] Google Cloud Vision API not available
[WARNING] Parsers not loaded, using basic extraction
```

---

## 🎨 How Hints Improve Accuracy

### Example: Store Name Detection

**OCR Output (with errors):**
```
KH ND MARKETING SDN BHD
SHAH ALAM SELANGOR
```

**Without hints:**
- Store: "KH ND MARKETING" ❌ (incomplete)

**With hints:**
- Fuzzy match finds: "KHIND MARKETING" ✅
- Location map finds: "SHAH ALAM, SELANGOR" ✅

### Example: Product Detection

**OCR Output:**
```
KHI JAR RIC CKR RCJ1009     RM 45.90
KHIND STAND FAN 16"         RM 89.00
```

**Without hints:**
- Extracts all items equally

**With hints:**
- Prioritizes known KHIND products
- "KHI JAR RIC CKR" → Matches "KHIND JAR RICE RCJ1009" hint
- Ensures important products aren't missed due to OCR errors

---

## 🔄 Adding More Hints

### To add new stores:

Edit `ocr/app/store_hints_w4.py`:
```python
STORE_HINTS_W4 = [
    "AEON BIG (M) Sdn Bhd",
    "YOUR NEW STORE NAME",  # Add here
    # ...
]
```

### To add new products:

Edit `ocr/app/product_hints_w4.py`:
```python
PRODUCT_HINTS_W4 = [
    "KHIND RICE COOKER 7.8L",
    "YOUR NEW PRODUCT NAME",  # Add here
    # ...
]
```

### To add store locations:

Edit `ocr/app/store_loc_map_w4.py`:
```python
RAW_STORE_LOCATIONS = r"""
YOUR STORE NAME	CITY, STATE
"""
```

Then redeploy.

---

## 📞 Troubleshooting

### "Google Cloud Vision API not available"

**Solution:**
```bash
gcloud services enable vision.googleapis.com --project=whatsapp-bulk-messaging-480620
```

### "Parsers not loaded"

**Cause:** Missing `ocr/` folder in deployment

**Solution:** Ensure `ocr/` is committed to git and not in `.gcloudignore`

### "No text extracted from image"

**Causes:**
- Image too blurry/dark
- Image URL from WABot is expired/inaccessible
- Receipt is upside down

**Solution:** Ask customer to resend a clearer photo

### Vision API works but parsing is poor

**Solution:** Check/improve hints in `ocr/app/`:
- Add more store variations to `store_hints_w4.py`
- Add more product patterns to `product_hints_w4.py`
- Update location mappings in `store_loc_map_w4.py`

---

## 🆓 Free Tier Details

Google Cloud Vision Free Tier (monthly):
- **1,000 requests FREE** per month
- Resets on the 1st of each month
- No credit card required for free tier
- After free tier: $1.50 per 1,000 requests

**Perfect for testing and small contests!**

---

## 📚 Additional Resources

- [Google Cloud Vision API Docs](https://cloud.google.com/vision/docs)
- [Vision API Python Client](https://cloud.google.com/python/docs/reference/vision/latest)
- [Vision API Pricing](https://cloud.google.com/vision/pricing)
