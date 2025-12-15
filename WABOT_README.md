# 🤖 WABot.my Keyword Auto-Reply System

## 📖 Complete Integration Package for WhatsApp Contest Management

This package provides **automated keyword-based replies** for your WhatsApp contest platform using wabot.my.

---

## 🎯 What This Does

When a customer sends a WhatsApp message like:
- `"JOIN"` → Auto-reply: "Welcome to our contest! Please send your NRIC..."
- `"HELP"` → Auto-reply: "Commands: JOIN, STATUS, SUBMIT, STOP"
- `"STATUS"` → Auto-reply: "Your contest entry status: Verified ✅"

**All automated. No manual intervention needed.** ✨

---

## 📚 Documentation Structure

This package includes **3 comprehensive guides**. Choose based on your needs:

### 🚀 **Quick Start** (5 minutes)
**File:** `WABOT_QUICK_SETUP.md`

**For:** First-time setup, getting started quickly

**Includes:**
- 5-minute setup checklist
- Essential configuration
- First keyword reply
- Quick testing

**Start here if:** You want to get up and running ASAP

---

### 📘 **Complete Guide** (60+ pages)
**File:** `WABOT_INTEGRATION_GUIDE.md`

**For:** Comprehensive understanding, production deployment

**Includes:**
- Detailed architecture explanation
- Step-by-step configuration
- Advanced features
- Troubleshooting guide
- API reference
- Security considerations
- 10+ example configurations

**Start here if:** You want full understanding before deploying

---

### 📝 **Implementation Summary**
**File:** `WABOT_IMPLEMENTATION_SUMMARY.md`

**For:** Technical overview, understanding what was built

**Includes:**
- Files created/modified
- Architecture diagram
- Database schema changes
- Code examples
- Testing procedures

**Start here if:** You're a developer reviewing the implementation

---

## 🎬 Getting Started

### Step 1: Choose Your Path

**Fast Track** (Recommended for testing):
```
1. Read: WABOT_QUICK_SETUP.md
2. Follow 5-minute setup
3. Test with WhatsApp
4. Read full guide later
```

**Complete Understanding** (Recommended for production):
```
1. Read: WABOT_INTEGRATION_GUIDE.md
2. Understand architecture
3. Follow deployment steps
4. Test thoroughly
5. Go live
```

### Step 2: Deploy

```bash
# Windows Local Machine
deploy_local.bat

# Cloud Shell
./deploy_to_gcp.sh
```

### Step 3: Configure WABot

