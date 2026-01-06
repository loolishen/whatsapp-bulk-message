# WABot Troubleshooting - Why Messages Aren't Reaching Your Webhook

## ✅ Your Webhook is Working!

Your webhook returns 200 OK when tested with curl. The issue is **WABot is not forwarding messages**.

## 🔍 Step 1: Check if WABot is Sending Anything

**In Cloud Shell, run:**
```bash
gcloud app logs read --limit=200 --project=whatsapp-bulk-messaging-480620 | grep -i "WEBHOOK\|POST.*whatsapp"
```

**Look for:**
- `WEBHOOK POST HIT` - means WABot sent something
- If you see NOTHING when you send a WhatsApp message, WABot is not configured correctly

## 🔧 Step 2: Verify WABot Dashboard Configuration

### A. Webhook URL (MUST BE EXACT)

1. Go to **WABot Dashboard**: https://app.wabot.my
2. Navigate to: **Settings** → **Webhook** or **Automation** → **Webhook**
3. **Webhook URL MUST BE EXACTLY:**
   ```
   https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
   ```
4. **Common mistakes:**
   - ❌ Missing `https://`
   - ❌ Wrong domain
   - ❌ Missing trailing `/`
   - ❌ Extra spaces
   - ❌ `http://` instead of `https://`

### B. Enable "Forward Data to Webhook" (CRITICAL!)

1. In WABot Dashboard → **Settings** → **Webhook**
2. Find **"Forward Data to Webhook"** toggle/checkbox
3. **MUST BE ENABLED** ✅ (green/checked/on)
4. **This is the #1 reason messages don't reach your webhook!**

### C. Enable Message Events

1. In WABot Dashboard → **Settings** → **Webhook**
2. Under **"Events"** or **"Webhook Events"** section
3. **Enable these events:**
   - ✅ **Message** (incoming messages)
   - ✅ **Status** (message delivery status)
   - ✅ **QR** (QR code events - optional)

### D. Test Webhook Button

1. In WABot Dashboard → **Settings** → **Webhook**
2. Click **"Test Webhook"** or **"Validate"** or **"Send Test"** button
3. **Expected result:** "Webhook is valid" or "Success" or "200 OK"
4. **If it fails:** Check the error message and fix the URL

## 📱 Step 3: Check WABot Instance Status

1. Go to **WABot Dashboard** → **Instances** or **Connections**
2. Your WhatsApp instance (phone: 60162107682) should show:
   - ✅ **Status: Connected** (green/active)
   - ✅ **QR Code: Scanned** (if using QR login)
3. **If status is "Disconnected":**
   - Reconnect your WhatsApp
   - Scan QR code again if needed
   - Wait for "Connected" status before testing

## 🧪 Step 4: Test with Real WhatsApp Message

1. **Send a test message** to your WhatsApp number: `60162107682`
2. **Message:** `TEST` or `JOIN`
3. **Immediately check logs:**
   ```bash
   gcloud app logs read --limit=50 --project=whatsapp-bulk-messaging-480620 | grep -i "WEBHOOK"
   ```
4. **Expected:** You should see `WEBHOOK POST HIT` within 1-2 seconds
5. **If you see nothing:** WABot is not forwarding (go back to Step 2)

## 🔍 Step 5: Check WABot Logs (if available)

1. In WABot Dashboard → **Logs** or **Activity**
2. Look for:
   - Webhook delivery attempts
   - Error messages
   - Failed webhook calls

## 🚨 Common Issues & Solutions

### Issue 1: "Forward Data to Webhook" is Disabled
**Solution:** Enable it in WABot Dashboard → Settings → Webhook

### Issue 2: Wrong Webhook URL
**Solution:** Copy-paste the exact URL:
```
https://whatsapp-bulk-messaging-480620.as.r.appspot.com/webhook/whatsapp/
```

### Issue 3: WABot Instance is Disconnected
**Solution:** Reconnect WhatsApp in WABot Dashboard

### Issue 4: Message Events Not Enabled
**Solution:** Enable "Message" event in webhook settings

### Issue 5: Webhook URL Has HTTP Instead of HTTPS
**Solution:** Use `https://` not `http://`

## ✅ Verification Checklist

Before testing, verify:

- [ ] Webhook URL is set correctly in WABot Dashboard
- [ ] "Forward Data to Webhook" is **ENABLED**
- [ ] "Message" event is **ENABLED**
- [ ] WABot instance status is **"Connected"**
- [ ] Webhook test button shows **"Success"**
- [ ] Your webhook returns 200 OK (tested with curl)

## 📞 Still Not Working?

If you've checked everything above and messages still don't reach your webhook:

1. **Check WABot Dashboard for error messages**
2. **Try the "Test Webhook" button** - what error does it show?
3. **Check if WABot has a "Webhook Logs" section** - look for failed deliveries
4. **Verify your WABot plan supports webhooks** (some free plans don't)

## 🎯 Next Steps After Webhook Works

Once you see `WEBHOOK POST HIT` in logs when sending WhatsApp messages:

1. **Re-enable processing** in `whatsapp_webhook.py` (uncomment the TODO section)
2. **Test with a real message** - should create customer and process contest flow
3. **Monitor logs** for any processing errors
