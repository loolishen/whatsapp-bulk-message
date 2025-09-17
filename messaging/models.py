from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal
import re
import uuid
from datetime import datetime, date
from django.utils import timezone as dj_timezone

# =============================================================================
# MULTI-TENANT CORE MODELS
# =============================================================================

class Tenant(models.Model):
    """Multi-tenant organization model"""
    tenant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    plan = models.TextField()
    creation_date = models.DateTimeField(default=dj_timezone.now)
    company_address = models.TextField(blank=True, null=True)
    company_registration_number = models.TextField(blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_phone_number = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class WhatsAppConnection(models.Model):
    """WhatsApp connection per tenant"""
    PROVIDER_CHOICES = [
        ('wabot', 'WABot'),
        ('meta', 'Meta Business API'),
        ('twilio', 'Twilio'),
    ]
    
    whatsapp_connection_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='whatsapp_connections')
    phone_number = models.TextField()
    access_token_ref = models.TextField(help_text='Reference to secret manager, not raw token')
    instance_id = models.TextField()
    provider = models.TextField(choices=PROVIDER_CHOICES, default='wabot')
    
    def __str__(self):
        return f"{self.tenant.name} - {self.phone_number} ({self.provider})"

# =============================================================================
# CUSTOMER MANAGEMENT MODELS
# =============================================================================

class TenantUser(models.Model):
    """Link Django auth user to a Tenant with a role/plan cache."""
    from django.contrib.auth import get_user_model
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='tenant_profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    role = models.TextField(default='member')  # owner/admin/member
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.user.username} @ {self.tenant.name}"

class Customer(models.Model):
    """Customer model with multi-tenancy"""
    GENDER_CHOICES = [
        ('N/A', 'N/A'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('NB', 'Non-binary'),
        ('PNS', 'Prefer not to say'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('N/A', 'N/A'),
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]

    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='customers')
    name = models.TextField()
    phone_number = models.TextField()
    ic_number = models.TextField(blank=True, null=True, help_text='Encrypted IC number')
    gender = models.TextField(choices=GENDER_CHOICES, default='N/A')
    marital_status = models.TextField(choices=MARITAL_STATUS_CHOICES, default='N/A')
    age = models.IntegerField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    
    # OCR-extracted information
    nric = models.TextField(blank=True, null=True, help_text='NRIC extracted from OCR')
    address = models.TextField(blank=True, null=True, help_text='Address extracted from OCR')
    store_name = models.TextField(blank=True, null=True, help_text='Store name from receipt OCR')
    store_location = models.TextField(blank=True, null=True, help_text='Store location from receipt OCR')
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Total amount spent from receipt')
    products_purchased = models.JSONField(default=list, blank=True, help_text='Products purchased from receipt OCR')
    last_receipt_date = models.DateTimeField(blank=True, null=True, help_text='Date of last receipt processed')
    ocr_confidence = models.FloatField(blank=True, null=True, help_text='OCR confidence score')
    
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
    
class Consent(models.Model):
    """Customer consent management"""
    CONSENT_TYPE_CHOICES = [
        ('pdpa', 'PDPA'),
        ('marketing', 'Marketing'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]
    
    STATUS_CHOICES = [
        ('granted', 'Granted'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    consent_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='consents')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='consents')
    type = models.TextField(choices=CONSENT_TYPE_CHOICES)
    status = models.TextField(choices=STATUS_CHOICES)
    occurred_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.customer.name} - {self.type} - {self.status}"

# =============================================================================
# CONVERSATION AND MESSAGING MODELS
# =============================================================================

class Conversation(models.Model):
    """Conversation between customer and WhatsApp connection"""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='conversations')
    whatsapp_connection = models.ForeignKey(WhatsAppConnection, on_delete=models.CASCADE, related_name='conversations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
    channel = models.TextField(default='whatsapp')
    # Optional contest linkage to scope conversations to a contest
    # (defined below; forward reference via string)
    contest = models.ForeignKey('Contest', on_delete=models.SET_NULL, blank=True, null=True, related_name='conversations')
    last_message_at = models.DateTimeField(blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.customer.name} - {self.whatsapp_connection.phone_number}"

class CoreMessage(models.Model):
    """Individual message in a conversation"""
    DIRECTION_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', blank=True, null=True)
    direction = models.TextField(choices=DIRECTION_CHOICES, blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='queued')
    text_body = models.TextField(blank=True, null=True)
    provider_msg_id = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.direction} - {self.status} - {self.created_at}"

    class Meta:
        db_table = 'messages'

