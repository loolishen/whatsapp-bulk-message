from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal
import re
from datetime import datetime, date

class Contact(models.Model):
    GENDER_CHOICES = [
        ('N/A', 'N/A'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('PNS', 'Prefer not to say'),
    ]
    
    RACE_CHOICES = [
        ('N/A', 'N/A'),
        ('MAL', 'Malay'),
        ('CHN', 'Chinese'),
        ('IND', 'Indian'),
        ('BUM', 'Bumiputera (Sabah/Sarawak)'),
        ('OAS', 'Orang Asli'),
        ('OTH', 'Other'),
    ]
    
    STATE_CHOICES = [
        ('N/A', 'N/A'),
        ('JHR', 'Johor'),
        ('KDH', 'Kedah'),
        ('KTN', 'Kelantan'),
        ('KUL', 'Kuala Lumpur'),
        ('LBN', 'Labuan'),
        ('MLK', 'Melaka'),
        ('NSN', 'Negeri Sembilan'),
        ('PHG', 'Pahang'),
        ('PNG', 'Penang'),
        ('PRK', 'Perak'),
        ('PLS', 'Perlis'),
        ('PJY', 'Putrajaya'),
        ('SBH', 'Sabah'),
        ('SWK', 'Sarawak'),
        ('SEL', 'Selangor'),
        ('TRG', 'Terengganu'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('N/A', 'N/A'),
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    ic_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        validators=[RegexValidator(
            regex=r'^\d{12}$',
            message='IC number must be 12 digits'
        )],
        help_text='Malaysian IC number (12 digits)'
    )
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='N/A')
    gender = models.CharField(max_length=5, choices=GENDER_CHOICES, default='N/A')
    race = models.CharField(max_length=20, choices=RACE_CHOICES, default='N/A')
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, default='N/A')
    age = models.IntegerField(blank=True, null=True, help_text='Calculated from IC number')
    date_of_birth = models.DateField(blank=True, null=True, help_text='Extracted from IC number')
    
    # Purchase tracking
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    average_spend = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    purchase_count = models.IntegerField(default=0)
    last_purchase_date = models.DateField(blank=True, null=True)
    
    # Customer segmentation
    customer_tier = models.CharField(max_length=20, default='BRONZE', choices=[
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ])
    
    # WhatsApp interaction tracking
    whatsapp_status = models.CharField(max_length=20, default='ACTIVE', choices=[
        ('ACTIVE', 'Active'),
        ('BLOCKED', 'Blocked'),
        ('UNSUBSCRIBED', 'Unsubscribed'),
        ('INVALID', 'Invalid Number'),
    ])
    last_whatsapp_interaction = models.DateTimeField(blank=True, null=True)
    message_count = models.IntegerField(default=0)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Original fields
    event_source = models.CharField(max_length=100, default='N/A', help_text='Source event (e.g., Event A, Event B, Manual Entry)')
    event_date = models.DateField(blank=True, null=True, help_text='Date when the event was carried out')
    events_participated = models.TextField(blank=True, default='', help_text='Comma-separated list of events participated')
    events_count = models.IntegerField(default=1, help_text='Number of different events participated in')
    date_added = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
    
    def calculate_age_from_ic(self):
        """Calculate age from Malaysian IC number"""
        if not self.ic_number or len(self.ic_number) != 12:
            return None
        
        try:
            # Extract birth year from IC (first 2 digits)
            birth_year = int(self.ic_number[:2])
            birth_month = int(self.ic_number[2:4])
            birth_day = int(self.ic_number[4:6])
            
            # Handle year conversion (00-30 = 2000-2030, 31-99 = 1931-1999)
            if birth_year <= 30:
                birth_year += 2000
            else:
                birth_year += 1900
            
            # Create date object
            birth_date = date(birth_year, birth_month, birth_day)
            today = date.today()
            
            # Calculate age
            age = today.year - birth_date.year
            if today.month < birth_month or (today.month == birth_month and today.day < birth_day):
                age -= 1
            
            return age
        except (ValueError, TypeError):
            return None
    
    def extract_gender_from_ic(self):
        """Extract gender from Malaysian IC number (last digit)"""
        if not self.ic_number or len(self.ic_number) != 12:
            return 'N/A'
        
        last_digit = int(self.ic_number[-1])
        return 'M' if last_digit % 2 == 1 else 'F'
    
    def extract_state_from_ic(self):
        """Extract state from Malaysian IC number (digits 7-8)"""
        if not self.ic_number or len(self.ic_number) != 12:
            return 'N/A'
        
        state_code = self.ic_number[6:8]
        state_mapping = {
            '01': 'JHR', '02': 'KDH', '03': 'KTN', '04': 'MLK', '05': 'NSN',
            '06': 'PHG', '07': 'PNG', '08': 'PRK', '09': 'PLS', '10': 'SEL',
            '11': 'TRG', '12': 'SBH', '13': 'SWK', '14': 'KUL', '15': 'LBN',
            '16': 'PJY'
        }
        return state_mapping.get(state_code, 'N/A')
    
    def update_customer_tier(self):
        """Update customer tier based on total spending"""
        if self.total_spent >= 1000:
            self.customer_tier = 'PLATINUM'
        elif self.total_spent >= 500:
            self.customer_tier = 'GOLD'
        elif self.total_spent >= 200:
            self.customer_tier = 'SILVER'
        else:
            self.customer_tier = 'BRONZE'
    
    def save(self, *args, **kwargs):
        # Auto-extract information from IC if provided
        if self.ic_number:
            if not self.age:
                self.age = self.calculate_age_from_ic()
            if self.gender == 'N/A':
                self.gender = self.extract_gender_from_ic()
            if self.state == 'N/A':
                self.state = self.extract_state_from_ic()
            
            # Extract date of birth
            if not self.date_of_birth and self.ic_number:
                try:
                    birth_year = int(self.ic_number[:2])
                    birth_month = int(self.ic_number[2:4])
                    birth_day = int(self.ic_number[4:6])
                    
                    if birth_year <= 30:
                        birth_year += 2000
                    else:
                        birth_year += 1900
                    
                    self.date_of_birth = date(birth_year, birth_month, birth_day)
                except (ValueError, TypeError):
                    pass
        
        # Update customer tier
        self.update_customer_tier()
        
        super().save(*args, **kwargs)

