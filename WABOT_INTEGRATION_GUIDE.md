# 🤖 WABot.my Integration Guide - Keyword Auto-Reply System

## 📋 Overview

This guide walks you through setting up **wabot.my** webhook integration with your Django WhatsApp Bulk Message application to enable **automated keyword-based replies** for contests.

---

## 🎯 What You'll Achieve

✅ Receive incoming WhatsApp messages via webhook  
✅ Automatically detect keywords (e.g., "JOIN", "SUBMIT", "STOP")  
✅ Send custom replies based on contest-specific keywords  
✅ Track customer contest participation automatically  
✅ Handle multi-language keywords (English + Malay)

---

## 🏗️ Architecture Overview

```
┌─────────────┐         ┌──────────────┐         ┌───────────────┐
│ Customer    │         │  WABot.my    │         │  Your Django  │
│  WhatsApp   │────────▶│   Platform   │────────▶│  Application  │
│             │         │              │         │               │
└─────────────┘         └──────────────┘         └───────────────┘
                                                           │
                                                           ▼
                                                  ┌────────────────┐
                                                  │  Keyword       │
                                                  │  Matching      │
                                                  │  Engine        │
                                                  └────────────────┘
                                                           │
                                                           ▼
                                                  ┌────────────────┐
                                                  │  Send Auto     │
                                                  │  Reply         │
                                                  └────────────────┘
```

---

## 📦 Part 1: WABot.my Setup

### Step 1: Login to WABot.my Dashboard

