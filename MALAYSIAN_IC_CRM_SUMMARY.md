# Malaysian IC-Based WhatsApp CRM System

## Overview
This enhanced WhatsApp CRM system is specifically designed for Malaysian businesses to manage customer relationships using Malaysian IC (Identity Card) data, purchase history tracking, and automated WhatsApp interactions.

## Key Features Implemented

### 1. Malaysian IC Data Processing
- **IC Number Validation**: 12-digit Malaysian IC number validation
- **Automatic Data Extraction**: 
  - Age calculation from birth date
  - Gender determination (odd/even last digit)
  - State extraction from IC number
  - Date of birth parsing
- **IC Parser Service**: `MalaysianICParser` class with comprehensive IC number analysis

### 2. OCR Integration
- **Image Processing**: OCR service for IC cards and receipts
- **Text Extraction**: Automatic text extraction from images
- **Data Parsing**: Structured data extraction from OCR results
- **Confidence Scoring**: OCR confidence levels for quality control

### 3. WhatsApp Webhook System
- **Message Reception**: Handle incoming WhatsApp messages, images, and documents
- **Auto-Response**: Intelligent auto-responses based on message content
- **Media Processing**: Download and process images/documents from WhatsApp
- **Status Tracking**: Message delivery and read status tracking

### 4. Purchase History Management
- **Receipt Processing**: OCR-based receipt text extraction
- **Purchase Tracking**: Individual purchase records with items and amounts
- **Spending Analytics**: Total spent, average spend, purchase count
- **Customer Tiers**: Automatic tier assignment (Bronze, Silver, Gold, Platinum)

### 5. Customer Segmentation
- **Multi-Criteria Segmentation**:
  - Spending ranges (min/max)
  - Age groups
  - Gender
  - Marital status
  - State/region
  - Customer tier
- **Dynamic Segments**: Real-time customer count updates
- **Custom Filters**: JSON-based custom filtering criteria

### 6. Campaign Management
- **Campaign Creation**: Multi-step campaign builder
- **Targeting**: Segment-based and custom recipient targeting
- **Content Management**: Text, image, and video message support
- **Scheduling**: Start/end date scheduling
- **Tracking**: Comprehensive campaign performance metrics

### 7. Enhanced Analytics
- **Customer Insights**: Purchase patterns, spending behavior
- **Demographics**: Age, gender, state distribution
- **Campaign Performance**: Delivery, read, click, conversion rates
- **Purchase Analytics**: Revenue trends, customer lifetime value

## Database Structure

### Core Models

#### Contact (Enhanced)
```python
- name: Customer name
- phone_number: WhatsApp number
- ic_number: Malaysian IC (12 digits)
- age: Calculated from IC
- gender: Extracted from IC
- state: Extracted from IC
- marital_status: Customer marital status
- date_of_birth: Extracted from IC
- total_spent: Sum of all purchases
- average_spend: Average per purchase
- purchase_count: Number of purchases
- customer_tier: Bronze/Silver/Gold/Platinum
- whatsapp_status: Active/Blocked/Unsubscribed
- last_whatsapp_interaction: Last message timestamp
- message_count: Total messages sent
- response_rate: Customer response percentage
```

#### Purchase
```python
- customer: Foreign key to Contact
- receipt_image: Receipt image file
- receipt_text: OCR extracted text
- total_amount: Purchase amount
- purchase_date: Date of purchase
- items: JSON list of purchased items
- ocr_processed: OCR completion status
- ocr_confidence: OCR confidence score
```

#### CustomerSegment
```python
- name: Segment name
- description: Segment description
- min_spending/max_spending: Spending filters
- min_age/max_age: Age filters
- gender_filter: Gender filter
- marital_status_filter: Marital status filter
- state_filter: State filter
- customer_tier_filter: Tier filter
- custom_filters: JSON custom criteria
```

#### Campaign
```python
- name: Campaign name
- objective: Campaign goal
- segments: Many-to-many with CustomerSegment
- custom_recipients: Many-to-many with Contact
- message_text: Campaign message
- media_image/media_video: Campaign media
- scheduled_start/scheduled_end: Campaign timing
- status: Draft/Scheduled/Running/Completed
- tracking metrics: sent, delivered, read, clicked, converted
```

#### WhatsAppMessage
```python
- campaign: Foreign key to Campaign
- contact: Foreign key to Contact
- message_type: Sent/Received
- message_text: Message content
- media_url: Media file URL
- whatsapp_message_id: WhatsApp API message ID
- status: Pending/Sent/Delivered/Read/Failed
- timestamps: sent_at, delivered_at, read_at
- interaction_tracking: clicked_links, viewed_media
```

#### OCRProcessingLog
```python
- image_url: Processed image URL
- image_type: IC/Receipt/Other
- status: Processing status
- extracted_text: OCR text result
- confidence_score: OCR confidence
- extracted_data: Structured data
- contact/purchase: Related objects
```

