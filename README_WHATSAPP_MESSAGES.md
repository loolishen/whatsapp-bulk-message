# WhatsApp Messages System Documentation

## 📱 Overview

This document provides comprehensive documentation for the WhatsApp messaging system, including PDPA compliance, customer management, CRM integration, contest functionality, and bulk messaging capabilities.

## 🏗️ System Architecture

### Core Components
- **WhatsApp Webhook Handler** - Processes incoming messages
- **PDPA Consent Service** - Manages customer consent compliance
- **Customer Management** - Database operations for customer data
- **CRM Integration** - Customer relationship management features
- **Contest System** - Competition and engagement features
- **Bulk Messaging** - Mass communication capabilities

---

## 🔄 WhatsApp Message Flow

### 1. Incoming Message Processing

```mermaid
graph TD
    A[WhatsApp Message] --> B[Webhook Handler]
    B --> C[Customer Lookup/Creation]
    C --> D[PDPA Consent Check]
    D --> E{Consent Status}
    E -->|No Consent| F[Send Consent Templates]
    E -->|Granted| G[Process Message]
    E -->|Withdrawn| H[Service Only Response]
    F --> I[Wait for Response]
    I --> J[Update Consent Status]
    G --> K[Information Collection]
    H --> L[End]
    J --> M[Send Confirmation]
    K --> N[Update Database]
    M --> O[End]
    N --> O[End]
```

### 2. Message Types Supported

| Message Type | Description | Processing |
|--------------|-------------|------------|
| **Text** | Plain text messages | Full PDPA flow + info collection |
| **Image** | Photos and images | OCR processing for IC/receipts |
| **Document** | PDFs and files | Basic processing |
| **Sticker** | WhatsApp stickers | Acknowledgment only |

---

## 🛡️ PDPA Compliance System

### Consent Management Flow

#### 1. First Contact Templates

**Bahasa Malaysia:**
```
Hi {{name}}! Anda dihubungi oleh {{brand}} berkaitan pembelian/promosi produk kami.
Dengan membalas YA, anda memberi kebenaran untuk kami menghantar mesej WhatsApp tentang resit, sokongan & promosi. Balas TIDAK untuk menolak.
Anda boleh berhenti pada bila-bila masa dengan taip STOP.
```

**English:**
```
Hi {{name}}! This is {{brand}} about your purchase/promotions.
Reply YES to consent to receive WhatsApp messages for receipts, support & promos. Reply NO to decline.
You can opt out anytime by typing STOP.
```

#### 2. Consent Response Handling

| Response | Action | Database Update |
|----------|--------|-----------------|
| `YES`, `YA`, `SETUJU`, `OK`, `START` | Grant consent | `Consent.status = 'granted'` |
| `NO`, `TAK`, `TDK`, `NOPE`, `STOP`, `BATAL` | Withdraw consent | `Consent.status = 'withdrawn'` |
| `STOP` (anywhere in message) | Opt-out | `Consent.status = 'withdrawn'` |
| `START` (anywhere in message) | Opt-in | `Consent.status = 'granted'` |

#### 3. Consent Confirmation Messages

**Consent Granted:**
- **BM**: "Terima kasih! Kebenaran anda telah direkodkan. Anda boleh taip STOP untuk berhenti pada bila-bila masa."
- **EN**: "Thank you! Your consent has been recorded. You can type STOP anytime to opt out."

**Consent Declined:**
- **BM**: "Baik, kami tidak akan menghantar mesej promosi. Anda masih boleh hubungi kami untuk sokongan."
- **EN**: "Understood. We won't send promotional messages. You can still contact us for support."

---

## 👥 Customer Management Integration

### 1. Automatic Customer Creation

When a new phone number messages the WhatsApp system:

```python
# Customer creation process
customer = Customer.objects.create(
    name=f"Customer {phone_number[-4:]}",
    phone_number=clean_phone,
    tenant=tenant,
    gender='N/A',
    marital_status='N/A'
)
```

### 2. Information Collection Flow

#### IC Number Processing
When customers send their IC number (e.g., `901231-01-1234`):

```python
# Extract information from IC
birth_year = int(ic_number[:2]) + 2000  # Convert to 4-digit year
birth_month = int(ic_number[2:4])
birth_day = int(ic_number[4:6])
gender_code = int(ic_number[7:8])
state_code = int(ic_number[8:10])

# Calculate age
age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))

# Determine gender
gender = 'F' if gender_code % 2 == 0 else 'M'

# Map state code to state
state_mapping = {
    1: 'JHR', 2: 'KDH', 3: 'KTN', 4: 'MLK', 5: 'NSN',
    6: 'PHG', 7: 'PNG', 8: 'PRK', 9: 'SBH', 10: 'SWK',
    11: 'SEL', 12: 'TRG', 13: 'KUL', 14: 'LBN', 15: 'PJY'
}
```

