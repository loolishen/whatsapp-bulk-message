# 🚀 Your WABot.my Setup - Personalized Guide

## 📋 Your WABot Details

```yaml
Phone Number: 60162107682
Webhook Token: 6bb47e635cd7649c10a503e7032ecff4
Your Django Webhook: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
```

✅ **Configuration already added to `app.yaml`!**

---

## 🔧 Step 1: Configure WABot Dashboard

### Login to WABot.my

1. Go to: https://app.wabot.my
2. Login with your credentials
3. Select your WhatsApp instance (60162107682)

### Set Webhook URL

1. **Navigate to:** Settings → Webhook Settings
2. **Set Webhook URL to:**
   ```
   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
   ```

3. **Enable these events:**
   - ✅ `message` - Incoming messages from customers
   - ✅ `message_status` - Delivery status updates

4. **Save Settings**

---

## 📦 Step 2: Deploy Your Updates

### Windows (Local Machine)

```cmd
deploy_local.bat
```

### Cloud Shell

```bash
./deploy_to_gcp.sh
```

This will:
- ✅ Deploy updated `app.yaml` with WABot config
- ✅ Run database migrations for keyword auto-reply
- ✅ Set up the system

---

## 🎯 Step 3: Create Your First Keyword Reply

### Option A: Django Admin (Recommended)

1. Go to: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/
2. Login with: `tenant` / `Tenant123!`
3. Navigate to: **Messaging** → **Keyword Auto-Replies**
4. Click: **Add Keyword Auto-Reply**
5. Fill in:

```yaml
Name: Welcome Message
Keywords: JOIN,MASUK,SERTAI,HI,HELLO
Body: |
  🎉 Welcome! Thank you for contacting us on 60162107682.
  
  To join our contest:
  1️⃣ Send your NRIC photo
  2️⃣ Send your receipt
  
  Type HELP for more commands.
  Good luck! 🍀

Contest: (Select your contest or leave blank for all)
Priority: 10
Is Active: ✅ Checked
```

6. Click **Save**

### Option B: Python Shell (Quick Test)

```bash
# In Cloud Shell
python manage.py shell

from messaging.models import PromptReply, Tenant
from django.utils import timezone

tenant = Tenant.objects.first()

PromptReply.objects.create(
    tenant=tenant,
    name="Welcome Message",
    keywords="JOIN,MASUK,SERTAI,HI,HELLO",
    body="🎉 Welcome! Thank you for contacting 60162107682.\n\nTo join: Send your NRIC photo.\nType HELP for assistance.",
    is_active=True,
    priority=10
)

print("✅ Keyword reply created!")
```

---

## 🧪 Step 4: Test Your Setup

### Test 1: Send WhatsApp Message

1. **From your phone:** Send `"JOIN"` to **60162107682**
2. **Expected:** Auto-reply within 2 seconds
3. **Check:** You receive welcome message

### Test 2: Check Logs

```bash
gcloud app logs read --limit=30 --project=whatsapp-bulk-messaging-480620 | grep -i "keyword\|wabot"
```

**Expected output:**
```
Received WABOT webhook data: {...}
Processing WABOT message from 60123456789: JOIN
Keyword matched: Welcome Message
Keyword auto-reply: 1 replies sent
```

### Test 3: Verify Database

```bash
# In Cloud Shell
cloud-sql-proxy whatsapp-bulk-messaging-480620:asia-southeast1:whatsapp-bulk-db --port=5432 &
sleep 3

psql -h 127.0.0.1 -U whatsapp_user -d whatsapp_bulk

# Check keyword replies
SELECT name, keywords, trigger_count, is_active 
FROM messaging_promptreply 
WHERE is_active = true;

# Check recent messages
SELECT text_body, direction, created_at 
FROM messaging_coremessage 
ORDER BY created_at DESC 
LIMIT 10;

# Exit
\q
pkill cloud-sql-proxy
```

---

## 📱 Recommended Keyword Replies to Create

### 1. **Welcome/Join** (Priority: 10)
```yaml
Keywords: JOIN,MASUK,SERTAI,ENTER,DAFTAR,HI,HELLO,HAI
Body: |
  🎉 Selamat datang! Welcome to our contest!
  
  Untuk menyertai / To participate:
  1️⃣ Hantar gambar IC / Send NRIC photo
  2️⃣ Hantar resit pembelian / Send receipt
  
  Taip HELP untuk bantuan / Type HELP for assistance
  
  📞 Contact: 60162107682
```

### 2. **Help Menu** (Priority: 9)
```yaml
Keywords: HELP,BANTUAN,INFO,TOLONG,?
Body: |
  ℹ️ Arahan / Commands:
  
  • JOIN - Sertai pertandingan / Join contest
  • STATUS - Semak status / Check status
  • SUBMIT - Hantar dokumen / Submit documents
  • STOP - Berhenti mesej / Stop messages
  
  Balas dengan arahan / Reply with command
  
  📞 60162107682
```

