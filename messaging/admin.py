from django.contrib import admin
from .models import (
    Tenant, WhatsAppConnection, Customer, Consent, Conversation, CoreMessage, 
    MessageAttachment, Receipt, ReceiptItem, TemplateMessage, Segment, 
    Campaign, CampaignVariant, CampaignRun, CampaignRecipient, 
    CampaignMessage, SendQueue, Contest, ContestEntry, TenantUser,
    CustomerGroup, GroupMember, BlastCampaign, BlastRecipient
)

# =============================================================================
# MULTI-TENANT CORE ADMIN
# =============================================================================

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan', 'creation_date', 'company_email']
    search_fields = ['name', 'company_email']
    list_filter = ['plan', 'creation_date']
    readonly_fields = ['tenant_id', 'creation_date']

@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'created_at']
    search_fields = ['user__username', 'tenant__name']
    list_filter = ['role', 'tenant']

@admin.register(WhatsAppConnection)
class WhatsAppConnectionAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'phone_number', 'provider', 'instance_id']
    search_fields = ['tenant__name', 'phone_number']
    list_filter = ['provider', 'tenant']
    readonly_fields = ['whatsapp_connection_id']

# =============================================================================
# CUSTOMER MANAGEMENT ADMIN
# =============================================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'tenant', 'gender', 'age', 'created_at']
    search_fields = ['name', 'phone_number', 'tenant__name']
    list_filter = ['gender', 'marital_status', 'state', 'tenant', 'created_at']
    readonly_fields = ['customer_id', 'created_at']
    raw_id_fields = ['tenant']

@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'type', 'status', 'occurred_at']
    search_fields = ['customer__name', 'customer__phone_number']
    list_filter = ['type', 'status', 'occurred_at']
    readonly_fields = ['consent_id', 'occurred_at']
    raw_id_fields = ['tenant', 'customer']

# =============================================================================
# CONVERSATION AND MESSAGING ADMIN
# =============================================================================

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'whatsapp_connection', 'last_message_at', 'is_archived']
    search_fields = ['customer__name', 'whatsapp_connection__phone_number']
    list_filter = ['is_archived', 'channel', 'created_at']
    readonly_fields = ['conversation_id', 'created_at']
    raw_id_fields = ['tenant', 'whatsapp_connection', 'customer']

@admin.register(CoreMessage)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'direction', 'status', 'created_at']
    search_fields = ['text_body', 'conversation__customer__name']
    list_filter = ['direction', 'status', 'created_at']
    readonly_fields = ['message_id', 'created_at']
    raw_id_fields = ['tenant', 'conversation']

@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ['message', 'kind', 'mime_type', 'bytes_size']
    search_fields = ['message__text_body']
    list_filter = ['kind', 'created_at']
    readonly_fields = ['attachment_id', 'created_at']
    raw_id_fields = ['tenant', 'message']

# =============================================================================
# RECEIPT AND OCR ADMIN
# =============================================================================

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total', 'purchase_date', 'ocr_confidence']
    search_fields = ['customer__name', 'customer__phone_number']
    list_filter = ['purchase_date', 'ocr_confidence', 'created_at']
    readonly_fields = ['receipt_id', 'created_at']
    raw_id_fields = ['tenant', 'customer']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'tenant')

@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ['receipt', 'description', 'qty', 'unit_price']
    search_fields = ['description', 'receipt__customer__name']
    list_filter = []
    readonly_fields = ['item_id']
    raw_id_fields = ['tenant', 'receipt']

# =============================================================================
# TEMPLATE AND CAMPAIGN ADMIN
# =============================================================================

@admin.register(TemplateMessage)
class TemplateMessageAdmin(admin.ModelAdmin):
    list_display = ['category', 'body_preview', 'tenant', 'created_at']
    search_fields = ['body', 'tenant__name']
    list_filter = ['category', 'created_at']
    readonly_fields = ['template_id', 'created_at']
    raw_id_fields = ['tenant', 'whatsapp_connection']
    
    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'Body Preview'

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'is_dynamic', 'last_materialized_at']
    search_fields = ['name', 'description', 'tenant__name']
    list_filter = ['is_dynamic', 'created_at']
    readonly_fields = ['segment_id', 'created_at', 'last_materialized_at']
    raw_id_fields = ['tenant']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'status', 'send_start_at', 'throttle_per_min']
    search_fields = ['name', 'tenant__name']
    list_filter = ['status', 'send_start_at', 'created_at']
    readonly_fields = ['campaign_id', 'created_at']
    raw_id_fields = ['tenant', 'segment']

@admin.register(CampaignVariant)
class CampaignVariantAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'name', 'split_pct', 'template']
    search_fields = ['name', 'campaign__name']
    list_filter = ['split_pct', 'created_at']
    readonly_fields = ['variant_id', 'created_at']
    raw_id_fields = ['tenant', 'campaign', 'template']

@admin.register(CampaignRun)
class CampaignRunAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'status', 'started_at', 'completed_at']
    search_fields = ['campaign__name']
    list_filter = ['status', 'started_at', 'completed_at']
    readonly_fields = ['run_id', 'started_at', 'completed_at']
    raw_id_fields = ['tenant', 'campaign']