#### Information Collection Prompt
```
📋 Hi! To provide you with better service, please share your information:

1️⃣ **IC Number**: Send your IC number (e.g., 901231-01-1234)
2️⃣ **Gender**: Reply with M (Male), F (Female), or NB (Non-binary)
3️⃣ **Marital Status**: Reply with SINGLE, MARRIED, DIVORCED, or WIDOWED

You can send your IC number first, and I'll automatically extract your age, gender, and state information!
```

### 3. Customer Database Schema

```sql
-- Customer table structure
CREATE TABLE messaging_customer (
    customer_id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES messaging_tenant(tenant_id),
    name TEXT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    ic_number VARCHAR(20),
    age INTEGER,
    gender VARCHAR(10),
    marital_status VARCHAR(20),
    state VARCHAR(10),
    city VARCHAR(100),
    created_at TIMESTAMP,
    last_whatsapp_interaction TIMESTAMP,
    message_count INTEGER DEFAULT 0
);

-- Consent tracking
CREATE TABLE messaging_consent (
    id SERIAL PRIMARY KEY,
    tenant_id UUID REFERENCES messaging_tenant(tenant_id),
    customer_id UUID REFERENCES messaging_customer(customer_id),
    type VARCHAR(20) NOT NULL,  -- 'whatsapp'
    status VARCHAR(20) NOT NULL,  -- 'granted', 'withdrawn'
    occurred_at TIMESTAMP NOT NULL
);
```

---

## 🎯 CRM Integration

### 1. Customer Segmentation

The system automatically segments customers based on:

| Segment | Criteria | Use Case |
|---------|----------|----------|
| **New Customers** | First-time message | Onboarding campaigns |
| **Consented** | `Consent.status = 'granted'` | Marketing campaigns |
| **Opted Out** | `Consent.status = 'withdrawn'` | Service messages only |
| **High Value** | High purchase amount | VIP campaigns |
| **Inactive** | No messages in 30+ days | Re-engagement campaigns |

### 2. CRM Dashboard Features

#### Customer List (`/customers/`)
- **Message Statistics**: Total, inbound, outbound message counts
- **Consent Status**: Visual indicators for consent state
- **Last Message Date**: Recent activity tracking
- **Bulk Operations**: Select and delete multiple customers
- **Filter Options**: By state, gender, marital status

#### Customer Detail (`/customers/{id}/`)
- **Profile Information**: Complete customer demographics
- **Message Timeline**: WhatsApp-style chat history
- **Consent History**: Complete audit trail
- **Statistics**: Message counts and activity metrics

### 3. CRM Campaign Integration

```python
# Campaign targeting based on consent
def get_eligible_customers(tenant, campaign_type):
    if campaign_type == 'marketing':
        return Customer.objects.filter(
            tenant=tenant,
            consents__type='whatsapp',
            consents__status='granted'
        ).distinct()
    elif campaign_type == 'service':
        return Customer.objects.filter(tenant=tenant)
```

---

## 🏆 Contest System Integration

### 1. Contest Creation Flow

```python
# Contest creation with WhatsApp integration
contest = Contest.objects.create(
    tenant=tenant,
    name="Monthly Giveaway",
    description="Win amazing prizes!",
    start_date=timezone.now(),
    end_date=timezone.now() + timedelta(days=30),
    max_entries=1,
    whatsapp_integration=True
)
```

### 2. Contest Entry via WhatsApp

When customers message during an active contest:

```python
# Contest entry processing
def process_contest_entry(customer, message_text, tenant):
    active_contests = Contest.objects.filter(
        tenant=tenant,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        whatsapp_integration=True
    )
    
    for contest in active_contests:
        # Check if customer already entered
        existing_entry = ContestEntry.objects.filter(
            contest=contest,
            customer=customer
        ).first()
        
        if not existing_entry:
            # Create new entry
            ContestEntry.objects.create(
                contest=contest,
                customer=customer,
                entry_text=message_text,
                entry_date=timezone.now()
            )
            
            # Send confirmation
            send_contest_confirmation(customer, contest)
```

### 3. Contest Templates