1. Go to [https://app.wabot.my](https://app.wabot.my)
2. Login with your credentials
3. Navigate to your **WhatsApp Instance**

### Step 2: Get Your Instance Details

You'll need these details:

| Field | Location | Example |
|-------|----------|---------|
| **Instance ID** | Dashboard → Instance Settings | `wa_instance_12345` |
| **API Token** | Settings → API Token | `abc123def456...` |
| **Phone Number** | Instance Dashboard | `60123456789` |

📝 **Save these details** - you'll need them later!

---

### Step 3: Configure Webhook URL

1. **In WABot.my Dashboard:**
   - Go to **Settings** → **Webhook Settings**
   - Find the **Webhook URL** field

2. **Enter your webhook URL:**
   ```
   https://your-project-id.as.r.appspot.com/webhook/whatsapp/
   ```
   
   Replace `your-project-id` with your actual Google App Engine project ID.

3. **Webhook Events to Enable:**
   - ✅ `message` - Incoming messages
   - ✅ `message_status` - Message delivery status
   - ✅ `qr` - QR code for connecting device

4. **Save Settings**

---

### Step 4: Test Webhook Connection

1. **In WABot.my Dashboard:**
   - Go to **Webhook Test** section
   - Click **Send Test Webhook**

2. **Check your application logs:**
   ```bash
   gcloud app logs read --limit=20 --project=YOUR_PROJECT_ID
   ```

3. **Look for:**
   ```
   Received WABOT webhook data: {...}
   ```

✅ **If you see this log**, your webhook is working!

---

## 📝 Part 2: Django Application Setup

### Step 1: Add WABot Configuration

Edit `settings_production.py`:

```python
# WABot.my Configuration
WABOT_INSTANCE_ID = os.environ.get('WABOT_INSTANCE_ID', 'your_instance_id')
WABOT_API_TOKEN = os.environ.get('WABOT_API_TOKEN', 'your_api_token')
WABOT_API_URL = 'https://api.wabot.my/v1'
WABOT_PHONE_NUMBER = os.environ.get('WABOT_PHONE_NUMBER', '60123456789')
```

### Step 2: Update `app.yaml` with Environment Variables

```yaml
env_variables:
  DJANGO_SETTINGS_MODULE: "settings_production"
  SECRET_KEY: "your-secret-key"
  CLOUD_SQL_CONNECTION_NAME: "project:region:instance"
  
  # WABot Configuration
  WABOT_INSTANCE_ID: "your_instance_id"
  WABOT_API_TOKEN: "your_api_token"
  WABOT_PHONE_NUMBER: "60123456789"
```

---

## 🔧 Part 3: Keyword Auto-Reply Setup

### Understanding the Keyword System

Your application now supports **contest-specific keyword auto-replies**:

| Feature | Description | Example |
|---------|-------------|---------|
| **Keywords** | Trigger words customers send | `JOIN`, `MASUK`, `SUBMIT` |
| **Replies** | Automated responses | "Thank you for joining!" |
| **Contest-Specific** | Each contest has its own keywords | Contest A: `JOIN`, Contest B: `PROMO` |
| **Multi-Language** | Support multiple keywords | `JOIN`, `MASUK`, `SERTAI` (all trigger same reply) |

---

### How to Add Keywords to Contests

#### Method 1: During Contest Creation

1. **Go to:** Contest Management → Create New Contest
2. **Scroll to:** "Keyword Auto-Reply" section
3. **Add Keywords and Replies:**

```
┌─────────────────────────────────────────────────────────┐
│  Keyword #1                                             │
│  ─────────────────────────────────────────────────────  │
│  Keywords: JOIN, MASUK, SERTAI                          │
│  Reply: Thank you for joining our contest! Please send  │
│  your NRIC photo to continue.                           │
│  ───────────────────────────────────────────────────    │
│                                                          │
│  [+ Add Another Keyword Reply]                          │
└─────────────────────────────────────────────────────────┘
```

4. **Click Save**

#### Method 2: Via Django Admin

1. **Go to:** `/admin/messaging/promptreply/`
2. **Click:** "Add Prompt Reply"
3. **Fill in:**
   - **Name:** "Contest Welcome Message"
   - **Keywords:** `JOIN,MASUK,SERTAI` (comma-separated)
   - **Body:** "Thank you for joining..."
   - **Contest:** Select your contest
   - **Is Active:** ✅ Checked

---

### Keyword Matching Rules

The system uses **smart matching**:

1. **Case-Insensitive:** `JOIN` = `join` = `JoIn`
2. **Whitespace Trimmed:** `" JOIN "` = `"JOIN"`
3. **Partial Match:** Message "I want to JOIN now" matches keyword "JOIN"
4. **Multiple Keywords:** One message can trigger multiple replies
5. **Priority:** Contest-specific keywords take priority over global keywords

---

## 🎨 Part 4: Common Use Cases

### Use Case 1: Contest Entry Flow

**Customer Sends:** `JOIN`

**System Response:**
```
✅ Thank you for joining our Christmas Contest!

Please send us:
1️⃣ Your NRIC photo
2️⃣ Your receipt photo (min RM50)

Type HELP if you need assistance.
```

---

### Use Case 2: Help Request

**Customer Sends:** `HELP`

**System Response:**
```
ℹ️ Contest Help Menu:

🎯 JOIN - Join the contest
📸 SUBMIT - Submit your entry
❓ STATUS - Check your entry status
🛑 STOP - Opt out of messages

Need more help? Reply with your question.
```

---

### Use Case 3: Status Check

**Customer Sends:** `STATUS`

**System Response:**
```
📊 Your Contest Status:

Contest: Christmas 2025
Status: ✅ Verified
Submitted: Dec 10, 2025
NRIC: Verified ✓
Receipt: Verified ✓

Good luck! 🍀
```

---

### Use Case 4: Opt-Out

**Customer Sends:** `STOP`

**System Response:**
```
We've received your request to stop receiving contest messages.

You will no longer receive:
❌ Contest notifications
❌ Marketing messages

You can rejoin anytime by typing JOIN.
```

---

## 📊 Part 5: Database Setup

### Create Keyword Auto-Reply Migration

The new database fields needed:

```python
# messaging/models.py - PromptReply enhancement

class PromptReply(models.Model):
    """Enhanced keyword-based auto-replies for contests"""
    prompt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='prompt_replies')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='prompt_replies', 
                                blank=True, null=True, help_text='Link to specific contest (optional)')
    
    name = models.CharField(max_length=120, help_text='Internal name for this reply')
    keywords = models.TextField(help_text='Comma-separated keywords (e.g., JOIN,MASUK,SERTAI)')
    body = models.TextField(help_text='Reply message text')
    
    # Optional media
    image_url = models.URLField(blank=True, null=True, help_text='Optional image URL')
    
    # Settings
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text='Higher priority = checked first')
    
    # Statistics
    trigger_count = models.IntegerField(default=0, help_text='Number of times triggered')
    last_triggered_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.keywords})"
    
    def get_keywords_list(self):
        """Get list of keywords"""
        return [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]
    
    def matches_message(self, message_text):
        """Check if message contains any of the keywords"""
        message_lower = message_text.lower().strip()
        for keyword in self.get_keywords_list():
            if keyword in message_lower:
                return True
        return False
```

---

## 🚀 Part 6: Deployment

### Step 1: Create Migration

```bash
# Create migration for new fields
python manage.py makemigrations messaging
```

### Step 2: Deploy to GCP

```cmd
REM On Windows
deploy_local.bat
```

### Step 3: Run Migrations in Cloud Shell

```bash
# In Cloud Shell
./deploy_to_gcp.sh
```

---

## 🧪 Part 7: Testing Your Setup

### Test 1: Send a Message

1. **From WhatsApp:** Send `JOIN` to your WABot number
2. **Expected:** Auto-reply with contest welcome message
3. **Check logs:**
   ```bash
   gcloud app logs read --limit=30 | grep -i "keyword"
   ```

---

### Test 2: Check Database

```bash
# In Cloud Shell
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
psql -h 127.0.0.1 -U DB_USER -d DB_NAME

# Check prompt replies
SELECT name, keywords, trigger_count FROM messaging_promptreply WHERE is_active = true;

# Check messages received
SELECT text_body, direction, created_at FROM messages ORDER BY created_at DESC LIMIT 10;
```

---

### Test 3: Verify Webhook Logs

```bash
# Check recent webhook activity
gcloud app logs read --limit=50 | grep -i "webhook\|wabot"
```

Expected logs:
```
Received WABOT webhook data: {...}
Processing WABOT message from 60123456789: JOIN
Keyword matched: JOIN → Sending reply
Successfully sent keyword auto-reply
```

---

## 📋 Part 8: Keyword Setup Examples

### Example 1: Contest Entry Keywords

```yaml
Name: Contest Entry
Keywords: JOIN,MASUK,SERTAI,ENTER
Reply: |
  🎉 Welcome to our contest!
  
  To enter, please send:
  1. Your NRIC photo
  2. Your receipt (min RM50)
  
  Good luck!
Contest: Christmas 2025
Priority: 10
```

---

### Example 2: Help Keywords

```yaml
Name: Help Command
Keywords: HELP,BANTUAN,INFO
Reply: |
  ℹ️ Available Commands:
  
  JOIN - Enter contest
  STATUS - Check your entry
  SUBMIT - Submit documents
  STOP - Opt out
  
  Reply with a command to continue.
Contest: (None - applies to all)
Priority: 5
```

---

### Example 3: Status Check

```yaml
Name: Status Check
Keywords: STATUS,CHECK,SEMAK
Reply: |
  📊 Checking your status...
  
  We'll send you an update shortly.
  Type HELP for more options.
Contest: Christmas 2025
Priority: 8
```

---

## 🔒 Part 9: Security Considerations

### 1. Webhook Security

**Add webhook verification:**

```python
# In whatsapp_webhook.py
def verify_wabot_signature(request):
    """Verify webhook came from WABot"""
    signature = request.headers.get('X-WABot-Signature')
    if not signature:
        return False
    
    # Verify signature with your secret
    expected = hmac.new(
        settings.WABOT_WEBHOOK_SECRET.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

### 2. Rate Limiting

**Prevent spam:**

```python
# Add to settings_production.py
WABOT_RATE_LIMIT = 10  # Max messages per minute per user
```

### 3. Sensitive Data

**Never log:**
- Customer phone numbers in plain text
- Full NRIC numbers
- Personal information

---

## 📊 Part 10: Monitoring & Analytics

### Track Keyword Performance

```sql
-- Most popular keywords
SELECT 
    name,
    keywords,
    trigger_count,
    last_triggered_at
FROM messaging_promptreply
WHERE is_active = true
ORDER BY trigger_count DESC
LIMIT 10;
```

### Monitor Response Times

```sql
-- Average response time
SELECT 
    AVG(EXTRACT(EPOCH FROM (sent_at - created_at))) as avg_response_seconds
FROM messages
WHERE direction = 'outbound'
AND created_at > NOW() - INTERVAL '24 hours';
```

---

## 🐛 Part 11: Troubleshooting

### Issue 1: No Auto-Reply Sent

**Symptoms:** Customer sends keyword, no reply received

**Check:**
1. ✅ Keyword exists in database
2. ✅ `is_active = true`
3. ✅ Keywords match (case-insensitive)
4. ✅ WABot connection active
5. ✅ Check logs: `gcloud app logs read --limit=50`

**Solution:**
```bash
# Check prompt replies
python manage.py shell

from messaging.models import PromptReply
replies = PromptReply.objects.filter(is_active=True)
for r in replies:
    print(f"{r.name}: {r.keywords}")
```

---

### Issue 2: Webhook Not Receiving Messages

**Symptoms:** No logs showing incoming webhooks

**Check:**
1. ✅ Webhook URL correct in WABot dashboard
2. ✅ HTTPS enabled (required)
3. ✅ Firewall allows WABot IPs
4. ✅ Django app deployed

**Solution:**
```bash
# Test webhook manually
curl -X POST https://your-app.appspot.com/webhook/whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{"type":"message","data":{"from":"60123456789","message":"TEST"}}'
```

---

### Issue 3: Duplicate Replies

**Symptoms:** Customer receives multiple replies for one message

**Check:**
1. ✅ Multiple keywords with same trigger?
2. ✅ Duplicate PromptReply records?
3. ✅ Webhook called multiple times?

**Solution:**
```python
# Add deduplication in webhook handler
def _process_wabot_message(self, data):
    message_id = data.get('data', {}).get('id')
    
    # Check if already processed
    if CoreMessage.objects.filter(provider_msg_id=message_id).exists():
        logger.info(f"Message {message_id} already processed, skipping")
        return
    
    # Continue processing...
```

---

## 📚 Part 12: API Reference

### Send Message via WABot API

```python
import requests

def send_wabot_message(phone_number, message_text):
    """Send message via WABot API"""
    url = f"{settings.WABOT_API_URL}/send-message"
    
    headers = {
        'Authorization': f'Bearer {settings.WABOT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'instance_id': settings.WABOT_INSTANCE_ID,
        'to': phone_number,
        'message': message_text
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### Send Message with Image

```python
def send_wabot_image(phone_number, image_url, caption=''):
    """Send image via WABot API"""
    url = f"{settings.WABOT_API_URL}/send-image"
    
    headers = {
        'Authorization': f'Bearer {settings.WABOT_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'instance_id': settings.WABOT_INSTANCE_ID,
        'to': phone_number,
        'image_url': image_url,
        'caption': caption
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

---

## ✅ Part 13: Checklist

Before going live, verify:

### WABot Setup
- [ ] Instance connected and active
- [ ] Webhook URL configured
- [ ] API token saved in `app.yaml`
- [ ] Test message sent successfully

### Django Application
- [ ] Database migrations run
- [ ] PromptReply records created
- [ ] Keywords tested
- [ ] Webhook receiving messages

### Testing
- [ ] Sent test keyword → received reply
- [ ] Checked database for message records
- [ ] Verified logs show processing
- [ ] Tested multiple keywords
- [ ] Tested case variations (JOIN vs join)

### Production Ready
- [ ] Rate limiting enabled
- [ ] Error logging configured
- [ ] Monitoring dashboard set up
- [ ] Customer support trained

---

## 🎯 Quick Start Summary

```bash
# 1. Configure WABot in dashboard
# 2. Update app.yaml with credentials
# 3. Deploy application
gcloud app deploy

# 4. Run migrations
./deploy_to_gcp.sh

# 5. Create keyword replies in Django admin
# 6. Test with WhatsApp message
# 7. Monitor logs
gcloud app logs tail
```

---

## 📞 Support

- **WABot Documentation:** https://docs.wabot.my
- **Django Logs:** `gcloud app logs read --limit=50`
- **Database Access:** Cloud Shell + Cloud SQL Proxy

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Tested With:** WABot.my Basic Plan, Django 5.0.6