class Message(models.Model):
    text_content = models.TextField()
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message created at {self.created_at}"

class BulkMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Contact)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Bulk message to {self.recipients.count()} recipients"


class Purchase(models.Model):
    """Model to track customer purchases from receipts"""
    customer = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='purchases')
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    receipt_text = models.TextField(blank=True, help_text='OCR extracted text from receipt')
    
    # Purchase details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    items = models.JSONField(default=list, help_text='List of purchased items')
    
    # OCR processing status
    ocr_processed = models.BooleanField(default=False)
    ocr_confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    ocr_errors = models.TextField(blank=True, help_text='Any OCR processing errors')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer.name} - RM{self.total_amount} on {self.purchase_date}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update customer's purchase statistics
        self.customer.purchase_count = self.customer.purchases.count()
        self.customer.total_spent = sum(p.total_amount for p in self.customer.purchases.all())
        self.customer.average_spend = (
            self.customer.total_spent / self.customer.purchase_count 
            if self.customer.purchase_count > 0 else Decimal('0.00')
        )
        self.customer.last_purchase_date = self.purchase_date
        self.customer.save()


class CustomerSegment(models.Model):
    """Model for customer segmentation"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Segmentation criteria
    min_spending = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_spending = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    min_age = models.IntegerField(blank=True, null=True)
    max_age = models.IntegerField(blank=True, null=True)
    gender_filter = models.CharField(max_length=5, choices=Contact.GENDER_CHOICES, default='N/A')
    marital_status_filter = models.CharField(max_length=10, choices=Contact.MARITAL_STATUS_CHOICES, default='N/A')
    state_filter = models.CharField(max_length=20, choices=Contact.STATE_CHOICES, default='N/A')
    customer_tier_filter = models.CharField(max_length=20, choices=[
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ], default='')
    
    # Custom filters
    custom_filters = models.JSONField(default=dict, help_text='Additional custom filtering criteria')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_customers(self):
        """Get customers matching this segment's criteria"""
        queryset = Contact.objects.all()
        
        if self.min_spending is not None:
            queryset = queryset.filter(total_spent__gte=self.min_spending)
        if self.max_spending is not None:
            queryset = queryset.filter(total_spent__lte=self.max_spending)
        if self.min_age is not None:
            queryset = queryset.filter(age__gte=self.min_age)
        if self.max_age is not None:
            queryset = queryset.filter(age__lte=self.max_age)
        if self.gender_filter != 'N/A':
            queryset = queryset.filter(gender=self.gender_filter)
        if self.marital_status_filter != 'N/A':
            queryset = queryset.filter(marital_status=self.marital_status_filter)
        if self.state_filter != 'N/A':
            queryset = queryset.filter(state=self.state_filter)
        if self.customer_tier_filter:
            queryset = queryset.filter(customer_tier=self.customer_tier_filter)
        
        return queryset
    
    def get_customer_count(self):
        """Get count of customers in this segment"""
        return self.get_customers().count()


