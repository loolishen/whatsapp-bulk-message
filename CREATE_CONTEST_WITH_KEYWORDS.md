# 🎯 How to Create a Contest with Keyword Auto-Reply

## ✅ What's Different Now?

**Keywords are now part of Contest creation!**  
No separate panel needed - everything is in one place.

---

## 📋 Step-by-Step: Create Your First Contest

### Step 1: Deploy Your App

```cmd
REM On Windows
deploy_local.bat
```

Then in Cloud Shell:
```bash
./deploy_to_gcp.sh
```

---

### Step 2: Go to Contest Creation

1. **Open:** https://whatsapp-bulk-messaging-480620.as.r.appspot.com
2. **Navigate to:** Contest Manager → **Create Contest**

---

### Step 3: Fill in Contest Details

#### 📝 **Contest Section:**
```yaml
Name: Khind Merdeka Contest 2025
Description: Win amazing prizes this Merdeka!
Start Date: 2025-01-01 00:00
End Date: 2025-12-31 23:59
```

#### 🤖 **Keyword Auto-Reply Section:**
```yaml
Keywords: JOIN,MASUK,SERTAI,START,HI,HELLO
Auto-Reply Message: |
  🎉 Selamat datang! Welcome to Khind Merdeka Contest!
  
  Thank you for joining us! To participate:
  1️⃣ Send your NRIC photo
  2️⃣ Send your purchase receipt (min RM98)
  
  We'll guide you through each step!
  
  Type HELP if you need assistance.
  
Priority: 8
```

#### 🔒 **PDPA Agreement:**
```yaml
PDPA Link: https://khind.com.my/pages/privacy-policy
PDPA Message: (pre-filled)
Agreement Message: Wonderful! Welcome! Let's get started!
Rejection Message: We respect your choice.
```

#### 📋 **Requirements:**
```yaml
☑ Require NRIC
☑ Require Receipt
Minimum Purchase: 98.00
```

---

### Step 4: Click "Create Contest"

That's it! Your contest is now live with automatic keyword replies! 🎉

---

## 🧪 Test Your Contest

### 1. Send a keyword via WhatsApp

Send `"JOIN"` to your WABot number: **60162107682**

### 2. Expected Response

You should immediately receive your auto-reply message:
```
🎉 Selamat datang! Welcome to Khind Merdeka Contest!

Thank you for joining us! To participate:
1️⃣ Send your NRIC photo
2️⃣ Send your purchase receipt (min RM98)

We'll guide you through each step!

Type HELP if you need assistance.
```

---

## 📊 View Your Contests

**Go to:** Contest Manager

You'll see:
- ✅ All your contests (no more placeholders!)
- ✅ Keywords for each contest
- ✅ Entry counts
- ✅ Active/inactive status
- ✅ Start/end dates

---

## 🎨 Example Contests to Create

### Contest 1: Main Contest
```yaml
Name: Khind Merdeka 2025 Contest
Keywords: JOIN,MASUK,SERTAI,MERDEKA,CONTEST
Auto-Reply: 
  🎊 Welcome to Khind Merdeka Contest 2025!
  
  Win amazing prizes! To enter:
  • Send NRIC photo
  • Send receipt (RM98+ purchase)
  
  Let's get started! 🚀
Priority: 10
```

### Contest 2: Help/Support
```yaml
Name: Help & Support
Keywords: HELP,BANTUAN,INFO,SOKONGAN,SUPPORT
Auto-Reply:
  ℹ️ Need help? Here are your options:
  
  • Type STATUS - Check your entry
  • Type SUBMIT - Submit documents
  • Type CONTACT - Reach support
  
  📞 Support: 60162107682
Priority: 9
```

### Contest 3: Status Check
```yaml
Name: Check Status
Keywords: STATUS,SEMAK,CHECK,STATUSKU,MY STATUS
Auto-Reply:
  📊 Checking your contest status...
  
  Please wait a moment while we retrieve your information.
Priority: 8
```

---

## 🔍 Managing Multiple Contests

### Priority System

When someone sends "JOIN":
1. System checks contests by priority (highest first)
2. Finds first matching keyword
3. Sends that contest's auto-reply

**Example:**
- Contest A: Keywords "JOIN,START" - Priority 10 ✅ **Matched**
- Contest B: Keywords "JOIN,ENTER" - Priority 5 (skipped)

### Best Practices

1. **Use unique keywords** for different contests
2. **Higher priority** for main contests (8-10)
3. **Lower priority** for general replies (3-5)
4. **Test keywords** before making contest active

---

## ✏️ Editing Contests

1. Go to Django Admin: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/admin/
2. Login: `tenant` / `Tenant123!`
3. Click: **Messaging** → **Contests**
4. Edit any contest to update:
   - Keywords
   - Auto-reply message
   - Priority
   - Dates
   - Requirements

---

## 🐛 Troubleshooting

### Issue: Auto-reply not working

**Check:**
1. ✅ Contest `is_active` = True
2. ✅ Contest dates are current
3. ✅ Keywords are comma-separated (no spaces)
4. ✅ Auto-reply message is filled in
5. ✅ WABot webhook is configured

### Issue: Wrong reply sent

**Check:**
1. Multiple contests might have same keyword
2. Check priorities (higher wins)
3. Review keyword list in Contest Manager

### Issue: Can't create contest

**Check:**
1. All required fields filled:
   - Name ✅
   - Start/End dates ✅
   - Keywords ✅
   - Auto-reply message ✅
2. Dates are valid (start before end)

---

## 📈 Monitoring Performance

### In Contest Manager:

- **Total Entries:** See how many people joined
- **Keywords Triggered:** Track popular keywords
- **Active/Inactive:** Toggle contests on/off
- **Date Range:** See when contest runs

### In Django Admin:

More detailed stats:
- Individual contest analytics
- Customer entries
- Document submissions
- PDPA consents

---

## ✅ Quick Checklist

Before going live:

- [ ] Created contest with name & description
- [ ] Added keywords (comma-separated)
- [ ] Wrote auto-reply message
- [ ] Set priority (5-10)
- [ ] Configured PDPA messages
- [ ] Set requirements (NRIC, receipt, amount)
- [ ] Set start/end dates
- [ ] Clicked "Create Contest"
- [ ] Tested keywords via WhatsApp
- [ ] Received auto-reply
- [ ] Contest shows in Contest Manager

---

## 🚀 You're Ready!

**Your workflow:**
1. Create Contest → Fill form → Include keywords → Save
2. Test by sending keyword to WhatsApp
3. Monitor entries in Contest Manager
4. Select winners when contest ends

**No more:**
- ❌ Separate keyword panel
- ❌ Demo/hardcoded contests
- ❌ Complex setup

**Just:**
- ✅ One form
- ✅ Real contests
- ✅ Live immediately

---

**Your Details:**
- Phone: 60162107682
- Dashboard: https://whatsapp-bulk-messaging-480620.as.r.appspot.com
- Contest Manager: /contest_manager
- Create Contest: /contest_create

