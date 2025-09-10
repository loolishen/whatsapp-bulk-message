# WhatsApp Bulk Message App

A Django-based application for sending bulk WhatsApp messages using the WaBot.my API.

## Features

- WhatsApp-style message preview
- Bulk message sending to multiple contacts
- Contact management (CRUD operations)
- Image support for messages
- Real WhatsApp API integration
- Test contact (+60172419029) included for testing

## Setup Instructions

### 1. Install Dependencies

```bash
cd C:\whatsappbulkmessage
venv\Scripts\activate
pip install requests
```

### 2. Set Up WhatsApp API

First, you need to create a WhatsApp instance:

```bash
python manage.py setup_whatsapp --webhook-url=https://webhook.site/your-unique-id-here
```

This will:
- Create a new WhatsApp instance
- Set up a webhook (optional)
- Provide you with an instance ID

**Important:** Update the `DEFAULT_INSTANCE_ID` in `whatsapp_bulk/settings.py` with your actual instance ID.

### 3. Connect Your WhatsApp

After creating an instance, you'll need to scan a QR code with your WhatsApp mobile app to connect the instance to your WhatsApp account.

### 4. Test the Integration

```bash
python manage.py test_whatsapp --instance-id=YOUR_INSTANCE_ID --message="Test message from Django app!"
```

This will send a test message to +60172419029.

## API Configuration

### Current API Settings (whatsapp_bulk/settings.py):

```python
WHATSAPP_API = {
    'ACCESS_TOKEN': '68a0a10422130',
    'BASE_URL': 'https://app.wabot.my/api',
    'DEFAULT_INSTANCE_ID': '68A0A11A89A8D',  # Update this!
    'DEFAULT_TEST_NUMBER': '+60162107682',
}
```

### WaBot.my API Endpoints Used:

1. **Create Instance**: `GET /create_instance`
2. **Set Webhook**: `POST /set_webhook`
3. **Send Text**: `POST /send` (type: text)
4. **Send Media**: `POST /send` (type: media)

## Usage

### Running the App

```bash
python manage.py runserver
```

Navigate to:
- Main page: `http://localhost:8000/` - Send messages and select recipients
- Customer management: `http://localhost:8000/customers/` - Manage contacts

### Sending Messages

1. Go to the main page
2. Enter your message in the compose section
3. Optionally upload an image
4. Select recipients from the list
5. Click "Send Message"

The app will:
- Save the message to the database
- Send to each selected contact via WhatsApp API
- Show success/failure status

### Adding Contacts

You can add contacts in two ways:
1. Through the "Manage Customers" page
2. Via Django admin: `http://localhost:8000/admin/`

## Testing

### Test Contact Included
- Name: Test Contact  
- Phone: +60172419029

This contact is automatically added for testing purposes.

### Manual Testing Commands

```bash
# Test API connection
python manage.py test_whatsapp

# Test with custom message
python manage.py test_whatsapp --message="Hello from my app!"

# Test with different number
python manage.py test_whatsapp --number="+1234567890"
```

## File Structure

```
messaging/
├── models.py              # Contact, Message, BulkMessage models
├── views.py               # Main views with WhatsApp integration
├── whatsapp_service.py    # WhatsApp API service class
├── management/
│   └── commands/
│       ├── setup_whatsapp.py  # Setup instance command
│       └── test_whatsapp.py   # Test messaging command
└── templates/
    └── messaging/
        ├── recipients_and_preview.html  # Main page
        └── manage_customers.html        # Customer management
```

## Important Notes

1. **Instance ID**: Make sure to update `DEFAULT_INSTANCE_ID` in settings after creating an instance
2. **Phone Numbers**: The API expects numbers without the '+' sign (e.g., '60172419029' not '+60172419029')
3. **QR Code**: You must scan the QR code with your WhatsApp to activate the instance
4. **Rate Limits**: Be aware of WhatsApp's rate limits for bulk messaging
5. **Webhook**: Optional but recommended for receiving message status updates

## Troubleshooting

### Common Issues:

1. **"ModuleNotFoundError: No module named 'requests'"**
   - Solution: `pip install requests`

2. **"Failed to send message: 401 Unauthorized"**
   - Check your access token in settings
   - Verify your instance ID is correct

3. **"Failed to send message: Instance not connected"**
   - Scan the QR code to connect your WhatsApp
   - Check instance status in WaBot.my dashboard

4. **Messages not sending**
   - Verify phone number format (no '+' sign)
   - Check WhatsApp connection status
   - Review API response in console logs

### Debug Mode:

Enable debug logging by checking the console output when sending messages. Error details are printed to help diagnose issues.

## Next Steps

- Store instance IDs in database for multiple WhatsApp accounts
- Add message scheduling
- Implement delivery status tracking via webhooks
- Add support for WhatsApp groups
- Create message templates