class MessageAttachment(models.Model):
    """Attachments for messages"""
    KIND_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]
    
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attachments')
    message = models.ForeignKey(CoreMessage, on_delete=models.CASCADE, related_name='attachments')
    kind = models.TextField(choices=KIND_CHOICES)
    storage_path = models.TextField()
    mime_type = models.TextField()
    bytes_size = models.BigIntegerField()
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.kind} - {self.message.message_id}"

# =============================================================================
# RECEIPT AND OCR MODELS
# =============================================================================

class Receipt(models.Model):
    """Receipt tracking with OCR data"""
    receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='receipts')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='receipts')
    purchase_date = models.DateTimeField()
    subtotal = models.IntegerField()  # Store in cents
    discount = models.IntegerField(default=0)  # Store in cents
    tax = models.IntegerField(default=0)  # Store in cents
    total = models.IntegerField()  # Store in cents
    ocr_confidence = models.FloatField(blank=True, null=True)
    source_image_path = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.customer.name} - RM{self.total/100:.2f} - {self.purchase_date}"

class ReceiptItem(models.Model):
    """Individual items in a receipt"""
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='receipt_items')
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    description = models.TextField()
    qty = models.IntegerField()
    unit_price = models.IntegerField()  # Store in cents
    
    def __str__(self):
        return f"{self.description} x{self.qty} - RM{self.unit_price/100:.2f}"

# =============================================================================
# TEMPLATE AND CAMPAIGN MODELS
# =============================================================================

class TemplateMessage(models.Model):
    """WhatsApp template messages"""
    CATEGORY_CHOICES = [
        ('marketing', 'Marketing'),
        ('utility', 'Utility'),
        ('authentication', 'Authentication'),
        ('transactional', 'Transactional'),
    ]
    
    template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='templates')
    whatsapp_connection = models.ForeignKey(WhatsAppConnection, on_delete=models.CASCADE, related_name='templates')
    category = models.TextField(choices=CATEGORY_CHOICES)
    body = models.TextField(help_text='Template body with placeholders like {{name}}')
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.category} - {self.body[:50]}..."

class Segment(models.Model):
    """Customer segmentation"""
    segment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='segments')
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    definition_json = models.JSONField(default=dict, help_text='JSON definition of segment criteria')
    is_dynamic = models.BooleanField(default=True)
    last_materialized_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"