### 3. **Status Check** (Priority: 8)
```yaml
Keywords: STATUS,CHECK,SEMAK,MY STATUS,STATUSKU
Body: |
  📊 Menyemak status anda...
     Checking your status...
  
  Sila tunggu sebentar.
  Please wait a moment.
  
  📞 60162107682
```

### 4. **Thank You** (Priority: 5)
```yaml
Keywords: THANKS,THANK,TERIMA KASIH,TQ,THANK YOU,TY
Body: |
  Sama-sama! 😊 You're welcome!
  
  Nak bantuan lagi? / Need more help?
  Taip HELP / Type HELP
  
  📞 60162107682
```

### 5. **Stop/Unsubscribe** (Priority: 10)
```yaml
Keywords: STOP,BERHENTI,UNSUBSCRIBE,QUIT,CANCEL,BATAL
Body: |
  ✅ Anda telah berjaya diberhentikan daripada menerima mesej.
     You have been unsubscribed from receiving messages.
  
  Untuk sertai semula, taip: JOIN
  To rejoin, type: JOIN
  
  📞 60162107682
```

---

## 🔍 Troubleshooting

### Issue: No auto-reply received

**Check 1: Webhook configured in WABot?**
```
Login to app.wabot.my → Settings → Webhook
Should be: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
```

**Check 2: Keyword reply exists?**
```bash
python manage.py shell
>>> from messaging.models import PromptReply
>>> PromptReply.objects.filter(is_active=True).values('name', 'keywords')
```

**Check 3: Logs showing webhook received?**
```bash
gcloud app logs read --limit=50 | grep -i "wabot\|webhook"
```

### Issue: Webhook not receiving messages

**Test webhook manually:**
```bash
curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "data": {
      "from": "60123456789",
      "message": "TEST",
      "id": "test123",
      "timestamp": "2025-12-15T12:00:00Z"
    }
  }'
```

Expected: `{"status": "success"}`

### Issue: WABot instance not connected

**Check in WABot Dashboard:**
1. Go to app.wabot.my
2. Check if WhatsApp is connected (green indicator)
3. If not connected, scan QR code again

---

## ✅ Success Checklist

After completing setup:

- [ ] `app.yaml` updated with WABot config
- [ ] Deployed to Google App Engine
- [ ] Database migrations run
- [ ] Webhook URL set in WABot dashboard (https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/)
- [ ] At least 5 keyword replies created
- [ ] Sent test "JOIN" message to 60162107682
- [ ] Received auto-reply
- [ ] Checked logs - no errors
- [ ] Verified messages in database

---

## 🎯 Quick Test Commands

```bash
# Deploy
deploy_local.bat && ./deploy_to_gcp.sh

# Check logs
gcloud app logs tail --project=whatsapp-bulk-messaging-480620

# Test webhook
curl -X POST https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{"type":"message","data":{"from":"60123456789","message":"JOIN"}}'

# Check database
psql -h 127.0.0.1 -U whatsapp_user -d whatsapp_bulk \
  -c "SELECT name, keywords, trigger_count FROM messaging_promptreply WHERE is_active=true;"
```

---

## 📞 Your Contact Details

| Detail | Value |
|--------|-------|
| **Your WhatsApp Number** | 60162107682 |
| **Your Webhook Token** | 6bb47e635cd7649c10a503e7032ecff4 |
| **Your Django Webhook** | https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/ |
| **WABot Dashboard** | https://app.wabot.my |
| **Your App URL** | https://whatsapp-bulk-messaging-480620.as.r.appspot.com |
| **Django Admin** | https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/ |

---

## 🚀 Next Steps

1. ✅ **Deploy** - Run `deploy_local.bat` then `./deploy_to_gcp.sh`
2. ✅ **Configure** - Set webhook in WABot dashboard
3. ✅ **Create Keywords** - Add 5 keyword replies via Django admin
4. ✅ **Test** - Send "JOIN" to 60162107682
5. ✅ **Monitor** - Check logs and analytics

---

## 📚 Additional Resources

- **Full Integration Guide:** `WABOT_INTEGRATION_GUIDE.md`
- **Quick Setup:** `WABOT_QUICK_SETUP.md`
- **Implementation Details:** `WABOT_IMPLEMENTATION_SUMMARY.md`
- **WABot Documentation:** https://docs.wabot.my

---

**Status:** ✅ Ready to Deploy  
**Your Number:** 60162107682  
**Last Updated:** December 2025

**Start with Step 1 above!** 🎉