class Campaign(models.Model):
    """Model for WhatsApp campaigns"""
    CAMPAIGN_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    CAMPAIGN_OBJECTIVE_CHOICES = [
        ('RETENTION', 'Customer Retention'),
        ('ACQUISITION', 'New Customer Acquisition'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('RE_ENGAGEMENT', 'Re-engagement'),
        ('PROMOTION', 'Promotion'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    objective = models.CharField(max_length=20, choices=CAMPAIGN_OBJECTIVE_CHOICES)
    
    # Targeting
    segments = models.ManyToManyField(CustomerSegment, blank=True)
    custom_recipients = models.ManyToManyField(Contact, blank=True, related_name='custom_campaigns')
    
    # Content
    message_text = models.TextField()
    media_image = models.ImageField(upload_to='campaign_media/', blank=True, null=True)
    media_video = models.FileField(upload_to='campaign_media/', blank=True, null=True)
    
    # Scheduling
    scheduled_start = models.DateTimeField(blank=True, null=True)
    scheduled_end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS_CHOICES, default='DRAFT')
    
    # Tracking
    landing_url = models.URLField(blank=True, null=True)
    tracking_pixel = models.CharField(max_length=100, blank=True, null=True)
    
    # Results
    total_sent = models.IntegerField(default=0)
    total_delivered = models.IntegerField(default=0)
    total_read = models.IntegerField(default=0)
    total_clicked = models.IntegerField(default=0)
    total_converted = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_total_recipients(self):
        """Get total number of recipients for this campaign"""
        total = 0
        for segment in self.segments.all():
            total += segment.get_customer_count()
        total += self.custom_recipients.count()
        return total


class WhatsAppMessage(models.Model):
    """Model to track individual WhatsApp messages"""
    MESSAGE_TYPE_CHOICES = [
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    ]
    
    MESSAGE_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('READ', 'Read'),
        ('FAILED', 'Failed'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, blank=True, null=True, related_name='messages')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='whatsapp_messages')
    
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    message_text = models.TextField()
    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=20, blank=True, null=True)  # image, video, document
    
    # WhatsApp API tracking
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=MESSAGE_STATUS_CHOICES, default='PENDING')
    
    # Timestamps
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Interaction tracking
    clicked_links = models.JSONField(default=list, help_text='List of clicked links')
    viewed_media = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.contact.name} - {self.message_type} - {self.status}"


class OCRProcessingLog(models.Model):
    """Model to track OCR processing of images"""
    PROCESSING_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    image_url = models.URLField()
    image_type = models.CharField(max_length=20, choices=[
        ('IC', 'IC Card'),
        ('RECEIPT', 'Receipt'),
        ('OTHER', 'Other'),
    ])
    
    # Processing details
    status = models.CharField(max_length=20, choices=PROCESSING_STATUS_CHOICES, default='PENDING')
    extracted_text = models.TextField(blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    processing_errors = models.TextField(blank=True)
    
    # Extracted data
    extracted_data = models.JSONField(default=dict, help_text='Structured data extracted from image')
    
    # Related objects
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"OCR {self.image_type} - {self.status} - {self.created_at}"