**Entry Confirmation:**
```
🎉 Contest Entry Confirmed!

Contest: {{contest_name}}
Entry Date: {{entry_date}}
Entry ID: {{entry_id}}

Good luck! Winners will be announced on {{end_date}}.
```

**Winner Notification:**
```
🏆 Congratulations! You Won!

Contest: {{contest_name}}
Prize: {{prize_description}}
Claim Instructions: {{claim_instructions}}

Please contact us to claim your prize!
```

---

## 📢 Bulk Messaging System

### 1. Message Queue Processing

```python
# Bulk message creation
def create_bulk_message(tenant, template, recipients, campaign_type):
    # Check consent for marketing messages
    if campaign_type == 'marketing':
        eligible_customers = get_eligible_customers(tenant, 'marketing')
        recipients = recipients.filter(id__in=eligible_customers)
    
    # Create message queue entries
    for customer in recipients:
        SendQueue.objects.create(
            tenant=tenant,
            customer=customer,
            message_type='whatsapp',
            content=template,
            status='pending',
            scheduled_at=timezone.now()
        )
```

### 2. Message Templates

#### Marketing Templates
```
🎉 Special Offer!

{{customer_name}}, don't miss out on our exclusive deal!

📱 {{offer_description}}
💰 {{discount_amount}}% OFF
⏰ Valid until {{expiry_date}}

Reply STOP to opt out.
```

#### Service Templates
```
🔔 Service Update

{{customer_name}}, here's an important update:

{{service_message}}

Need help? Contact us anytime!
```

### 3. Message Scheduling

```python
# Scheduled message processing
def process_scheduled_messages():
    pending_messages = SendQueue.objects.filter(
        status='pending',
        scheduled_at__lte=timezone.now()
    )
    
    for message in pending_messages:
        # Check consent before sending
        if message.message_type == 'marketing':
            consent_status = get_consent_status(
                message.tenant, 
                message.customer, 
                'whatsapp'
            )
            if consent_status != 'granted':
                message.status = 'skipped'
                message.save()
                continue
        
        # Send message
        result = send_whatsapp_message(message.customer, message.content)
        if result['success']:
            message.status = 'sent'
        else:
            message.status = 'failed'
        message.save()
```

---

## 🔧 Technical Implementation

### 1. Webhook Handler

```python
# WhatsApp webhook processing
class WhatsAppWebhookView(View):
    def post(self, request):
        data = json.loads(request.body)
        
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    self._handle_message_changes(change['value'])
        
        return JsonResponse({'status': 'success'})
    
    def _process_incoming_message(self, message_data):
        # Extract message details
        from_number = message_data.get('from')
        text_content = message_data.get('text', {}).get('body', '')
        
        # Get or create customer
        customer = self._get_or_create_contact(from_number)
        
        # Process through PDPA service
        pdpa_service = PDPAConsentService()
        pdpa_service.handle_incoming_message(customer, text_content)
```

### 2. Database Models

```python
# Core message model
class CoreMessage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10)  # 'inbound', 'outbound'
    status = models.CharField(max_length=20)  # 'sent', 'delivered', 'read'
    text_body = models.TextField()
    provider_msg_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

# Consent tracking
class Consent(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=20)  # 'whatsapp'
    status = models.CharField(max_length=20)  # 'granted', 'withdrawn'
    occurred_at = models.DateTimeField(auto_now_add=True)
```

### 3. API Integration

```python
# WhatsApp API service
class WhatsAppAPIService:
    def send_text_message(self, phone_number, message_text):
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message_text}
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
```

---

## 📊 Analytics & Reporting

### 1. Message Statistics

```python
# Message analytics
def get_message_analytics(tenant, date_range):
    return {
        'total_messages': CoreMessage.objects.filter(
            tenant=tenant,
            created_at__range=date_range
        ).count(),
        'inbound_messages': CoreMessage.objects.filter(
            tenant=tenant,
            direction='inbound',
            created_at__range=date_range
        ).count(),
        'outbound_messages': CoreMessage.objects.filter(
            tenant=tenant,
            direction='outbound',
            created_at__range=date_range
        ).count(),
        'consent_rate': calculate_consent_rate(tenant, date_range),
        'opt_out_rate': calculate_opt_out_rate(tenant, date_range)
    }
```

### 2. Customer Engagement Metrics