## API Endpoints

### Campaign Management
- `GET /api/campaigns/` - List all campaigns
- `POST /api/campaigns/create/` - Create new campaign
- `GET /api/campaigns/<id>/` - Get campaign details

### Customer Segmentation
- `GET /api/segments/` - List all segments
- `POST /api/segments/create/` - Create new segment
- `GET /api/segments/<id>/` - Get segment details and customers

### Customer Data
- `GET /api/customers/<id>/purchases/` - Get customer purchase history

### OCR Processing
- `POST /api/ocr/process/` - Process image with OCR

### WhatsApp Webhook
- `POST /webhook/whatsapp/` - Receive WhatsApp messages
- `GET /webhook/whatsapp/` - Webhook verification

## Usage Workflow

### 1. Customer Registration
1. Customer sends IC photo via WhatsApp
2. Webhook receives image and triggers OCR
3. IC data is extracted and parsed
4. Contact record is created/updated
5. Confirmation message sent to customer

### 2. Purchase Tracking
1. Customer sends receipt photo via WhatsApp
2. OCR extracts purchase information
3. Purchase record is created
4. Customer spending statistics updated
5. Customer tier recalculated
6. Confirmation message sent

### 3. Campaign Creation
1. Create customer segments based on criteria
2. Design campaign message and media
3. Schedule campaign timing
4. Target specific segments or custom recipients
5. Launch campaign and track performance

### 4. Analytics and Reporting
1. View customer demographics and spending patterns
2. Analyze campaign performance metrics
3. Track purchase history and trends
4. Monitor customer engagement levels

## Technical Implementation

### OCR Service
- **MalaysianICParser**: Handles IC number parsing and validation
- **ReceiptParser**: Extracts purchase data from receipt text
- **OCRService**: Main OCR processing service with image type detection

### WhatsApp Integration
- **WhatsAppAPIService**: Enhanced with media handling and webhook support
- **WhatsAppWebhookView**: Handles incoming messages and status updates
- **Auto-Response System**: Intelligent message routing and responses

### Data Processing
- **Automatic IC Parsing**: Real-time IC data extraction
- **Purchase Analytics**: Automatic spending calculations
- **Customer Segmentation**: Dynamic segment updates
- **Campaign Tracking**: Real-time performance metrics

## Configuration

### Required Settings
```python
WHATSAPP_API = {
    'ACCESS_TOKEN': 'your_access_token',
    'BASE_URL': 'https://app.wabot.my/api',
    'DEFAULT_INSTANCE_ID': 'your_instance_id',
}

CLOUDINARY = {
    'CLOUD_NAME': 'your_cloud_name',
    'API_KEY': 'your_api_key',
    'API_SECRET': 'your_api_secret',
}

WHATSAPP_WEBHOOK_VERIFY_TOKEN = 'your_verify_token'
```

### Dependencies
- Django 4.2.7
- Cloudinary for image storage
- Pandas for data processing
- OpenCV and Tesseract for OCR
- Celery for background tasks
- Redis for task queue

## Security and Compliance

### Data Protection
- IC number validation and secure storage
- GDPR/PDPA compliance considerations
- Secure image processing and storage
- Webhook verification and authentication

### Privacy Features
- Customer consent tracking
- Data retention policies
- Secure API endpoints
- Encrypted data transmission

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Machine learning for customer behavior prediction
2. **Multi-language Support**: Bahasa Malaysia and Chinese language support
3. **Integration APIs**: Connect with external POS systems
4. **Mobile App**: Native mobile application for customers
5. **Advanced Segmentation**: AI-powered customer segmentation
6. **Automated Campaigns**: Trigger-based automated messaging
7. **Loyalty Programs**: Points and rewards system integration

### Scalability Considerations
- Database optimization for large customer bases
- Caching strategies for improved performance
- Background task processing for OCR operations
- CDN integration for media delivery
- Load balancing for high-traffic scenarios

## Getting Started

1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Configure Settings**: Update WhatsApp and Cloudinary credentials
3. **Run Migrations**: `python manage.py migrate`
4. **Set Webhook**: Configure WhatsApp webhook URL
5. **Test OCR**: Upload sample IC and receipt images
6. **Create Segments**: Set up initial customer segments
7. **Launch Campaigns**: Start with simple text campaigns

## Support and Maintenance

### Monitoring
- OCR processing success rates
- WhatsApp message delivery rates
- Campaign performance metrics
- Customer engagement levels

### Troubleshooting
- OCR accuracy issues
- WhatsApp API connectivity
- Image processing errors
- Database performance optimization

This comprehensive CRM system provides a complete solution for Malaysian businesses to manage customer relationships through WhatsApp, with automated IC processing, purchase tracking, and intelligent campaign management.