class Campaign(models.Model):
    """Marketing campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    campaign_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaigns')
    name = models.TextField()
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='campaigns')
    status = models.TextField(choices=STATUS_CHOICES, default='draft')
    send_start_at = models.DateTimeField(blank=True, null=True)
    send_end_at = models.DateTimeField(blank=True, null=True)
    time_zone = models.TextField(default='UTC')
    throttle_per_min = models.IntegerField(default=60)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"

class CampaignVariant(models.Model):
    """A/B test variants for campaigns"""
    variant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaign_variants')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='variants')
    name = models.TextField()
    split_pct = models.IntegerField(help_text='Percentage of recipients for this variant')
    template = models.ForeignKey(TemplateMessage, on_delete=models.CASCADE, related_name='variants')
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.campaign.name} - {self.name}"

class CampaignRun(models.Model):
    """Individual campaign execution runs"""
    STATUS_CHOICES = [
        ('initializing', 'Initializing'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    run_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaign_runs')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='runs')
    segment_version_json = models.JSONField(default=dict, help_text='Snapshot of segment definition at run time')
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='initializing')
    
    def __str__(self):
        return f"{self.campaign.name} - Run {self.run_id}"

class CampaignRecipient(models.Model):
    """Recipients for a campaign run"""
    recipient_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaign_recipients')
    run = models.ForeignKey(CampaignRun, on_delete=models.CASCADE, related_name='recipients')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    variant = models.ForeignKey(CampaignVariant, on_delete=models.CASCADE, related_name='recipients')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='campaign_recipients')
    whatsapp_connection = models.ForeignKey(WhatsAppConnection, on_delete=models.CASCADE, related_name='campaign_recipients')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='campaign_recipients', blank=True, null=True)
    skip_reason = models.TextField(blank=True, null=True)
    selected = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.customer.name} - {self.campaign.name}"

class CampaignMessage(models.Model):
    """Individual messages sent as part of a campaign"""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    campaign_message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='campaign_messages')
    recipient = models.ForeignKey(CampaignRecipient, on_delete=models.CASCADE, related_name='messages')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='messages')
    variant = models.ForeignKey(CampaignVariant, on_delete=models.CASCADE, related_name='messages')
    template = models.ForeignKey(TemplateMessage, on_delete=models.CASCADE, related_name='campaign_messages')
    status = models.TextField(choices=STATUS_CHOICES, default='queued')
    error_code = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return f"{self.recipient.customer.name} - {self.status}"

# =============================================================================
# SEND QUEUE MODEL (for scheduled messages)
# =============================================================================

class SendQueue(models.Model):
    """Operational queue for scheduled message sending"""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('processing', 'Processing'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    queue_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='send_queue')
    campaign_message = models.ForeignKey(CampaignMessage, on_delete=models.CASCADE, related_name='queue_entries')
    scheduled_at = models.DateTimeField()
    status = models.TextField(choices=STATUS_CHOICES, default='queued')
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=dj_timezone.now)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['tenant', 'status']),
        ]
    
    def __str__(self):
        return f"Queue {self.queue_id} - {self.status} - {self.scheduled_at}"

# =============================================================================
# CONTEST AND PROMPT REPLIES
# =============================================================================

class Contest(models.Model):
    """Enhanced contest management with PDPA integration and custom messages."""
    contest_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='contests')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Contest requirements
    requires_nric = models.BooleanField(default=True, help_text='Require NRIC for participation')
    requires_receipt = models.BooleanField(default=True, help_text='Require proof of purchase')
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Minimum purchase amount required')
    
    # Custom post-PDPA messages
    post_pdpa_text = models.TextField(blank=True, null=True, help_text='Text message sent after PDPA consent')
    post_pdpa_image_url = models.URLField(blank=True, null=True, help_text='Image URL for post-PDPA message')
    post_pdpa_gif_url = models.URLField(blank=True, null=True, help_text='GIF URL for post-PDPA message')
    
    # Contest instructions
    contest_instructions = models.TextField(blank=True, null=True, help_text='Instructions for contestants')
    verification_instructions = models.TextField(blank=True, null=True, help_text='Instructions for verification process')
    
    # Eligibility message
    eligibility_message = models.TextField(default="Congratulations! You are eligible to participate in this contest. Please follow the instructions to complete your entry.", help_text='Message sent when contestant is verified as eligible')
    
    created_at = models.DateTimeField(default=dj_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"
    
    @property
    def is_currently_active(self):
        """Check if contest is currently active"""
        now = dj_timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at
    
    @property
    def total_entries(self):
        """Get total number of entries"""
        return self.entries.count()
    
    @property
    def verified_entries(self):
        """Get number of verified entries"""
        return self.entries.filter(is_verified=True).count()

class ContestEntry(models.Model):
    """Enhanced contest entry with verification and document collection."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('winner', 'Winner'),
    ]
    
    entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='contest_entries')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='entries')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='contest_entries')
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, blank=True, null=True, related_name='contest_entries')
    
    # Entry status and verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)
    
    # Contestant information
    contestant_name = models.CharField(max_length=200, blank=True, null=True)
    contestant_nric = models.CharField(max_length=20, blank=True, null=True, help_text='NRIC number for verification')
    contestant_phone = models.CharField(max_length=20, blank=True, null=True)
    contestant_email = models.EmailField(blank=True, null=True)
    
    # Receipt/proof of purchase
    receipt_image_url = models.URLField(blank=True, null=True, help_text='Receipt image URL')
    receipt_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Receipt amount')
    receipt_date = models.DateTimeField(blank=True, null=True, help_text='Receipt date')
    receipt_store = models.CharField(max_length=200, blank=True, null=True, help_text='Store name from receipt')
    
    # Additional documents
    additional_documents = models.JSONField(default=list, blank=True, help_text='Additional document URLs')
    
    # Verification details
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.CharField(max_length=200, blank=True, null=True, help_text='Who verified this entry')
    verification_notes = models.TextField(blank=True, null=True, help_text='Verification notes')
    
    # Timestamps
    submitted_at = models.DateTimeField(default=dj_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['contest', 'customer']
    
    def __str__(self):
        return f"{self.customer.name} @ {self.contest.name} ({self.status})"
    
    @property
    def is_eligible(self):
        """Check if entry meets contest requirements"""
        if not self.contest.is_currently_active:
            return False
        
        # Check NRIC requirement
        if self.contest.requires_nric and not self.contestant_nric:
            return False
        
        # Check receipt requirement
        if self.contest.requires_receipt and not self.receipt_image_url:
            return False
        
        # Check minimum purchase amount
        if self.contest.min_purchase_amount and self.receipt_amount:
            if self.receipt_amount < self.contest.min_purchase_amount:
                return False
        
        return True

class PromptReply(models.Model):
    """Saved quick replies for CRM agents."""
    prompt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='prompt_replies')
    name = models.CharField(max_length=120)
    body = models.TextField()
    created_at = models.DateTimeField(default=dj_timezone.now)
    
    def __str__(self):
        return self.name