| Metric | Description | Calculation |
|--------|-------------|-------------|
| **Message Volume** | Total messages sent/received | `COUNT(CoreMessage)` |
| **Response Rate** | Customer response percentage | `Inbound / Outbound * 100` |
| **Consent Rate** | Percentage with granted consent | `Granted / Total * 100` |
| **Opt-out Rate** | Percentage who opted out | `Withdrawn / Total * 100` |
| **Engagement Score** | Customer activity level | `Messages in last 30 days` |

---

## 🚀 Deployment & Configuration

### 1. Environment Variables

```bash
# WhatsApp API Configuration
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_verify_token
WHATSAPP_BASE_URL=https://app.wabot.my/api

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/whatsapp_bulk

# Cloudinary Configuration (for media)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 2. Webhook Setup

```python
# Webhook URL configuration
WEBHOOK_URL = "https://yourdomain.com/webhook/whatsapp/"
VERIFY_TOKEN = "your_verify_token"

# WhatsApp webhook verification
def verify_webhook(request):
    verify_token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    
    if verify_token == VERIFY_TOKEN:
        return HttpResponse(challenge)
    else:
        return HttpResponse('Verification failed', status=403)
```

### 3. Message Processing Queue

```python
# Celery task for message processing
@shared_task
def process_whatsapp_message(message_id):
    message = CoreMessage.objects.get(id=message_id)
    
    # Process through PDPA service
    pdpa_service = PDPAConsentService()
    pdpa_service.handle_incoming_message(
        message.conversation.customer,
        message.text_body,
        message.tenant
    )
```

---

## 🧪 Testing & Development

### 1. Management Commands

```bash
# Test PDPA flow
python manage.py test_pdpa --customer-phone 60162107682 --message "hello"

# Test consent responses
python manage.py test_pdpa --customer-phone 60162107682 --message "yes"
python manage.py test_pdpa --customer-phone 60162107682 --message "stop"

# Clear consent history
python manage.py test_pdpa --action clear-consent --customer-phone 60162107682

# Show consent history
python manage.py test_pdpa --action show-consent --customer-phone 60162107682
```

### 2. Test Scenarios

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| **First Contact** | "hello" | PDPA consent templates sent |
| **Consent Yes** | "yes" | Consent granted confirmation |
| **Consent No** | "no" | Consent declined confirmation |
| **Opt-out** | "stop" | Opt-out confirmation |
| **IC Processing** | "901231-01-1234" | Demographics extracted and saved |
| **Contest Entry** | Any message during contest | Contest entry created |

---

## 🔒 Security & Compliance

### 1. PDPA Compliance Features

- **Explicit Consent**: Clear consent request with purpose
- **Opt-out Mechanism**: Easy STOP command functionality
- **Data Minimization**: Only collect necessary information
- **Audit Trail**: Complete consent history tracking
- **Data Retention**: Configurable data retention policies

### 2. Security Measures

- **CSRF Protection**: All forms protected with CSRF tokens
- **Tenant Isolation**: Users can only access their own data
- **Input Validation**: All inputs validated and sanitized
- **Rate Limiting**: Prevent message spam
- **Encryption**: Sensitive data encrypted at rest

### 3. Privacy Controls

```python
# Data anonymization for compliance
def anonymize_customer_data(customer):
    customer.name = f"Customer {customer.customer_id[:8]}"
    customer.ic_number = None
    customer.phone_number = f"***{customer.phone_number[-4:]}"
    customer.save()
```

---

## 📈 Performance Optimization

### 1. Database Optimization

```python
# Efficient queries with select_related
customers = Customer.objects.select_related('tenant').filter(
    tenant=tenant
).prefetch_related('consents', 'conversations__messages')

# Message statistics with annotations
customers_with_stats = customers.annotate(
    total_messages=Count('conversations__messages'),
    inbound_messages=Count('conversations__messages', 
                          filter=Q(conversations__messages__direction='inbound')),
    outbound_messages=Count('conversations__messages', 
                           filter=Q(conversations__messages__direction='outbound'))
)
```

### 2. Caching Strategy

```python
# Redis caching for frequently accessed data
from django.core.cache import cache

def get_customer_consent_status(customer_id):
    cache_key = f"consent_status_{customer_id}"
    consent_status = cache.get(cache_key)
    
    if not consent_status:
        consent_status = Consent.objects.filter(
            customer_id=customer_id,
            type='whatsapp'
        ).order_by('-occurred_at').first()
        cache.set(cache_key, consent_status, 300)  # 5 minutes
    
    return consent_status
```

---

## 🚨 Error Handling & Monitoring

### 1. Error Logging

```python
import logging

