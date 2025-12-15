# 🚀 WABot.my - 5-Minute Quick Setup

## ✅ Prerequisites Checklist

Before starting, make sure you have:

- [ ] WABot.my Basic plan subscription active
- [ ] WhatsApp number connected to WABot
- [ ] Django app deployed to Google App Engine
- [ ] Database migrations completed

---

## 📋 Step-by-Step Setup (5 Minutes)

### Step 1: Get WABot Credentials (2 minutes)

1. Login to [app.wabot.my](https://app.wabot.my)
2. Go to **Settings** → **API**
3. Copy these details:

```
Instance ID: _________________
API Token: _________________
Phone Number: _________________
```

---

### Step 2: Configure Your App (1 minute)

Edit `app.yaml` and add:

```yaml
env_variables:
  # Existing variables...
  
  # WABot Configuration
  WABOT_INSTANCE_ID: "your_instance_id_here"
  WABOT_API_TOKEN: "your_api_token_here"
  WABOT_PHONE_NUMBER: "60123456789"
```

---

### Step 3: Set Webhook URL (1 minute)

1. In WABot Dashboard → **Settings** → **Webhook**
2. Set Webhook URL to:

```
https://YOUR_PROJECT_ID.as.r.appspot.com/webhook/whatsapp/
```

3. Enable these events:
   - ✅ `message`
   - ✅ `message_status`

4. Click **Save**

---

### Step 4: Deploy & Migrate (2 minutes)

**Windows (Local Machine):**
```cmd
deploy_local.bat
```

**Cloud Shell:**
```bash
./deploy_to_gcp.sh
```

---

### Step 5: Create Your First Keyword Reply

**Option A: Django Admin** (Recommended)

1. Go to: `https://YOUR_APP.appspot.com/admin/`
2. Navigate to: **Messaging** → **Keyword Auto-Replies**
3. Click **Add Keyword Auto-Reply**
4. Fill in:

```
Name: Welcome Message
Keywords: JOIN,MASUK,SERTAI
Message: Welcome to our contest! 🎉

To participate:
1. Send your NRIC photo
2. Send your receipt

Good luck!

Contest: Select your contest
Priority: 10
Is Active: ✅ Checked
```

5. Click **Save**

**Option B: Python Shell** (Quick Test)

```bash
# In Cloud Shell
python manage.py shell

from messaging.models import PromptReply, Tenant, Contest
from messaging.keyword_autoreply_service import KeywordAutoReplyService

# Get your tenant
tenant = Tenant.objects.first()

# Get your contest (or None for global)
contest = Contest.objects.first()

# Create keyword reply
service = KeywordAutoReplyService()
service.create_prompt_reply(
    tenant=tenant,
    contest=contest,
    name="Welcome Message",
    keywords="JOIN,MASUK,SERTAI",
    body="Welcome to our contest! Please send your NRIC to continue.",
    priority=10
)

print("✅ Keyword reply created!")
```

---

## 🧪 Test Your Setup

### Test 1: Send Message from WhatsApp

1. **From your phone:** Send `JOIN` to your WABot number
2. **Expected:** Auto-reply received within 2 seconds
3. **Check:** Message appears in your app's message history

---

### Test 2: Check Logs

```bash
gcloud app logs read --limit=30 | grep -i "keyword"
```

**Expected output:**
```
Processing WABOT message from 60123456789: JOIN
Keyword matched: Welcome Message for customer...
Keyword auto-reply: 1 replies sent
```

---

### Test 3: Verify Database

```bash
# In Cloud Shell
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
psql -h 127.0.0.1 -U USER -d DATABASE

# Check prompt replies
SELECT name, keywords, trigger_count, is_active 
FROM messaging_promptreply 
WHERE is_active = true;

# Should show your keyword reply
```

---

## 🎯 Common Keywords to Set Up

Here are pre-configured keyword replies you should create:

### 1. **Contest Entry**
```yaml
Keywords: JOIN,MASUK,SERTAI,ENTER,DAFTAR
Message: |
  🎉 Welcome to [Contest Name]!
  
  To enter, please send:
  1️⃣ Your NRIC photo
  2️⃣ Your receipt (min RM50)
  
  Type HELP for assistance.
Priority: 10
```

### 2. **Help Command**
```yaml
Keywords: HELP,BANTUAN,INFO,TOLONG
Message: |
  ℹ️ How can I help you?
  
  Commands:
  • JOIN - Enter contest
  • STATUS - Check entry status
  • SUBMIT - Submit documents
  • STOP - Opt out
  
  Reply with a command.
Priority: 9
```

### 3. **Status Check**
```yaml
Keywords: STATUS,CHECK,SEMAK,MY STATUS
Message: |
  📊 Checking your contest status...
  
  Please wait a moment.
Priority: 8
```

### 4. **Opt-Out**
```yaml
Keywords: STOP,BERHENTI,UNSUBSCRIBE,QUIT
Message: |
  You've been unsubscribed from contest messages.
  
  To rejoin, type: JOIN
Priority: 10
```

### 5. **Thank You**
```yaml
Keywords: THANK,THANKS,TERIMA KASIH,TQ
Message: |
  You're welcome! 😊
  
  Need more help? Type HELP
Priority: 5
```

---

## ⚡ Pro Tips

### Tip 1: Use Priority Wisely

- **Priority 10:** Critical keywords (JOIN, STOP)
- **Priority 5-9:** Common keywords (HELP, STATUS)
- **Priority 1-4:** Optional keywords (THANKS, INFO)

### Tip 2: Multiple Languages

Always include Malay + English:
```
Keywords: JOIN,MASUK,SERTAI,ENTER,DAFTAR
```

### Tip 3: Personalize Messages

Use these placeholders:
- `{{name}}` - Full customer name
- `{{first_name}}` - First name only

Example:
```
Hi {{first_name}}! Welcome to our contest! 🎉
```

### Tip 4: Test Before Launch

Create a test contest and verify:
1. ✅ Keywords trigger correctly
2. ✅ Message formatting looks good
3. ✅ Images (if any) load properly
4. ✅ Multiple languages work

---

## 🐛 Troubleshooting

### Problem: No auto-reply received

**Check:**
```bash
# 1. Check webhook is receiving messages
gcloud app logs read --limit=20 | grep "WABOT"

# 2. Check keyword reply exists and is active
python manage.py shell
>>> from messaging.models import PromptReply
>>> PromptReply.objects.filter(is_active=True).count()
```

**Solution:**
- If count is 0 → Create keyword reply
- If no logs → Check webhook URL in WABot dashboard
- If logs but no reply → Check keywords match exactly

---

### Problem: Wrong reply sent

**Check:**
```bash
# Test keyword matching
python manage.py shell

from messaging.models import PromptReply
from messaging.keyword_autoreply_service import KeywordAutoReplyService

service = KeywordAutoReplyService()
prompt = PromptReply.objects.get(name="Your Prompt Name")

result = service.test_keyword_match("JOIN", prompt)
print(result)
# {'matches': True, 'matched_keywords': ['join']}
```

---

### Problem: Multiple replies sent

**Solution:** Set `priority` correctly and ensure only ONE keyword reply matches per message. The system sends only the FIRST match by default.

---

## 📞 Need Help?

1. **Check Logs:**
   ```bash
   gcloud app logs tail
   ```

2. **Test Webhook:**
   ```bash
   curl -X POST https://YOUR_APP.appspot.com/webhook/whatsapp/ \
     -H "Content-Type: application/json" \
     -d '{"type":"message","data":{"from":"60123456789","message":"TEST"}}'
   ```

3. **Verify Database:**
   ```sql
   SELECT * FROM messaging_promptreply WHERE is_active = true;
   ```

---

## ✅ Success Checklist

After setup, you should have:

- [ ] WABot webhook configured and receiving messages
- [ ] At least 5 keyword auto-replies created
- [ ] Tested keywords from WhatsApp
- [ ] Verified auto-replies sent successfully
- [ ] Checked logs for errors
- [ ] Database records created for messages

---

## 🎉 You're Done!

Your keyword auto-reply system is now live!

**Next Steps:**
1. Create more keyword replies for your contests
2. Monitor trigger counts in Django admin
3. Refine keywords based on customer usage
4. Add images to make replies more engaging

**Documentation:**
- Full Guide: `WABOT_INTEGRATION_GUIDE.md`
- API Reference: https://docs.wabot.my

---

**Setup Time:** ~5 minutes  
**Last Updated:** December 2025  
**Status:** Production Ready ✅


