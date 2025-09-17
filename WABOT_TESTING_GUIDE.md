# WABOT Testing Guide

## Step 1: Start Django Server
```bash
python manage.py runserver 0.0.0.0:8000
```

## Step 2: Test Webhook Endpoint

### Option A: Using Python Script
```bash
python test_local_webhook.py
```

### Option B: Using curl
```bash
curl -X POST http://127.0.0.1:8000/webhook/whatsapp/ \
  -H "Content-Type: application/json" \
  -d '{
    "type": "message",
    "data": {
      "id": "test_001",
      "from": "60162107682",
      "message": "hello",
      "timestamp": "1640995200"
    }
  }'
```

### Option C: Using Postman
1. Open Postman
2. Set method to POST
3. URL: `http://127.0.0.1:8000/webhook/whatsapp/`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
```json
{
  "type": "message",
  "data": {
    "id": "test_001",
    "from": "60162107682",
    "message": "hello",
    "timestamp": "1640995200"
  }
}
```

## Step 3: Configure WABOT Webhook

1. Go to your WABOT dashboard
2. Set webhook URL to: `http://your-ngrok-url.ngrok.io/webhook/whatsapp/`
3. Enable webhook for message events

## Step 4: Test with Real WhatsApp

1. Send a message to your WhatsApp number
2. Check Django logs for webhook data
3. Check customer list for new customer
4. Verify PDPA consent flow

## Step 5: Verify Results

1. Check `/customers/` page for new customer
2. Check customer detail page for messages
3. Verify consent status
4. Test PDPA responses (YES/NO/STOP)

## Troubleshooting

### If webhook not receiving data:
1. Check WABOT webhook URL is correct
2. Use ngrok for local testing: `ngrok http 8000`
3. Check Django logs for errors
4. Verify webhook endpoint is accessible

### If customer not created:
1. Check tenant exists in database
2. Check phone number format
3. Check webhook data format
4. Check Django logs for errors

### If messages not recorded:
1. Check conversation creation
2. Check WhatsAppConnection exists
3. Check CoreMessage creation
4. Check database constraints