logger = logging.getLogger(__name__)

def handle_whatsapp_error(error, customer, message):
    logger.error(f"WhatsApp error for customer {customer.phone_number}: {error}")
    
    # Send error notification to admin
    send_admin_notification(
        f"WhatsApp error: {error}",
        customer=customer,
        message=message
    )
```

### 2. Health Checks

```python
# System health monitoring
def check_whatsapp_health():
    try:
        # Test WhatsApp API connection
        wa_service = WhatsAppAPIService()
        result = wa_service.get_phone_number_info()
        
        return {
            'status': 'healthy',
            'whatsapp_api': 'connected',
            'database': 'connected',
            'timestamp': timezone.now()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now()
        }
```

---

## 📚 API Reference

### 1. Webhook Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/whatsapp/` | POST | Receive WhatsApp messages |
| `/webhook/whatsapp/` | GET | Webhook verification |

### 2. Customer Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/customers/` | GET | List all customers |
| `/customers/{id}/` | GET | Get customer details |
| `/customers/{id}/` | DELETE | Delete customer |
| `/bulk-delete-customers/` | POST | Bulk delete customers |

### 3. PDPA Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings/pdpa/` | GET | PDPA settings dashboard |
| `/customers/{id}/consent/` | POST | Update consent status |

---

## 🔄 Integration Workflow

### 1. Complete Customer Journey

```mermaid
sequenceDiagram
    participant C as Customer
    participant W as WhatsApp
    participant S as System
    participant D as Database
    
    C->>W: Sends "hello"
    W->>S: Webhook notification
    S->>D: Create customer record
    S->>W: Send PDPA templates
    W->>C: Consent request
    
    C->>W: Replies "yes"
    W->>S: Webhook notification
    S->>D: Update consent status
    S->>W: Send confirmation
    W->>C: Consent confirmed
    
    C->>W: Sends IC number
    W->>S: Webhook notification
    S->>D: Extract & save demographics
    S->>W: Send confirmation
    W->>C: Profile updated
    
    C->>W: Sends contest message
    W->>S: Webhook notification
    S->>D: Create contest entry
    S->>W: Send confirmation
    W->>C: Entry confirmed
```

### 2. Campaign Flow

```mermaid
sequenceDiagram
    participant A as Admin
    participant S as System
    participant D as Database
    participant W as WhatsApp
    participant C as Customer
    
    A->>S: Create campaign
    S->>D: Save campaign
    A->>S: Select recipients
    S->>D: Check consent status
    S->>D: Create message queue
    S->>W: Send messages
    W->>C: Receive campaign
    C->>W: Responds
    W->>S: Webhook notification
    S->>D: Update engagement
```

---

## 📋 Troubleshooting Guide

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Webhook not receiving messages** | Incorrect webhook URL | Verify webhook URL in WhatsApp settings |
| **Consent not being recorded** | Database connection issue | Check database connectivity |
| **Messages not sending** | Invalid access token | Verify WhatsApp API credentials |
| **Customer not created** | Tenant not found | Ensure tenant exists in database |
| **IC processing failing** | Invalid IC format | Check IC number format validation |

### Debug Commands

```bash
# Check system health
python manage.py check

# Test PDPA flow
python manage.py test_pdpa --customer-phone 60162107682 --message "hello"

# View logs
tail -f logs/whatsapp.log

# Check database
python manage.py dbshell
```

---

## 🎯 Best Practices

### 1. Message Design
- Keep messages concise and clear
- Include opt-out instructions
- Use emojis sparingly
- Test messages before sending

### 2. Consent Management
- Always request explicit consent
- Provide clear opt-out mechanism
- Maintain consent audit trail
- Respect customer preferences

### 3. Performance
- Use database indexes for frequent queries
- Implement caching for static data
- Monitor message queue processing
- Set up proper error handling

### 4. Security
- Validate all inputs
- Use CSRF protection
- Implement rate limiting
- Encrypt sensitive data

---

## 📞 Support & Maintenance

### 1. Monitoring
- Set up alerts for failed messages
- Monitor consent rates
- Track customer engagement
- Watch for system errors

### 2. Maintenance Tasks
- Regular database cleanup
- Update WhatsApp API credentials
- Monitor webhook health
- Review consent compliance

### 3. Updates
- Keep WhatsApp API version current
- Update PDPA templates as needed
- Monitor regulatory changes
- Test new features thoroughly

---

*This documentation is maintained and updated regularly. For the latest version, please check the project repository.*
