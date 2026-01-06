# 🧪 Complete Contest Flow Test Instructions

## Quick Start (Copy & Paste into Cloud Shell)

### Option 1: Python Script (Recommended - Easier)

```bash
cd ~/app-full

# Download the test script
curl -o test_contest_flow.py https://raw.githubusercontent.com/your-repo/test_contest_flow.py
# OR if you have it locally, upload it via gsutil

# Make it executable
chmod +x test_contest_flow.py

# Install requests if not already installed
pip3 install requests --user

# Run the test
python3 test_contest_flow.py
```

### Option 2: Bash Script

```bash
cd ~/app-full

# Download the test script
curl -o test_contest_full_flow.sh https://raw.githubusercontent.com/your-repo/test_contest_full_flow.sh
# OR if you have it locally, upload it via gsutil

# Make it executable
chmod +x test_contest_full_flow.sh

# Run the test
bash test_contest_full_flow.sh
```

## Manual Step-by-Step Test

If you prefer to test manually, follow these steps:

### 1. Create Test Contest

```bash
cd ~/app-full
python3 << 'EOF'
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, Tenant

tenant = Tenant.objects.first()
contest = Contest.objects.create(
    tenant=tenant,
    name="🧪 Test Contest",
    description="Test contest",
    starts_at=datetime.now() - timedelta(days=1),
    ends_at=datetime.now() + timedelta(days=30),
    is_active=True,
    keywords="TEST,JOIN",
    auto_reply_message="Welcome! Reply 'AGREE' to continue.",
    introduction_message="Hello! Welcome to our test contest.",
    pdpa_message="Do you agree to our PDPA terms? Reply 'AGREE'.",
    participant_agreement="Thank you! Please send your NRIC.",
    requires_nric=True,
    requires_receipt=True,
    min_purchase_amount=10.00
)
print(f"Contest created: {contest.contest_id}")
EOF
```

### 2. Test WhatsApp Webhook - Initial Message

```bash
curl -X POST "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+60123456789",
            "type": "text",
            "text": {"body": "TEST"},
            "id": "test_msg_1",
            "timestamp": "1234567890"
          }],
          "contacts": [{
            "profile": {"name": "Test User"},
            "wa_id": "+60123456789"
          }]
        }
      }]
    }]
  }'
```

### 3. Test PDPA Agreement

```bash
curl -X POST "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+60123456789",
            "type": "text",
            "text": {"body": "AGREE"},
            "id": "test_msg_2",
            "timestamp": "1234567891"
          }],
          "contacts": [{
            "profile": {"name": "Test User"},
            "wa_id": "+60123456789"
          }]
        }
      }]
    }]
  }'
```

### 4. Test NRIC Submission

```bash
curl -X POST "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+60123456789",
            "type": "text",
            "text": {"body": "123456789012"},
            "id": "test_msg_3",
            "timestamp": "1234567892"
          }],
          "contacts": [{
            "profile": {"name": "Test User"},
            "wa_id": "+60123456789"
          }]
        }
      }]
    }]
  }'
```

### 5. Test Receipt Image (OCR)

```bash
curl -X POST "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "+60123456789",
            "type": "image",
            "image": {
              "id": "test_image_1",
              "mime_type": "image/png",
              "caption": "Test receipt"
            },
            "id": "test_msg_4",
            "timestamp": "1234567893"
          }],
          "contacts": [{
            "profile": {"name": "Test User"},
            "wa_id": "+60123456789"
          }]
        }
      }]
    }]
  }'
```

### 6. Verify Data in Database

```bash
cd ~/app-full
python3 << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Contest, ContestEntry, Customer

# Find test contest
contest = Contest.objects.filter(name__icontains="Test Contest").first()
if contest:
    print(f"Contest: {contest.name}")
    entries = ContestEntry.objects.filter(contest=contest)
    print(f"Entries: {entries.count()}")
    for entry in entries:
        print(f"  - Entry ID: {entry.entry_id}")
        print(f"    Status: {entry.status}")
        print(f"    NRIC: {getattr(entry, 'contestant_nric', 'N/A')}")
        print(f"    Store: {getattr(entry, 'store_name', 'N/A')}")
else:
    print("No test contest found")
EOF
```

### 7. Check Contest Manager Page

```bash
curl -I "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/contest/manager/"
```

### 8. Check Participants Manager Page

```bash
curl -I "https://whatsapp-bulk-messaging-480620.as.r.appspot.com/participants/"
```

## What the Test Checks

✅ **Contest Creation**: Creates a test contest with all required fields  
✅ **WhatsApp Webhook**: Tests receiving messages via webhook  
✅ **Auto Reply**: Verifies keyword matching and auto-reply messages  
✅ **PDPA Flow**: Tests PDPA consent flow  
✅ **NRIC Collection**: Tests NRIC number collection  
✅ **OCR Processing**: Tests receipt image upload and OCR extraction  
✅ **Data Storage**: Verifies data is saved to ContestEntry model  
✅ **Contest Manager**: Checks that data appears in contest manager page  
✅ **Participants Manager**: Checks that data appears in participants manager page  

## Troubleshooting

### Test Script Fails

1. **Check Django Setup**:
   ```bash
   cd ~/app-full
   python3 -c "import django; print(django.get_version())"
   ```

2. **Check Database Connection**:
   ```bash
   python3 manage.py dbshell --settings=settings_production
   ```

3. **Check Logs**:
   ```bash
   gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620
   ```

### No Entries Found

- Wait a few seconds for processing to complete
- Check if webhook is receiving messages
- Verify contest is active and matches keywords
- Check database directly using Django shell

### OCR Not Working

- Verify DeepSeek API key is set in `app.yaml`
- Check OCR service logs
- Ensure image is being received by webhook
- Test OCR service directly

## Expected Results

After running the test, you should see:

1. ✅ Contest created in database
2. ✅ Webhook responses (200 OK)
3. ✅ Contest entry created with:
   - NRIC number
   - Receipt image URL
   - OCR extracted data (store name, location, products)
   - Status: submitted or verified
4. ✅ Data visible in Contest Manager page
5. ✅ Data visible in Participants Manager page

## Next Steps After Testing

1. **View Logs**: `gcloud app logs read --limit=100`
2. **Check Database**: Use Django shell to query entries
3. **View Pages**: Visit the manager pages in browser
4. **Clean Up**: Delete test contest if needed

## Notes

- The test uses phone number `+60123456789` - change if needed
- Test contest name includes "Test Contest - Full Flow" for easy identification
- OCR processing may take a few seconds
- Some steps may require authentication (302 redirects are normal)