@admin.register(CampaignRecipient)
class CampaignRecipientAdmin(admin.ModelAdmin):
    list_display = ['customer', 'campaign', 'variant', 'selected', 'skip_reason']
    search_fields = ['customer__name', 'campaign__name']
    list_filter = ['selected', 'created_at']
    readonly_fields = ['recipient_id', 'created_at']
    raw_id_fields = ['tenant', 'run', 'campaign', 'variant', 'customer', 'whatsapp_connection', 'conversation']

@admin.register(CampaignMessage)
class CampaignMessageAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'status', 'scheduled_at', 'sent_at']
    search_fields = ['recipient__customer__name', 'campaign__name']
    list_filter = ['status', 'scheduled_at', 'sent_at', 'created_at']
    readonly_fields = ['campaign_message_id', 'created_at']
    raw_id_fields = ['tenant', 'recipient', 'campaign', 'variant', 'template']

# =============================================================================
# SEND QUEUE ADMIN
# =============================================================================

@admin.register(SendQueue)
class SendQueueAdmin(admin.ModelAdmin):
    list_display = ['campaign_message', 'status', 'scheduled_at', 'retry_count', 'processed_at']
    search_fields = ['campaign_message__recipient__customer__name']
    list_filter = ['status', 'scheduled_at', 'retry_count', 'created_at']
    readonly_fields = ['queue_id', 'created_at', 'processed_at']
    raw_id_fields = ['tenant', 'campaign_message']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'campaign_message__recipient__customer',
            'campaign_message__campaign'
        )

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'keywords_display', 'starts_at', 'ends_at', 'is_active']
    search_fields = ['name', 'tenant__name', 'keywords']
    list_filter = ['is_active', 'starts_at', 'ends_at']
    readonly_fields = ['contest_id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('contest_id', 'tenant', 'name', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('starts_at', 'ends_at')
        }),
        ('Keyword Auto-Reply', {
            'fields': ('keywords', 'auto_reply_message', 'auto_reply_priority'),
            'description': 'Set keywords that trigger this contest (e.g., JOIN,MASUK,SERTAI) and the auto-reply message.'
        }),
        ('Requirements', {
            'fields': ('requires_nric', 'requires_receipt', 'min_purchase_amount')
        }),
        ('PDPA Messages', {
            'fields': ('pdpa_message', 'participant_agreement', 'participant_rejection'),
            'classes': ('collapse',)
        }),
        ('Post-PDPA Content', {
            'fields': ('post_pdpa_text', 'post_pdpa_image_url', 'post_pdpa_gif_url'),
            'classes': ('collapse',)
        }),
        ('Instructions', {
            'fields': ('contest_instructions', 'verification_instructions', 'eligibility_message'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def keywords_display(self, obj):
        """Display keywords as badges"""
        keywords = obj.get_keywords_list()
        if not keywords:
            return '-'
        from django.utils.html import mark_safe
        badges = []
        for kw in keywords[:3]:
            badges.append(f'<span style="background:#28a745;color:white;padding:2px 6px;border-radius:3px;margin-right:3px;font-size:11px;">{kw}</span>')
        if len(keywords) > 3:
            badges.append(f'<span style="color:#666;font-size:11px;">+{len(keywords)-3}</span>')
        return mark_safe(''.join(badges))
    keywords_display.short_description = 'Keywords'

@admin.register(ContestEntry)
class ContestEntryAdmin(admin.ModelAdmin):
    list_display = ['contest', 'customer', 'is_winner', 'submitted_at']
    search_fields = ['contest__name', 'customer__name', 'customer__phone_number']
    list_filter = ['is_winner', 'submitted_at']
    readonly_fields = ['entry_id']
    raw_id_fields = ['tenant', 'contest', 'customer', 'conversation']

# =============================================================================
# WHATSAPP BLASTING ADMIN
# =============================================================================

@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'source', 'member_count', 'created_at']
    search_fields = ['name', 'description', 'tenant__name']
    list_filter = ['source', 'created_at']
    readonly_fields = ['group_id', 'created_at', 'updated_at']
    raw_id_fields = ['tenant', 'contest']
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = 'Members'

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['customer', 'group', 'tenant', 'added_at']
    search_fields = ['customer__name', 'customer__phone_number', 'group__name']
    list_filter = ['added_at', 'tenant']
    readonly_fields = ['member_id', 'added_at']
    raw_id_fields = ['tenant', 'group', 'customer']

@admin.register(BlastCampaign)
class BlastCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'status', 'total_recipients', 'sent_count', 'delivered_count', 'success_rate', 'created_at']
    search_fields = ['name', 'tenant__name', 'message_text']
    list_filter = ['status', 'created_at', 'started_at', 'completed_at']
    readonly_fields = ['blast_id', 'created_at', 'started_at', 'completed_at']
    raw_id_fields = ['tenant', 'whatsapp_connection']
    filter_horizontal = ['target_groups', 'target_contests']
    
    def success_rate(self, obj):
        return f"{obj.success_rate}%"
    success_rate.short_description = 'Success Rate'

@admin.register(BlastRecipient)
class BlastRecipientAdmin(admin.ModelAdmin):
    list_display = ['customer', 'blast_campaign', 'status', 'sent_at', 'delivered_at']
    search_fields = ['customer__name', 'customer__phone_number', 'blast_campaign__name']
    list_filter = ['status', 'sent_at', 'delivered_at', 'created_at']
    readonly_fields = ['recipient_id', 'created_at', 'sent_at', 'delivered_at']
    raw_id_fields = ['tenant', 'blast_campaign', 'customer', 'message']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer',
            'blast_campaign',
            'tenant'
        )