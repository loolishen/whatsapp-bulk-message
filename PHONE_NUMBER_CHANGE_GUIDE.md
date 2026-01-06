# 📱 Phone Number Change Guide
## From 60162107682 → 601163955379

This guide documents all changes made for switching your WABot.my phone number.

---

## ✅ Changes Made

### 1. **app.yaml** - Environment Variables Updated
```yaml
WABOT_PHONE_NUMBER: "601163955379"  # Changed from 60162107682
```

### 2. **settings_production.py** - Configuration Updated (2 places)
```python
WHATSAPP_API = {
    'DEFAULT_TEST_NUMBER': '+601163955379',  # Changed from +60162107682
}

WABOT_PHONE_NUMBER = os.environ.get('WABOT_PHONE_NUMBER', '601163955379')  # Changed default
```

### 3. **setup_whatsapp_connection.py** - Script Updated
```python
phone_number='601163955379',  # Changed from 60162107682
```

### 4. **New Scripts Created**
- `update_phone_number.py` - Updates database records
- `verify_tenant_and_connection.py` - Verifies complete setup

---

## 🚀 Deployment Steps

### Step 1: Deploy Updated Code

**Windows (Local Machine):**
```cmd
deploy_local.bat
```

**OR Cloud Shell:**
```bash
gcloud app deploy --project=whatsapp-bulk-messaging-480620
```

### Step 2: Run Database Update in Cloud Shell

```bash
# Start Cloud SQL Proxy
cloud-sql-proxy whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db --port=5432 &

# Run the update script
python update_phone_number.py

# Verify everything
python verify_tenant_and_connection.py
```

### Step 3: Update WABot.my Webhook

1. Login to [app.wabot.my](https://app.wabot.my)
2. Go to **Settings** → **Webhook**
3. Confirm webhook URL is still set to:
   ```
   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
   ```
4. Make sure these events are enabled:
   - ✅ `message` (incoming messages)
   - ✅ `message_status` (delivery status)

### Step 4: Test the Connection

**Test incoming messages:**
1. Send a WhatsApp message to **+601163955379**
2. Check logs:
   ```bash
   gcloud app logs tail -s default --project=whatsapp-bulk-messaging-480620
   ```
3. You should see:
   ```
   WEBHOOK POST HIT path=/webhook/whatsapp/
   Processing incoming message...
   ```

**Test sending messages:**
1. Login to your app: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/
2. Go to Campaigns → Create Campaign
3. Send a test message
4. Check if it sends successfully

---

## 🔐 Your Tenant Account (Unchanged)

Your login credentials remain the same:

- **URL:** https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/
- **Username:** `tenant`
- **Password:** `Tenant123!`

This account is automatically created/updated by `migrate_db.py` which runs during deployment.

---

## 📊 What Happens When Messages Arrive

Here's how your system processes incoming WhatsApp messages:

```
1. WABot.my receives WhatsApp message to +601163955379
   ↓
2. WABot.my sends webhook POST to:
   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
   ↓
3. Your Django app receives the webhook (messaging/whatsapp_webhook.py)
   ↓
4. System looks up Tenant (uses Tenant.objects.first())
   ↓
5. System looks up WhatsAppConnection for that Tenant
   ↓
6. Creates/Updates Customer record
   ↓
7. Creates Conversation record
   ↓
8. Creates CoreMessage record (inbound)
   ↓
9. Processes through StepByStepContestService
   ↓
10. Sends auto-reply if keywords match (via PromptReply)
```

**Important:** The phone number in `WhatsAppConnection` is used for sending messages, but incoming messages are matched based on your tenant's first WhatsAppConnection record.

---

## 🔍 Verification Checklist

Run this checklist after deployment:

- [ ] **Code deployed:**
  ```bash
  gcloud app versions list --service=default --project=whatsapp-bulk-messaging-480620
  ```
  (Should show new version deployed)

- [ ] **Database updated:**
  ```bash
  python verify_tenant_and_connection.py
  ```
  (Should show phone: 601163955379)

- [ ] **Tenant account works:**
  - Login at: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/login/
  - Username: tenant
  - Password: Tenant123!

- [ ] **WhatsApp connection configured:**
  - Go to Admin → Messaging → WhatsApp Connections
  - Should see: 601163955379 with Instance ID: 68A0A11A89A8D

- [ ] **Webhook receives messages:**
  - Send test message to +601163955379
  - Check logs show: "WEBHOOK POST HIT"

- [ ] **Can send messages:**
  - Create test campaign
  - Send to your test number
  - Verify message arrives

---

## 🐛 Troubleshooting

### Issue: "No WhatsApp connection found" error in logs

**Solution:** Run the database update script:
```bash
python update_phone_number.py
```

### Issue: Messages not arriving via webhook

**Check:**
1. WABot.my webhook URL is correct:
   ```
   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
   ```
2. WABot.my phone number is: +601163955379
3. Webhook events enabled: `message` and `message_status`
4. Check logs for webhook hits:
   ```bash
   gcloud app logs tail -s default --project=whatsapp-bulk-messaging-480620
   ```

### Issue: Can't send messages

**Check:**
1. WhatsAppConnection record exists with:
   - Phone: 601163955379
   - Instance ID: 68A0A11A89A8D
   - Token: 68a0a10422130
2. Environment variables in app.yaml are correct
3. WABot.my instance is active and connected

### Issue: Can't login with tenant/Tenant123!

**Solution:** Re-run database migration:
```bash
# In Cloud Shell with Cloud SQL Proxy running
python migrate_db.py
```

This will ensure the user account is created/updated.

---

## 📞 Quick Reference

### WABot.my Configuration
- **Instance ID:** 68A0A11A89A8D
- **Phone Number:** +601163955379 (or 601163955379)
- **API Token:** 68a0a10422130
- **API URL:** https://app.wabot.my/api
- **Webhook URL:** https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/

### Tenant Account
- **Username:** tenant
- **Password:** Tenant123!
- **Tenant Name:** Demo Tenant
- **Plan:** pro

### Project Details
- **Project ID:** whatsapp-bulk-messaging-480620
- **Region:** asia-southeast1
- **App URL:** https://whatsapp-bulk-messaging-480620.as.r.appspot.com

---

## 🎯 Next Steps

After completing the deployment:

1. **Test incoming messages:**
   - Send "TEST" to +601163955379
   - Verify webhook receives it

2. **Create keyword auto-replies:**
   - Login to admin panel
   - Go to Messaging → Keyword Auto-Replies
   - Create replies for your contests

3. **Monitor logs:**
   ```bash
   gcloud app logs tail -s default --project=whatsapp-bulk-messaging-480620
   ```

4. **Create your first campaign:**
   - Go to Campaigns → Create Campaign
   - Test with your phone number first

---

## 📝 Files Modified

| File | Change | Status |
|------|--------|--------|
| `app.yaml` | WABOT_PHONE_NUMBER env var | ✅ Updated |
| `settings_production.py` | Default phone numbers (2 places) | ✅ Updated |
| `setup_whatsapp_connection.py` | Hardcoded phone number | ✅ Updated |
| `update_phone_number.py` | Database update script | ✅ Created |
| `verify_tenant_and_connection.py` | Verification script | ✅ Created |

---

## ✅ Summary

Your WhatsApp system is now configured for the new phone number **+601163955379**. All code changes are complete, and your `tenant/Tenant123!` account is properly configured.

The webhook endpoint remains the same (`/webhook/whatsapp/`), so incoming messages will continue to work once you deploy and update the database.

**Ready to deploy!** 🚀