1. Login to [app.wabot.my](https://app.wabot.my)
2. Get Instance ID and API Token
3. Set webhook URL to:
   ```
   https://YOUR_PROJECT.as.r.appspot.com/webhook/whatsapp/
   ```

### Step 4: Create Keywords

**Quick Way** (Django Admin):
```
1. Go to /admin/messaging/promptreply/
2. Add Keyword Auto-Reply
3. Enter: JOIN,MASUK,SERTAI
4. Write welcome message
5. Save
```

### Step 5: Test

```
Send "JOIN" from WhatsApp → Receive auto-reply ✅
```

---

## 📦 What's Included

### Documentation (4 files)
- ✅ `WABOT_README.md` - This file
- ✅ `WABOT_QUICK_SETUP.md` - 5-minute setup guide
- ✅ `WABOT_INTEGRATION_GUIDE.md` - Complete 60+ page guide
- ✅ `WABOT_IMPLEMENTATION_SUMMARY.md` - Technical overview

### Code (4 files)
- ✅ `messaging/keyword_autoreply_service.py` - Keyword matching engine
- ✅ `messaging/admin_promptreply.py` - Django admin interface
- ✅ `messaging/migrations/0011_enhance_promptreply_keywords.py` - Database migration
- ✅ `messaging/whatsapp_webhook.py` - Updated webhook handler

---

## 🎯 Key Features

### Smart Keyword Matching
- ✅ Case-insensitive: `JOIN` = `join` = `JoIn`
- ✅ Multi-language: `JOIN,MASUK,SERTAI`
- ✅ Partial match: "I want to JOIN" triggers keyword "JOIN"

### Contest Integration
- ✅ Contest-specific keywords
- ✅ Global keywords (all contests)
- ✅ Active contest validation

### Personalization
- ✅ `{{name}}` - Customer name
- ✅ `{{first_name}}` - First name only
- ✅ Custom placeholders

### Analytics
- ✅ Trigger count per keyword
- ✅ Last triggered timestamp
- ✅ Message history tracking

### Admin Interface
- ✅ Full CRUD for keyword replies
- ✅ Visual keyword display
- ✅ Bulk actions
- ✅ Search & filters

---

## 🧪 Testing Checklist

Before going live:

- [ ] WABot webhook configured
- [ ] Environment variables set in `app.yaml`
- [ ] Database migration run
- [ ] At least 5 keyword replies created
- [ ] Sent test message from WhatsApp
- [ ] Received auto-reply
- [ ] Checked logs for errors
- [ ] Verified message in database

---

## 📊 Common Keywords to Set Up

### Must-Have Keywords:

1. **JOIN** (Priority: 10)
   - Keywords: `JOIN,MASUK,SERTAI,ENTER,DAFTAR`
   - Reply: Contest welcome + instructions

2. **HELP** (Priority: 9)
   - Keywords: `HELP,BANTUAN,INFO,TOLONG`
   - Reply: Available commands

3. **STATUS** (Priority: 8)
   - Keywords: `STATUS,CHECK,SEMAK`
   - Reply: Entry status update

4. **STOP** (Priority: 10)
   - Keywords: `STOP,BERHENTI,UNSUBSCRIBE,QUIT`
   - Reply: Unsubscribe confirmation

5. **THANKS** (Priority: 5)
   - Keywords: `THANKS,THANK,TERIMA KASIH,TQ`
   - Reply: You're welcome

---

## 🔧 Configuration Example

### app.yaml
```yaml
env_variables:
  DJANGO_SETTINGS_MODULE: "settings_production"
  SECRET_KEY: "your-secret-key"
  
  # WABot Configuration
  WABOT_INSTANCE_ID: "your_instance_id"
  WABOT_API_TOKEN: "your_api_token"
  WABOT_PHONE_NUMBER: "60123456789"
```

### Keyword Reply Example
```python
Name: Welcome Message
Keywords: JOIN,MASUK,SERTAI
Body: |
  🎉 Welcome to our contest!
  
  To enter:
  1️⃣ Send your NRIC photo
  2️⃣ Send your receipt (min RM50)
  
  Type HELP for assistance.
  Good luck! 🍀
  
Contest: Christmas 2025
Priority: 10
Is Active: ✅ Yes
```

---

## 🐛 Troubleshooting

### No reply received?
**Check:** `WABOT_QUICK_SETUP.md` → Troubleshooting section

### Wrong reply sent?
**Check:** Priority values and keyword overlap

### Multiple replies?
**Check:** Ensure only one keyword matches

**Full troubleshooting:** See `WABOT_INTEGRATION_GUIDE.md` Part 11

---

## 📞 Support

### Documentation
1. **Quick Setup:** `WABOT_QUICK_SETUP.md`
2. **Full Guide:** `WABOT_INTEGRATION_GUIDE.md`
3. **Implementation:** `WABOT_IMPLEMENTATION_SUMMARY.md`

### Logs
```bash
gcloud app logs read --limit=50
gcloud app logs tail  # Real-time
```

### Database
```bash
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432 &
psql -h 127.0.0.1 -U USER -d DATABASE
```

### WABot
- Dashboard: https://app.wabot.my
- Docs: https://docs.wabot.my

---

## ✅ Success Criteria

You're ready for production when:

- ✅ Webhook receiving messages
- ✅ Keywords triggering replies
- ✅ Messages logged in database
- ✅ No errors in logs
- ✅ Customers receiving replies within 2 seconds
- ✅ Analytics tracking working

---

## 🎉 Next Steps

### 1. Deploy (15 minutes)
```bash
deploy_local.bat           # Windows
./deploy_to_gcp.sh         # Cloud Shell
```

### 2. Configure WABot (5 minutes)
Follow `WABOT_QUICK_SETUP.md`

### 3. Create Keywords (10 minutes)
Create 5 essential keyword replies

### 4. Test (5 minutes)
Send test messages from WhatsApp

### 5. Go Live! 🚀
Monitor logs and analytics

---

## 📈 Recommended Reading Order

### For Quick Testing:
```
1. WABOT_README.md (this file) ← You are here
2. WABOT_QUICK_SETUP.md (5 min)
3. Test your setup
4. Read full guide later
```

### For Production Deployment:
```
1. WABOT_README.md (this file) ← You are here
2. WABOT_IMPLEMENTATION_SUMMARY.md (technical overview)
3. WABOT_INTEGRATION_GUIDE.md (complete guide)
4. WABOT_QUICK_SETUP.md (deployment checklist)
5. Deploy and test
```

### For Developers:
```
1. WABOT_IMPLEMENTATION_SUMMARY.md (code overview)
2. Review: messaging/keyword_autoreply_service.py
3. Review: messaging/admin_promptreply.py
4. WABOT_INTEGRATION_GUIDE.md (API reference)
```

---

## 🎓 Learning Resources

### Beginner
- Start: `WABOT_QUICK_SETUP.md`
- Practice: Create 2-3 keyword replies
- Test: Send WhatsApp messages

### Intermediate
- Read: `WABOT_INTEGRATION_GUIDE.md` Parts 1-8
- Implement: 10+ keyword replies
- Customize: Add personalization

### Advanced
- Read: `WABOT_INTEGRATION_GUIDE.md` Parts 9-13
- Extend: Custom matching logic
- Optimize: Performance tuning

---

## 🔗 Quick Links

| Resource | Location |
|----------|----------|
| **Quick Setup** | `WABOT_QUICK_SETUP.md` |
| **Full Guide** | `WABOT_INTEGRATION_GUIDE.md` |
| **Implementation** | `WABOT_IMPLEMENTATION_SUMMARY.md` |
| **Service Code** | `messaging/keyword_autoreply_service.py` |
| **Admin Interface** | `messaging/admin_promptreply.py` |
| **Migration** | `messaging/migrations/0011_enhance_promptreply_keywords.py` |
| **Webhook Handler** | `messaging/whatsapp_webhook.py` |
| **WABot Dashboard** | https://app.wabot.my |
| **WABot Docs** | https://docs.wabot.my |

---

## 💡 Pro Tips

1. **Start Small:** Create 2-3 keywords, test, then expand
2. **Multi-Language:** Always include English + Malay
3. **Priority Matters:** Set critical keywords (JOIN, STOP) to priority 10
4. **Test Before Live:** Use test contest to verify everything works
5. **Monitor Analytics:** Check trigger counts weekly to refine keywords

---

## 🎯 Quick Commands

```bash
# Deploy
deploy_local.bat && ./deploy_to_gcp.sh

# Check logs
gcloud app logs tail

# Test webhook
curl -X POST https://YOUR_APP.appspot.com/webhook/whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{"type":"message","data":{"from":"60123456789","message":"JOIN"}}'

# Check database
psql -h 127.0.0.1 -U USER -d DB -c "SELECT name, keywords, trigger_count FROM messaging_promptreply;"
```

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Last Updated:** December 2025  
**Documentation:** 4 comprehensive guides  
**Code Quality:** Production-grade with error handling  
**Testing:** Ready for integration testing

---

## 🚀 Ready to Start?

**Choose your path:**

- 🏃 **Fast Track:** Open `WABOT_QUICK_SETUP.md` now
- 📚 **Complete Guide:** Open `WABOT_INTEGRATION_GUIDE.md` now
- 💻 **Code Review:** Open `WABOT_IMPLEMENTATION_SUMMARY.md` now

**Questions?** Check the relevant guide's troubleshooting section.

**Let's go! 🎉**


