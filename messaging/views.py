from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
import json
import base64
import pandas as pd
import re
import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
try:
    from .models import Contact, Message, BulkMessage, Campaign, CustomerSegment, Purchase, WhatsAppMessage, OCRProcessingLog
except Exception:  # during migrations or model refactors
    Contact = None
    Message = None
    BulkMessage = None
    Campaign = None
    CustomerSegment = None
    Purchase = None
    WhatsAppMessage = None
    OCRProcessingLog = None
from .whatsapp_service import WhatsAppAPIService
from .temp_image_storage import TemporaryImageStorage
from .cloudinary_service import cloudinary_service
from .ocr_service import OCRService
from safe_demographics import process_demographics, get_race_code, get_gender_code

# Initialize logger
logger = logging.getLogger(__name__)

# =========================
# Auth & Plan-Gated Dashboards
# =========================
from django.contrib.auth.decorators import login_required
from django.utils import timezone as dj_timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import (
    Tenant, TenantUser, Customer, CoreMessage, Conversation, WhatsAppConnection,
    PromptReply, Contest, ContestEntry, TemplateMessage, Segment,
    Campaign as NewCampaign, CampaignRun, CampaignRecipient, CampaignVariant,
    CampaignMessage, SendQueue, Consent
)


def _get_tenant(request):
    """Get tenant for authenticated user with error handling"""
    try:
        if not request.user.is_authenticated:
            return None
        
        # Check if user has tenant_profile
        if hasattr(request.user, 'tenant_profile'):
            return request.user.tenant_profile.tenant
        else:
            # User exists but has no tenant_profile
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"User {request.user.username} has no tenant_profile")
            return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"_get_tenant error: {e}")
        return None

def _require_plan(tenant, feature):
    if not tenant:
        return False
    plan = (tenant.plan or '').lower()
    if plan == 'pro':
        return True
    if feature == 'contest' and plan == 'contest':
        return True
    if feature == 'crm' and plan == 'crm':
        return True
    return False


@csrf_exempt
def auth_login(request):
    """Login view with CSRF exemption for App Engine"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'messaging/auth_login.html')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'messaging/auth_login.html')

def auth_logout(request):
    logout(request)
    return redirect('auth_login')


@login_required
def dashboard(request):
    """Dashboard view with proper error handling"""
    try:
        tenant = _get_tenant(request)
        if not tenant:
            messages.error(request, 'No tenant associated with your account')
            return redirect('auth_login')
        
        plan = (tenant.plan or '').upper()
        return render(request, 'messaging/dashboard.html', {
            'tenant': tenant,
            'plan': plan,
            'can_contest': _require_plan(tenant, 'contest'),
            'can_crm': _require_plan(tenant, 'crm'),
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard error: {e}")
        messages.error(request, 'An error occurred loading the dashboard')
        return redirect('auth_login')

def dashboard(request):
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    plan = (tenant.plan or '').upper()
    return render(request, 'messaging/dashboard.html', {
        'tenant': tenant,
        'plan': plan,
        'can_contest': _require_plan(tenant, 'contest'),
        'can_crm': _require_plan(tenant, 'crm'),
    })


# =========================
# Contest Management
# =========================
@login_required
def contest_home(request):
    """Enhanced contest home with management dashboard"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    # Only use hardcoded contests for display
    contests = [
        {
            'contest_id': 'merdeka_w1',
            'name': 'Khind Merdeka W1',
            'description': 'Merdeka Week 1 Contest',
            'starts_at': dj_timezone.now().replace(day=1),
            'ends_at': dj_timezone.now().replace(day=7),
            'is_active': True,
            'total_entries': 156,
            'verified_entries': 142,
            'flagged_entries': 14,
            'min_purchase_amount': 50.00
        },
        {
            'contest_id': 'merdeka_w2',
            'name': 'Khind Merdeka W2',
            'description': 'Merdeka Week 2 Contest',
            'starts_at': dj_timezone.now().replace(day=8),
            'ends_at': dj_timezone.now().replace(day=14),
            'is_active': True,
            'total_entries': 89,
            'verified_entries': 78,
            'flagged_entries': 11,
            'min_purchase_amount': 75.00
        },
        {
            'contest_id': 'merdeka_w3',
            'name': 'Khind Merdeka W3',
            'description': 'Merdeka Week 3 Contest',
            'starts_at': dj_timezone.now().replace(day=15),
            'ends_at': dj_timezone.now().replace(day=21),
            'is_active': False,
            'total_entries': 203,
            'verified_entries': 195,
            'flagged_entries': 8,
            'min_purchase_amount': 100.00
        }
    ]
    
    # Get active contest (from hardcoded contests)
    active_contest = next((c for c in contests if c['is_active']), None)
    
    # Get contest statistics with flagged entries
    contest_stats = []
    total_flagged_entries = 0
    total_all_entries = 0
    total_verified_entries = 0
    total_pending_entries = 0
    total_winners = 0
    
    for contest in contests:  # Show all hardcoded contests
        flagged_entries = contest['flagged_entries']
        total_flagged_entries += flagged_entries
        total_all_entries += contest['total_entries']
        total_verified_entries += contest['verified_entries']
        total_pending_entries += 0  # No pending entries in hardcoded data
        total_winners += 0  # No winners in hardcoded data
        
        stats = {
            'contest': contest,
            'total_entries': contest['total_entries'],
            'verified_entries': contest['verified_entries'],
            'pending_entries': 0,
            'flagged_entries': flagged_entries,
            'winners': 0,
        }
        contest_stats.append(stats)
    
    # Get active contest statistics for quick stats
    active_contest_stats = {
        'verified_entries': 0,
        'pending_entries': 0,
        'flagged_entries': 0,
        'winners': 0,
    }
    
    if active_contest:
        active_contest_stats = {
            'verified_entries': active_contest['verified_entries'],
            'pending_entries': 0,
            'flagged_entries': active_contest['flagged_entries'],
            'winners': 0,
        }
    
    # Overall contest statistics
    overall_stats = {
        'total_contests': len(contests),
        'active_contests': len([c for c in contests if c['is_active']]),
        'total_entries': total_all_entries,
        'total_verified_entries': total_verified_entries,
        'total_pending_entries': total_pending_entries,
        'total_flagged_entries': total_flagged_entries,
        'total_winners': total_winners,
    }
    
    context = {
        'tenant': tenant,
        'contests': contests,
        'active_contest': active_contest,
        'active_contest_stats': active_contest_stats,
        'contest_stats': contest_stats,
        'overall_stats': overall_stats,
        'now': dj_timezone.now(),
    }
    return render(request, 'messaging/contest_home_enhanced.html', context)


@login_required
def contest_contacts(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    q = (request.GET.get('q') or '').strip()
    customers = Customer.objects.filter(tenant=tenant)
    if q:
        customers = customers.filter(name__icontains=q)
    customers = customers.order_by('name')[:500]
    return render(request, 'messaging/contest_contacts.html', {'customers': customers, 'q': q})


@login_required
def contest_add_contact(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        if name and phone:
            Customer.objects.create(tenant=tenant, name=name, phone_number=phone)
        return redirect('contest_contacts')
    return render(request, 'messaging/contest_add_contact.html')


@login_required
def contest_send_message(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    # Get active contest
    contest = Contest.objects.filter(tenant=tenant, is_active=True).order_by('-starts_at').first()
    if not contest:
        messages.error(request, 'No active contest found')
        return redirect('contest_home')
    
    # Get contest entries
    entries = ContestEntry.objects.filter(tenant=tenant, contest=contest)
    
    if request.method == 'POST':
        try:
            # Get form data
            customer_ids = request.POST.getlist('customer_ids')
            message_text = request.POST.get('message_text', '').strip()
            send_immediately = request.POST.get('send_immediately') == 'on'
            
            if not customer_ids:
                messages.error(request, 'Please select at least one customer')
                return redirect('contest_send_message')
            
            if not message_text:
                messages.error(request, 'Please enter a message')
                return redirect('contest_send_message')
            
            # Initialize WhatsApp service
            wa_service = WhatsAppAPIService()
            
            # Send messages
            success_count = 0
            error_count = 0
            
            for customer_id in customer_ids:
                try:
                    customer = Customer.objects.get(tenant=tenant, customer_id=customer_id)
                    
                    # Send via WABot
                    result = wa_service.send_text_message(customer.phone_number, message_text)
                    
                    if result['success']:
                        # Create conversation and message record
                        conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
                        if conn:
                            convo, _ = Conversation.objects.get_or_create(
                                tenant=tenant, 
                                customer=customer, 
                                whatsapp_connection=conn, 
                                contest=contest,
                                defaults={}
                            )
                            CoreMessage.objects.create(
                                tenant=tenant,
                                conversation=convo,
                                direction='outbound',
                                status='sent',
                                text_body=message_text,
                                provider_msg_id=result['data'].get('id'),
                                sent_at=dj_timezone.now()
                            )
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Failed to send message to {customer.phone_number}: {result.get('error')}")
                        
                except Customer.DoesNotExist:
                    error_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error sending message to customer {customer_id}: {str(e)}")
            
            # Show results
            if success_count > 0:
                messages.success(request, f'Successfully sent {success_count} message(s)')
            if error_count > 0:
                messages.warning(request, f'Failed to send {error_count} message(s)')
            
            return redirect('contest_contacts')
            
        except Exception as e:
            messages.error(request, f'Error sending messages: {str(e)}')
            return redirect('contest_send_message')
    
    # GET request - show form
    # Get customers from contest entries, or all customers if no entries yet
    if entries.exists():
        customer_ids = [e.customer.customer_id for e in entries]
        customers = Customer.objects.filter(tenant=tenant, customer_id__in=customer_ids)
    else:
        # If no contest entries yet, show all customers for the tenant
        customers = Customer.objects.filter(tenant=tenant).order_by('name')[:50]  # Limit to 50 for performance
    
    context = {
        'contest': contest,
        'entries': entries,
        'customers': customers
    }
    return render(request, 'messaging/contest_send_message.html', context)


@login_required
def contest_select_winner(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    contest = Contest.objects.filter(tenant=tenant, is_active=True).order_by('-starts_at').first()
    entries = ContestEntry.objects.filter(tenant=tenant, contest=contest)
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        if entry_id:
            try:
                entry = entries.get(entry_id=entry_id)
                entries.update(is_winner=False)
                entry.is_winner = True
                entry.save()
                messages.success(request, 'Winner selected')
            except ContestEntry.DoesNotExist:
                messages.error(request, 'Invalid entry')
        return redirect('contest_select_winner')
    return render(request, 'messaging/contest_select_winner.html', {'contest': contest, 'entries': entries})


# =========================
# CRM Area
# =========================
@login_required
def crm_home(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    return render(request, 'messaging/crm_home.html', {})


@login_required
def crm_prompt_replies(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    prompts = PromptReply.objects.filter(tenant=tenant).order_by('-created_at')
    return render(request, 'messaging/crm_prompt_replies.html', {'prompts': prompts})


@login_required
def crm_add_prompt_reply(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        body = request.POST.get('body')
        if name and body:
            PromptReply.objects.create(tenant=tenant, name=name, body=body)
        return redirect('crm_prompt_replies')
    return render(request, 'messaging/crm_add_prompt_reply.html')


@login_required
def crm_schedule_message(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        text = request.POST.get('text')
        when = request.POST.get('when')
        template = TemplateMessage.objects.filter(tenant=tenant).first()
        customer = get_object_or_404(Customer, tenant=tenant, customer_id=customer_id)
        seg = Segment.objects.create(tenant=tenant, name='ad-hoc', definition_json={'customer_ids': [str(customer.customer_id)]}, is_dynamic=False)
        camp = NewCampaign.objects.create(tenant=tenant, name='Adhoc', segment=seg, status='scheduled')
        run = CampaignRun.objects.create(tenant=tenant, campaign=camp, segment_version_json=seg.definition_json)
        variant = CampaignVariant.objects.create(tenant=tenant, campaign=camp, name='A', split_pct=100, template=template)
        recipient = CampaignRecipient.objects.create(
            tenant=tenant, run=run, campaign=camp, variant=variant, customer=customer,
            whatsapp_connection=WhatsAppConnection.objects.filter(tenant=tenant).first()
        )
        cm = CampaignMessage.objects.create(
            tenant=tenant, recipient=recipient, campaign=camp, variant=variant, template=template,
            status='queued', scheduled_at=when
        )
        SendQueue.objects.create(tenant=tenant, campaign_message=cm, scheduled_at=when)
        messages.success(request, 'Scheduled message queued')
        return redirect('crm_home')
    customers = Customer.objects.filter(tenant=_get_tenant(request)).order_by('name')[:200]
    return render(request, 'messaging/crm_schedule.html', {'customers': customers})


@login_required
def crm_campaigns(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    campaigns = NewCampaign.objects.filter(tenant=tenant).order_by('-created_at')
    return render(request, 'messaging/crm_campaigns.html', {'campaigns': campaigns})


@login_required
def crm_analytics(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'crm'):
        return redirect('dashboard')
    total_customers = Customer.objects.filter(tenant=tenant).count()
    total_msgs = CampaignMessage.objects.filter(tenant=tenant).count()
    sent = CampaignMessage.objects.filter(tenant=tenant, status='sent').count()
    delivered = CampaignMessage.objects.filter(tenant=tenant, status='delivered').count()
    read = CampaignMessage.objects.filter(tenant=tenant, status='read').count()
    return render(request, 'messaging/crm_analytics.html', {
        'total_customers': total_customers,
        'total_msgs': total_msgs,
        'sent': sent,
        'delivered': delivered,
        'read': read,
    })


def main_page(request):
    """Main page with message preview and recipient selection"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    customers = Customer.objects.filter(tenant=tenant)
    
    # Filter functionality
    state_filter = request.GET.get('state')
    gender_filter = request.GET.get('gender')
    marital_filter = request.GET.get('marital_status')
    
    if state_filter:
        customers = customers.filter(state=state_filter)
    if gender_filter:
        customers = customers.filter(gender=gender_filter)
    if marital_filter:
        customers = customers.filter(marital_status=marital_filter)
    
    # Convert customers to JSON for safe JavaScript usage
    contacts_json = json.dumps([
        {
            'id': str(customer.customer_id), 
            'name': customer.name, 
            'phone': customer.phone_number,
            'state': customer.state or '',
            'gender': customer.gender,
            'marital_status': customer.marital_status,
            'age': customer.age,
            'city': customer.city or '',
        } 
        for customer in customers
    ])
    
    context = {
        'contacts': customers,  # Keep 'contacts' for template compatibility
        'contacts_json': contacts_json,
        'state_choices': [
            ('SEL', 'Selangor'), ('KUL', 'Kuala Lumpur'), ('JHR', 'Johor'),
            ('PNG', 'Penang'), ('PRK', 'Perak'), ('SBH', 'Sabah'),
            ('SWK', 'Sarawak'), ('KDH', 'Kedah'), ('KTN', 'Kelantan'),
            ('PHG', 'Pahang'), ('TRG', 'Terengganu'), ('MLK', 'Melaka'),
            ('NSN', 'Negeri Sembilan'), ('PLS', 'Perlis'), ('PJY', 'Putrajaya'),
            ('LBN', 'Labuan')
        ],
        'gender_choices': [
            ('N/A', 'N/A'), ('M', 'Male'), ('F', 'Female'),
            ('NB', 'Non-binary'), ('PNS', 'Prefer not to say')
        ],
        'marital_choices': [
            ('N/A', 'N/A'), ('SINGLE', 'Single'), ('MARRIED', 'Married'),
            ('DIVORCED', 'Divorced'), ('WIDOWED', 'Widowed')
        ],
        'selected_state': state_filter,
        'selected_gender': gender_filter,
        'selected_marital': marital_filter,
    }
    
    return render(request, 'messaging/recipients_and_preview.html', context)

def manage_customers(request):
    """Customer management page - add, edit, delete customers"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    customers = Customer.objects.filter(tenant=tenant)
    
    # Filter functionality
    state_filter = request.GET.get('state')
    gender_filter = request.GET.get('gender')
    marital_filter = request.GET.get('marital_status')
    
    if state_filter:
        customers = customers.filter(state=state_filter)
    if gender_filter:
        customers = customers.filter(gender=gender_filter)
    if marital_filter:
        customers = customers.filter(marital_status=marital_filter)
    
    # Add message counts and consent status for each customer
    from django.db.models import Count, Q, Max, Subquery, OuterRef
    from .pdpa_service import PDPAConsentService
    
    customers_with_counts = customers.annotate(
        total_messages=Count('conversations__messages'),
        inbound_messages=Count('conversations__messages', filter=Q(conversations__messages__direction='inbound')),
        outbound_messages=Count('conversations__messages', filter=Q(conversations__messages__direction='outbound')),
        last_message_date=Max('conversations__messages__created_at')
    ).order_by('-last_message_date', '-created_at')
    
    # Add consent status to each customer
    pdpa_service = PDPAConsentService()
    for customer in customers_with_counts:
        customer.consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
        # Get consent granted date
        latest_consent = Consent.objects.filter(
            tenant=tenant,
            customer=customer,
            type='whatsapp',
            status='granted'
        ).order_by('-occurred_at').first()
        customer.consent_granted_date = latest_consent.occurred_at if latest_consent else None
    
    # Get choices for dropdowns
    context = {
        'customers': customers_with_counts,
        'state_choices': [
            ('SEL', 'Selangor'), ('KUL', 'Kuala Lumpur'), ('JHR', 'Johor'),
            ('PNG', 'Penang'), ('PRK', 'Perak'), ('SBH', 'Sabah'),
            ('SWK', 'Sarawak'), ('KDH', 'Kedah'), ('KTN', 'Kelantan'),
            ('PHG', 'Pahang'), ('TRG', 'Terengganu'), ('MLK', 'Melaka'),
            ('NSN', 'Negeri Sembilan'), ('PLS', 'Perlis'), ('PJY', 'Putrajaya'),
            ('LBN', 'Labuan')
        ],
        'gender_choices': [
            ('N/A', 'N/A'), ('M', 'Male'), ('F', 'Female'),
            ('NB', 'Non-binary'), ('PNS', 'Prefer not to say')
        ],
        'marital_choices': [
            ('N/A', 'N/A'), ('SINGLE', 'Single'), ('MARRIED', 'Married'),
            ('DIVORCED', 'Divorced'), ('WIDOWED', 'Widowed')
        ],
        'selected_state': state_filter,
        'selected_gender': gender_filter,
        'selected_marital': marital_filter,
    }
    
    return render(request, 'messaging/manage_customers.html', context)




# =========================
# Settings: WhatsApp Integration
# =========================
@login_required
def whatsapp_settings(request):
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')

    # List connections
    conns = WhatsAppConnection.objects.filter(tenant=tenant).order_by('phone_number')

    if request.method == 'POST':
        # Add or update a connection
        phone = (request.POST.get('phone_number') or '').strip()
        access_token_ref = (request.POST.get('access_token_ref') or '').strip()
        instance_id = (request.POST.get('instance_id') or '').strip()
        provider = (request.POST.get('provider') or 'wabot')
        if phone and access_token_ref and instance_id:
            WhatsAppConnection.objects.create(
                tenant=tenant,
                phone_number=phone,
                access_token_ref=access_token_ref,
                instance_id=instance_id,
                provider=provider
            )
            messages.success(request, 'WhatsApp connection added')
            return redirect('whatsapp_settings')

    # Optional: instance status via API settings
    status = None
    try:
        svc = WhatsAppAPIService()
        status = svc.get_instance_status()
    except Exception:
        status = None

    return render(request, 'messaging/whatsapp_settings.html', {
        'connections': conns,
        'status': status,
    })


# =========================
# Contest: Create & Analytics
# =========================
@login_required
def contest_create(request):
    """Enhanced contest creation with PDPA integration and custom messages"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Basic contest information
            name = (request.POST.get('name') or '').strip()
            description = (request.POST.get('description') or '').strip()
            starts_at = request.POST.get('starts_at')
            ends_at = request.POST.get('ends_at')
            is_active = True if request.POST.get('is_active') == 'on' else False
            
            # Contest requirements
            requires_nric = True if request.POST.get('requires_nric') == 'on' else False
            requires_receipt = True if request.POST.get('requires_receipt') == 'on' else False
            min_purchase_amount = request.POST.get('min_purchase_amount')
            if min_purchase_amount:
                min_purchase_amount = Decimal(min_purchase_amount)
            else:
                min_purchase_amount = None
            
            # Custom post-PDPA messages
            post_pdpa_text = request.POST.get('post_pdpa_text', '').strip()
            post_pdpa_image_url = request.POST.get('post_pdpa_image_url', '').strip()
            post_pdpa_gif_url = request.POST.get('post_pdpa_gif_url', '').strip()
            
            # Contest instructions
            contest_instructions = request.POST.get('contest_instructions', '').strip()
            verification_instructions = request.POST.get('verification_instructions', '').strip()
            eligibility_message = request.POST.get('eligibility_message', '').strip()
            
            from django.utils.dateparse import parse_datetime
            from decimal import Decimal
            
            contest = Contest.objects.create(
                tenant=tenant,
                name=name or 'Untitled Contest',
                description=description or None,
                starts_at=parse_datetime(starts_at),
                ends_at=parse_datetime(ends_at),
                is_active=is_active,
                
                # Requirements
                requires_nric=requires_nric,
                requires_receipt=requires_receipt,
                min_purchase_amount=min_purchase_amount,
                
                # Custom messages
                post_pdpa_text=post_pdpa_text or None,
                post_pdpa_image_url=post_pdpa_image_url or None,
                post_pdpa_gif_url=post_pdpa_gif_url or None,
                
                # Instructions
                contest_instructions=contest_instructions or None,
                verification_instructions=verification_instructions or None,
                eligibility_message=eligibility_message or "Congratulations! You are eligible to participate in this contest. Please follow the instructions to complete your entry.",
            )
            
            messages.success(request, f'Contest "{contest.name}" created successfully!')
            return redirect('contest_detail', contest_id=contest.contest_id)
            
        except Exception as e:
            messages.error(request, f'Failed to create contest: {e}')
    
    return render(request, 'messaging/contest_create.html')


@login_required
def contest_analytics(request):
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    contest = Contest.objects.filter(tenant=tenant, is_active=True).order_by('-starts_at').first()
    entries = ContestEntry.objects.filter(tenant=tenant, contest=contest)
    total_entries = entries.count()
    winners = entries.filter(is_winner=True).count()
    # Simple per-day submission counts
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    timeline = entries.annotate(day=TruncDate('submitted_at')).values('day').order_by('day').annotate(count=Count('entry_id'))
    return render(request, 'messaging/contest_analytics.html', {
        'contest': contest,
        'total_entries': total_entries,
        'winners': winners,
        'timeline': list(timeline),
    })


@login_required
def contest_detail(request, contest_id):
    """Contest detail view with entries management"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    try:
        contest = Contest.objects.get(contest_id=contest_id, tenant=tenant)
    except Contest.DoesNotExist:
        messages.error(request, 'Contest not found')
        return redirect('contest_home')
    
    # Get contest entries with filtering
    entries = ContestEntry.objects.filter(contest=contest).order_by('-submitted_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        entries = entries.filter(status=status_filter)
    
    # Search by customer name
    search = request.GET.get('search', '').strip()
    if search:
        entries = entries.filter(customer__name__icontains=search)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get contest statistics
    contest_stats = {
        'total_entries': contest.total_entries,
        'verified_entries': contest.verified_entries,
        'pending_entries': contest.entries.filter(status='pending').count(),
        'winners': contest.entries.filter(is_winner=True).count(),
    }
    
    context = {
        'contest': contest,
        'entries': page_obj,
        'status_filter': status_filter,
        'search': search,
        'status_choices': ContestEntry.STATUS_CHOICES,
        'contest_stats': contest_stats,
        'now': dj_timezone.now(),
    }
    return render(request, 'messaging/contest_detail.html', context)


@login_required
def contest_entries(request, contest_id):
    """Contest entries management"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    try:
        contest = Contest.objects.get(contest_id=contest_id, tenant=tenant)
    except Contest.DoesNotExist:
        messages.error(request, 'Contest not found')
        return redirect('contest_home')
    
    # Get all entries
    entries = ContestEntry.objects.filter(contest=contest).order_by('-submitted_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        entries = entries.filter(status=status_filter)
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        entries = entries.filter(customer__name__icontains=search)
    
    context = {
        'contest': contest,
        'entries': entries,
        'status_filter': status_filter,
        'search': search,
        'status_choices': ContestEntry.STATUS_CHOICES,
    }
    return render(request, 'messaging/contest_entries.html', context)


@login_required
def contest_verify_entry(request, entry_id):
    """Verify a contest entry"""
    tenant = _get_tenant(request)
    if not _require_plan(tenant, 'contest'):
        return redirect('dashboard')
    
    try:
        entry = ContestEntry.objects.get(entry_id=entry_id, tenant=tenant)
    except ContestEntry.DoesNotExist:
        messages.error(request, 'Entry not found')
        return redirect('contest_home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        verification_notes = request.POST.get('verification_notes', '').strip()
        
        if action == 'verify':
            entry.status = 'verified'
            entry.is_verified = True
            entry.verified_at = dj_timezone.now()
            entry.verified_by = request.user.get_full_name() or request.user.username
            entry.verification_notes = verification_notes
            entry.save()
            
            # Send eligibility message
            from .whatsapp_service import WhatsAppAPIService
            wa_service = WhatsAppAPIService()
            wa_service.send_text_message(entry.customer.phone_number, entry.contest.eligibility_message)
            
            messages.success(request, f'Entry verified for {entry.customer.name}')
            
        elif action == 'reject':
            entry.status = 'rejected'
            entry.verification_notes = verification_notes
            entry.save()
            messages.success(request, f'Entry rejected for {entry.customer.name}')
        
        return redirect('contest_detail', contest_id=entry.contest.contest_id)
    
    context = {
        'entry': entry,
        'contest': entry.contest,
    }
    return render(request, 'messaging/contest_verify_entry.html', context)


@login_required
def contest_manager(request):
    """Contest manager page with detailed entries table"""
    try:
        tenant = _get_tenant(request)
        if not _require_plan(tenant, 'contest'):
            return redirect('dashboard')
    except Exception as e:
        print(f"Error in contest_manager: {e}")
        return redirect('dashboard')
    
    # Get filter parameters
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    store_filter = request.GET.get('store', '')
    location_filter = request.GET.get('location', '')
    contest_filter = request.GET.get('contest', 'merdeka_w1')  # Default to W1
    
    # Hardcoded contests
    contests = [
        {'id': 'merdeka_w1', 'name': 'Khind Merdeka W1', 'status': 'active'},
        {'id': 'merdeka_w2', 'name': 'Khind Merdeka W2', 'status': 'active'},
        {'id': 'merdeka_w3', 'name': 'Khind Merdeka W3', 'status': 'ended'}
    ]
    
    # Get selected contest
    selected_contest = next((c for c in contests if c['id'] == contest_filter), contests[0])
    
    # Import the hardcoded Khind Merdeka W1 and W2 data
    from .khind_merdeka_w1_data import KHIND_MERDEKA_W1_DATA
    from .khind_merdeka_w2_data import KHIND_MERDEKA_W2_DATA
    
    # Sample data for each contest
    contest_data = {
        'merdeka_w1': KHIND_MERDEKA_W1_DATA,
        'merdeka_w2': KHIND_MERDEKA_W2_DATA,
        'merdeka_w3': [
            {
                'submission_no': 'MLP_788',
                'amount_spent': 'RM159.00',
                'validity': 'valid',
                'reason': '-',
                'store': 'SENHENG',
                'store_location': 'Penang, Penang',
                'full_name': 'Lim Wei Ming',
                'phone_number': '+60155512345',
                'email': 'lim.weiming@email.com',
                'address': '789 Jalan Burma, George Town',
                'postcode': '10050',
                'city': 'George Town',
                'state': 'Penang',
                'receipt_url': '#'
            },
            {
                'submission_no': 'MLP_789',
                'amount_spent': 'RM199.00',
                'validity': 'valid',
                'reason': '-',
                'store': 'ELECTRONICS STORE',
                'store_location': 'Kota Kinabalu, Sabah',
                'full_name': 'Ahmad Bin Hassan',
                'phone_number': '+60123456789',
                'email': 'ahmad.hassan@email.com',
                'address': '123 Jalan Lintas, Kota Kinabalu',
                'postcode': '88000',
                'city': 'Kota Kinabalu',
                'state': 'Sabah',
                'receipt_url': '#'
            }
        ]
    }
    
    # Get entries for selected contest
    sample_entries = contest_data.get(contest_filter, contest_data['merdeka_w1'])
    
    # Apply search filter
    if search_query:
        sample_entries = [entry for entry in sample_entries if 
                         search_query.lower() in entry['full_name'].lower() or
                         search_query.lower() in entry['phone_number'].lower() or
                         search_query.lower() in entry['email'].lower() or
                         search_query.lower() in entry['submission_no'].lower()]
    
    # Apply status filter
    if status_filter:
        sample_entries = [entry for entry in sample_entries if entry['validity'] == status_filter]
    
    # Apply store and location filters to sample data
    if store_filter:
        sample_entries = [entry for entry in sample_entries if store_filter.lower() in entry['store'].lower()]
    
    if location_filter:
        sample_entries = [entry for entry in sample_entries if location_filter.lower() in entry['store_location'].lower()]
    
    # Implement pagination
    from django.core.paginator import Paginator
    paginator = Paginator(sample_entries, 20)  # 20 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contests': contests,
        'selected_contest': selected_contest,
        'entries': page_obj,
        'total_entries': len(sample_entries),
        'search_query': search_query,
        'status_filter': status_filter,
        'store_filter': store_filter,
        'location_filter': location_filter,
        'contest_filter': contest_filter,
    }
    return render(request, 'messaging/contest_manager.html', context)


@login_required
def participants_manager(request):
    """Participants manager page with filtering and detailed view"""
    try:
        tenant = _get_tenant(request)
        if not _require_plan(tenant, 'contest'):
            return redirect('dashboard')
    except Exception as e:
        print(f"Error in participants_manager: {e}")
        return redirect('dashboard')
    
    # Get filter parameters
    contest_filter = request.GET.get('contest', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '').strip()
    
    # Sample participants data
    participants = [
        {
            'id': 'participant1',
            'name': 'Loo Li Shen',
            'phone': '0162107682',
            'email': 'loolishen016@gmail.com',
            'ic': '041030 10 1963',
            'contest': 'Merdeka W1',
            'status': 'flagged',
            'errors': 'Invalid Receipt, Unreadable',
            'submission_date': 'Sep 15, 2024',
            'store': 'Jaya Grocer',
            'company_no': '123123123',
            'location': 'Subang Jaya, Selangor',
            'product': 'BLDC Fan',
            'amount': '1',
            'spent': 'RM123'
        },
        {
            'id': 'participant2',
            'name': 'Muhammad Dzulfadhlie',
            'phone': '+601127052763',
            'email': 'fadhlie2402.md@gmail.com',
            'ic': '950815-10-1234',
            'contest': 'Merdeka W1',
            'status': 'valid',
            'errors': '-',
            'submission_date': 'Sep 14, 2024',
            'store': 'ED FEST',
            'company_no': '456789012',
            'location': 'Sepang, Selangor',
            'product': 'Khind Rice Cooker',
            'amount': '1',
            'spent': 'RM59.00'
        },
        {
            'id': 'participant3',
            'name': 'Sarah Binti Rahman',
            'phone': '+60198765432',
            'email': 'sarah.rahman@email.com',
            'ic': '920315-08-5678',
            'contest': 'Back to School',
            'status': 'valid',
            'errors': '-',
            'submission_date': 'Aug 25, 2024',
            'store': 'COURTS',
            'company_no': '789012345',
            'location': 'Kuala Lumpur, KL',
            'product': 'Khind Blender',
            'amount': '1',
            'spent': 'RM299.00'
        },
        {
            'id': 'participant4',
            'name': 'Ahmad Bin Abdullah',
            'phone': '+60123456789',
            'email': 'ahmad@email.com',
            'ic': '880210-05-9012',
            'contest': 'Merdeka W1',
            'status': 'flagged',
            'errors': 'Receipt not clear, Missing store info',
            'submission_date': 'Sep 16, 2024',
            'store': 'HARVEY NORMAN',
            'company_no': '012345678',
            'location': 'Johor Bahru, Johor',
            'product': 'Khind Toaster',
            'amount': '1',
            'spent': 'RM89.50'
        },
        {
            'id': 'participant5',
            'name': 'Lim Wei Ming',
            'phone': '+60155512345',
            'email': 'lim.weiming@email.com',
            'ic': '930512-12-3456',
            'contest': 'Back to School',
            'status': 'valid',
            'errors': '-',
            'submission_date': 'Aug 20, 2024',
            'store': 'SENHENG',
            'company_no': '345678901',
            'location': 'Penang, Penang',
            'product': 'Khind Fan',
            'amount': '1',
            'spent': 'RM159.00'
        }
    ]
    
    # Apply filters
    if contest_filter:
        if contest_filter == 'merdeka':
            participants = [p for p in participants if p['contest'] == 'Merdeka W1']
        elif contest_filter == 'backtoschool':
            participants = [p for p in participants if p['contest'] == 'Back to School']
        elif contest_filter == 'holiday':
            participants = [p for p in participants if p['contest'] == 'Holiday Special']
    
    if status_filter:
        if status_filter == 'valid':
            participants = [p for p in participants if p['status'] == 'valid']
        elif status_filter == 'flagged':
            participants = [p for p in participants if p['status'] == 'flagged']
    
    if search_query:
        participants = [p for p in participants if 
                      search_query.lower() in p['name'].lower() or
                      search_query.lower() in p['phone'].lower() or
                      search_query.lower() in p['email'].lower()]
    
    context = {
        'participants': participants,
        'total_participants': len(participants),
        'contest_filter': contest_filter,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'messaging/participants_manager.html', context)

def analytics_dashboard(request):
    """Analytics dashboard with data visualizations"""
    from django.db.models import Count, Q
    from collections import defaultdict
    import json
    from datetime import datetime, timedelta
    
    # Get tenant and filter customers
    tenant = _get_tenant(request)
    customers = Customer.objects.filter(tenant=tenant)
    
    # Basic statistics
    total_customers = customers.count()
    
    # State choices (hardcoded since Customer model doesn't have STATE_CHOICES)
    STATE_CHOICES = [
        ('SEL', 'Selangor'), ('KUL', 'Kuala Lumpur'), ('JHR', 'Johor'),
        ('PNG', 'Penang'), ('PRK', 'Perak'), ('SBH', 'Sabah'),
        ('SWK', 'Sarawak'), ('KDH', 'Kedah'), ('KTN', 'Kelantan'),
        ('PHG', 'Pahang'), ('TRG', 'Terengganu'), ('MLK', 'Melaka'),
        ('NSN', 'Negeri Sembilan'), ('PLS', 'Perlis'), ('PJY', 'Putrajaya'),
        ('LBN', 'Labuan')
    ]
    
    # Distribution by State
    state_distribution = []
    for state_code, state_name in STATE_CHOICES:
        if state_code != 'N/A':
            count = customers.filter(state=state_code).count()
            if count > 0:
                state_distribution.append({'name': state_name, 'value': count})
    
    # Distribution by Gender
    gender_distribution = []
    for gender_code, gender_name in Customer.GENDER_CHOICES:
        if gender_code != 'N/A':
            count = customers.filter(gender=gender_code).count()
            if count > 0:
                gender_distribution.append({'name': gender_name, 'value': count})
    
    # Distribution by Marital Status
    marital_distribution = []
    for marital_code, marital_name in Customer.MARITAL_STATUS_CHOICES:
        if marital_code != 'N/A':
            count = customers.filter(marital_status=marital_code).count()
            if count > 0:
                marital_distribution.append({'name': marital_name, 'value': count})
    
    # Registration timeline (last 12 months)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    timeline_data = []
    current_date = start_date
    while current_date <= end_date:
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        count = customers.filter(created_at__date__range=[month_start, month_end]).count()
        timeline_data.append({
            'date': month_start.strftime('%Y-%m'),
            'count': count,
            'month': month_start.strftime('%b %Y')
        })
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Recent registrations (last 30 days)
    recent_date = end_date - timedelta(days=30)
    recent_customers = customers.filter(created_at__date__gte=recent_date).order_by('-created_at')[:10]
    
    # Prepare data for Chart.js (separate labels and data arrays)
    state_labels = [item['name'] for item in state_distribution]
    state_data = [item['value'] for item in state_distribution]
    
    gender_labels = [item['name'] for item in gender_distribution]
    gender_data = [item['value'] for item in gender_distribution]
    
    marital_labels = [item['name'] for item in marital_distribution]
    marital_data = [item['value'] for item in marital_distribution]
    
    timeline_labels = [item['month'] for item in timeline_data]
    timeline_counts = [item['count'] for item in timeline_data]
    
    # Cross-tabulation data for template
    cross_tabulation = {}
    
    for state_code, state_name in STATE_CHOICES:
        if state_code != 'N/A':
            gender_counts = {}
            total_for_state = 0
            for gender_code, gender_name in Customer.GENDER_CHOICES:
                if gender_code != 'N/A':
                    count = customers.filter(state=state_code, gender=gender_code).count()
                    gender_counts[gender_name] = count
                    total_for_state += count
            
            if total_for_state > 0:  # Only include states with customers
                gender_counts['total'] = total_for_state
                cross_tabulation[state_name] = gender_counts
    
    context = {
        'total_customers': total_customers,
        'unique_states': len([s for s in state_distribution if s['value'] > 0]),
        'recent_additions': customers.filter(created_at__date__gte=recent_date).count(),
        
        # Chart.js data
        'state_labels': json.dumps(state_labels),
        'state_data': json.dumps(state_data),
        'gender_labels': json.dumps(gender_labels),
        'gender_data': json.dumps(gender_data),
        'marital_labels': json.dumps(marital_labels),
        'marital_data': json.dumps(marital_data),
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_data': json.dumps(timeline_counts),
        
        # Cross-tabulation data
        'cross_tabulation': cross_tabulation,
        
        # Recent customers
        'recent_customers': recent_customers,
    }
    
    return render(request, 'messaging/analytics_dashboard.html', context)

def add_contact(request):
    """Add a new customer"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        ic_number = request.POST.get('ic_number', '')
        gender = request.POST.get('gender', 'N/A')
        marital_status = request.POST.get('marital_status', 'N/A')
        age = request.POST.get('age')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        
        if name and phone:
            customer_data = {
                'tenant': tenant,
                'name': name,
                'phone_number': phone,
                'ic_number': ic_number if ic_number else None,
                'gender': gender,
                'marital_status': marital_status,
                'city': city if city else None,
                'state': state if state else None,
            }
            
            # Handle age - convert to integer or set to None
            if age:
                try:
                    customer_data['age'] = int(age)
                except ValueError:
                    customer_data['age'] = None
            else:
                customer_data['age'] = None
                
            Customer.objects.create(**customer_data)
            
        # Redirect based on where the form was submitted from
        if request.POST.get('redirect_to') == 'customers':
            return redirect('manage_customers')
        else:
            return redirect('main_page')
    
    return redirect('main_page')

def edit_contact(request, contact_id):
    """Edit an existing customer"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    customer = get_object_or_404(Customer, customer_id=contact_id, tenant=tenant)
    
    if request.method == 'POST':
        customer.name = request.POST.get('name', customer.name)
        customer.phone_number = request.POST.get('phone', customer.phone_number)
        customer.ic_number = request.POST.get('ic_number', '') or None
        customer.gender = request.POST.get('gender', customer.gender)
        customer.marital_status = request.POST.get('marital_status', customer.marital_status)
        customer.city = request.POST.get('city', '') or None
        customer.state = request.POST.get('state', '') or None
        
        # Handle age
        age = request.POST.get('age')
        if age:
            try:
                customer.age = int(age)
            except ValueError:
                customer.age = None
        else:
            customer.age = None
            
        customer.save()
        return redirect('manage_customers')
    
    return redirect('manage_customers')

def delete_contact(request, contact_id):
    """Delete a customer"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    customer = get_object_or_404(Customer, customer_id=contact_id, tenant=tenant)
    customer.delete()
    
    if request.method == 'POST':
        # AJAX request for bulk delete
        return JsonResponse({'success': True})
    else:
        # Regular GET request
        return redirect('manage_customers')


@csrf_exempt
@login_required
def bulk_delete_customers(request):
    """Bulk delete customers"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if request.method != 'POST':
            logger.error("Bulk delete: Method not allowed")
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        tenant = _get_tenant(request)
        if not tenant:
            logger.error("Bulk delete: No tenant found")
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        # Debug: Log the POST data
        logger.info(f"Bulk delete POST data: {dict(request.POST)}")
        logger.info(f"Content type: {request.content_type}")
        
        # Try to get customer IDs from form data first
        customer_ids = request.POST.getlist('customer_ids[]')
        
        # If no form data, try JSON
        if not customer_ids and request.content_type == 'application/json':
            try:
                import json
                data = json.loads(request.body)
                customer_ids = data.get('customer_ids', [])
            except:
                pass
        
        logger.info(f"Customer IDs to delete: {customer_ids}")
        
        if not customer_ids:
            logger.warning("Bulk delete: No customers selected")
            return JsonResponse({'error': 'No customers selected'}, status=400)
        
        # Filter out invalid UUIDs (like "NaN")
        import uuid
        valid_customer_ids = []
        for customer_id in customer_ids:
            try:
                # Try to validate UUID
                uuid.UUID(str(customer_id))
                valid_customer_ids.append(customer_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid customer ID: {customer_id}")
                continue
        
        if not valid_customer_ids:
            logger.warning("Bulk delete: No valid customer IDs found")
            return JsonResponse({'error': 'No valid customer IDs found'}, status=400)
        
        logger.info(f"Valid customer IDs: {valid_customer_ids}")
        
        # Validate customer IDs exist
        valid_customers = Customer.objects.filter(
            customer_id__in=valid_customer_ids,
            tenant=tenant
        )
        logger.info(f"Found {valid_customers.count()} valid customers to delete")
        
        if valid_customers.count() == 0:
            logger.warning("Bulk delete: No valid customers found")
            return JsonResponse({'error': 'No valid customers found'}, status=400)
        
        # Delete customers
        deleted_count = valid_customers.delete()[0]
        logger.info(f"Successfully deleted {deleted_count} customers")
        
        return JsonResponse({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully deleted {deleted_count} customer(s)'
        })
        
    except Exception as e:
        logger.error(f"Bulk delete error: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
def upload_image(request):
    """Handle image upload via AJAX using Cloudinary cloud storage"""
    if request.method == 'POST':
        
        if request.FILES.get('image'):
            # Handle file upload
            image = request.FILES['image']
            
            # Validate file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                return JsonResponse({
                    'success': False, 
                    'error': 'Image too large. Maximum size is 10MB.'
                })
            
            # Upload to Cloudinary
            result = cloudinary_service.upload_file(image)
            
            if result['success']:
                return JsonResponse({
                    'success': True, 
                    'file_url': result['url'],
                    'public_id': result['public_id'],
                    'width': result.get('width'),
                    'height': result.get('height'),
                    'file_size': result.get('bytes'),
                    'storage_type': 'cloudinary',
                    'message': 'Image uploaded successfully to Cloudinary'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': result['error']
                })
        
        elif request.POST.get('base64_image'):
            # Handle base64 image data from JavaScript
            base64_data = request.POST.get('base64_image')
            original_filename = request.POST.get('filename', 'uploaded_image.jpg')
            
            # Upload base64 to Cloudinary
            result = cloudinary_service.upload_base64(base64_data, original_filename)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'file_url': result['url'],
                    'public_id': result['public_id'],
                    'width': result.get('width'),
                    'height': result.get('height'),
                    'file_size': result.get('bytes'),
                    'storage_type': 'cloudinary',
                    'message': 'Base64 image uploaded successfully to Cloudinary'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': result['error']
                })
            
    return JsonResponse({'success': False, 'error': 'No image provided'})

def serve_temp_image(request, file_id):
    """Serve temporary private images"""
    temp_storage = TemporaryImageStorage()
    return temp_storage.serve_file(file_id)

@csrf_exempt
def send_bulk_message(request):
    """Handle sending bulk messages via WhatsApp API"""
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Create message
        message = Message.objects.create(
            text_content=data.get('message', '')
        )
        
        # Handle image if provided
        image_url = None
        if data.get('image_url'):
            # Check if it's a Cloudinary URL or other proper URL
            if data['image_url'].startswith('data:image'):
                # Base64 images - convert to Cloudinary
                print("INFO: Converting base64 image to Cloudinary URL...")
                result = cloudinary_service.upload_base64(data['image_url'])
                if result['success']:
                    image_url = result['url']
                    print(f"SUCCESS: Base64 image converted to Cloudinary: {image_url}")
                else:
                    print(f"ERROR: Failed to convert base64 to Cloudinary: {result['error']}")
                    image_url = None
            elif data['image_url'].startswith('http'):
                # It's already a proper URL - Cloudinary URLs are always accessible
                image_url = data['image_url']
                print(f"INFO: Using image URL: {image_url}")
                
                # Check if it's a Cloudinary URL (always reliable)
                if 'cloudinary.com' in image_url:
                    print("✅ Cloudinary URL detected - reliable for WhatsApp API")
                elif 'localhost' in image_url or 'testserver' in image_url or '127.0.0.1' in image_url:
                    print("⚠️ WARNING: Using localhost URL - WhatsApp API cannot access this!")
                else:
                    print("INFO: External URL - should be accessible to WhatsApp API")
            else:
                print(f"WARNING: Unknown image URL format: {data['image_url']}")
                image_url = None
            
        # Create bulk message and add recipients
        bulk_message = BulkMessage.objects.create(message=message)
        recipient_ids = data.get('recipients', [])
        
        # Initialize WhatsApp service
        wa_service = WhatsAppAPIService()
        
        print(f"DEBUG: WhatsApp service initialized with:")  # Debug log
        print(f"  - access_token: {wa_service.access_token}")  # Debug log
        print(f"  - instance_id: {wa_service.instance_id}")  # Debug log
        print(f"  - base_url: {wa_service.base_url}")  # Debug log
        
        # Use instance ID from settings if not already set
        if not wa_service.instance_id:
            from django.conf import settings
            default_instance = getattr(settings, 'WHATSAPP_API', {}).get('DEFAULT_INSTANCE_ID')
            if default_instance:
                wa_service.set_instance_id(default_instance)
                print(f"DEBUG: Set instance_id from settings: {default_instance}")  # Debug log
            else:
                print("DEBUG: No default instance ID found in settings")  # Debug log
        
        successful_sends = 0
        failed_sends = 0
        
        print(f"DEBUG: Processing {len(recipient_ids)} recipients")  # Debug log
        
        for recipient_id in recipient_ids:
            try:
                customer = Customer.objects.get(customer_id=recipient_id, tenant=_get_tenant(request))
                bulk_message.recipients.add(customer)
                
                print(f"DEBUG: Sending to {customer.name} ({customer.phone_number})")  # Debug log
                
                # Send via WhatsApp API
                if image_url:
                    print(f"DEBUG: Sending media message with URL: {image_url}")  # Debug log
                    # Send media message
                    result = wa_service.send_media_message(
                        customer.phone_number, 
                        data.get('message', ''), 
                        image_url
                    )
                else:
                    print(f"DEBUG: Sending text message: {data.get('message', '')}")  # Debug log
                    # Send text message
                    result = wa_service.send_text_message(
                        customer.phone_number, 
                        data.get('message', '')
                    )
                
                print(f"DEBUG: WhatsApp API result: {result}")  # Debug log
                
                if result['success']:
                    successful_sends += 1
                    print(f"DEBUG: Successfully sent to {customer.phone_number}")  # Debug log
                else:
                    failed_sends += 1
                    print(f"DEBUG: Failed to send to {customer.phone_number}: {result.get('error', 'Unknown error')}")  # Debug log
                    
            except Customer.DoesNotExist:
                failed_sends += 1
                print(f"DEBUG: Customer with ID {recipient_id} not found")  # Debug log
                continue
        
        if successful_sends > 0:
            return JsonResponse({
                'success': True, 
                'message': f'Message sent successfully to {successful_sends} recipients. {failed_sends} failed.',
                'successful_sends': successful_sends,
                'failed_sends': failed_sends
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': f'Failed to send message to all {failed_sends} recipients.',
                'successful_sends': successful_sends,
                'failed_sends': failed_sends
            })
        
    return JsonResponse({'success': False})

@csrf_exempt
def import_excel(request):
    """
    Import contacts from an Excel file.
    - Accepts .xlsx (openpyxl) and .xls (xlrd==1.2.0 only).
    - Auto-detects headers and maps common column names.
    - Falls back to positional mapping when headers are missing.
    - Enriches with event_source / event_date from modal (preferred) or Excel.
    - Dedupes by phone; updates existing contacts' events_participated/events_count.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Use POST for file upload.'}, status=405)

    # --- Defensive checks for multipart upload
    if 'excel_file' not in request.FILES:
        # Helpful diagnostics (leave during troubleshooting; remove later)
        ct = request.META.get('CONTENT_TYPE', '')
        return JsonResponse({
            'success': False,
            'message': 'No file received. Ensure you POST multipart/form-data with a field named "excel_file".',
            'debug': {
                'content_type': ct,
                'files_keys': list(request.FILES.keys()),
                'post_keys': list(request.POST.keys()),
            }
        }, status=400)

    excel_file = request.FILES['excel_file']
    filename = excel_file.name or ''
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    if ext not in ('xlsx', 'xls'):
        return JsonResponse({'success': False, 'message': 'Unsupported file type. Please upload .xlsx or .xls.'}, status=400)

    # --- Pick engine by extension, with clear error if missing
    if ext == 'xlsx':
        engine = 'openpyxl'
        try:
            import openpyxl  # noqa: F401
        except Exception:
            return JsonResponse({
                'success': False,
                'message': 'openpyxl is required to read .xlsx files. Install with: pip install openpyxl'
            }, status=500)
    else:  # .xls
        engine = 'xlrd'
        try:
            import xlrd  # noqa: F401
            # xlrd>=2.0 removed xls support; we need 1.2.0
            import pkg_resources
            ver = pkg_resources.get_distribution('xlrd').version
            if tuple(map(int, ver.split('.')[:2])) >= (2, 0):
                return JsonResponse({
                    'success': False,
                    'message': 'xlrd>=2.0 no longer supports .xls. Install xlrd==1.2.0 for .xls files.'
                }, status=500)
        except Exception:
            return JsonResponse({
                'success': False,
                'message': 'xlrd==1.2.0 is required to read .xls files. Install with: pip install "xlrd==1.2.0"'
            }, status=500)

    # --- Optional metadata from modal
    event_source_modal = (request.POST.get('event_source') or '').strip() or 'Manual Import'
    event_date_modal = None
    if request.POST.get('event_date'):
        from datetime import datetime
        try:
            event_date_modal = datetime.strptime(request.POST['event_date'].strip(), '%Y-%m-%d').date()
        except ValueError:
            event_date_modal = None  # ignore invalid date

    # --- Read workbook: try with header row, if that fails fallback to header=None
    try:
        try:
            # Try assuming headers exist
            all_sheets = pd.read_excel(excel_file, sheet_name=None, engine=engine, header=0)
            headerless = False
        except Exception:
            # Retry as headerless
            excel_file.seek(0)
            all_sheets = pd.read_excel(excel_file, sheet_name=None, engine=engine, header=None)
            headerless = True
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error reading Excel file: {e}'}, status=400)

    total_processed = added = duplicates = errors = sheets_processed = 0
    error_details = []
    all_contacts = []

    # State mapping table (normalize inputs)
    state_mapping = {
        'selangor': 'SEL', 'sel': 'SEL',
        'kl': 'KUL', 'kuala lumpur': 'KUL', 'w.p. kuala lumpur': 'KUL',
        'johor': 'JHR', 'jhr': 'JHR',
        'penang': 'PNG', 'pulau pinang': 'PNG', 'png': 'PNG',
        'perak': 'PRK', 'prk': 'PRK',
        'sabah': 'SBH', 'sbh': 'SBH',
        'sarawak': 'SWK', 'swk': 'SWK',
        'kedah': 'KDH', 'kdh': 'KDH',
        'kelantan': 'KTN', 'ktn': 'KTN',
        'pahang': 'PHG', 'phg': 'PHG',
        'terengganu': 'TRG', 'trg': 'TRG', 'trengganu': 'TRG',
        'melaka': 'MLK', 'malacca': 'MLK', 'mlk': 'MLK',
        'negeri sembilan': 'NSN', 'n. sembilan': 'NSN', 'nsn': 'NSN',
        'perlis': 'PLS', 'pls': 'PLS',
        'putrajaya': 'PJY', 'pjy': 'PJY', 'w.p. putrajaya': 'PJY',
        'labuan': 'LBN', 'lbn': 'LBN', 'w.p. labuan': 'LBN'
    }

    # Helper: find best-effort column mapping
    def build_column_map(df: pd.DataFrame):
        col_map = {}
        if headerless:
            # No headers -> positional guess: col0=name, col1=phone if present
            if df.shape[1] >= 1: col_map['name'] = 0
            if df.shape[1] >= 2: col_map['phone'] = 1
            # Optional columns if present
            if df.shape[1] >= 3: col_map['state'] = 2
            if df.shape[1] >= 4: col_map['gender'] = 3
            if df.shape[1] >= 5: col_map['race'] = 4
            if df.shape[1] >= 6: col_map['date_added'] = 5
            if df.shape[1] >= 7: col_map['event_source'] = 6
            if df.shape[1] >= 8: col_map['event_date'] = 7
            return col_map

        # With headers: normalize and match
        headers = [str(c).strip().lower() for c in df.columns]
        for i, h in enumerate(headers):
            if any(x in h for x in ['name', 'nama']): col_map['name'] = i
            elif any(x in h for x in ['phone', 'telefon', 'mobile']): col_map['phone'] = i
            elif any(x in h for x in ['state', 'negeri']): col_map['state'] = i
            elif any(x in h for x in ['gender', 'jantina']): col_map['gender'] = i
            elif any(x in h for x in ['race', 'bangsa', 'ethnicity']): col_map['race'] = i
            elif any(x in h for x in ['date', 'tarikh', 'added']): col_map['date_added'] = i
            elif any(x in h for x in ['event date', 'event_date', 'tarikh_acara']): col_map['event_date'] = i
            elif any(x in h for x in ['event', 'acara', 'source']): col_map['event_source'] = i

        # Ensure at least name/phone via positional fallback
        if 'name' not in col_map and df.shape[1] >= 1: col_map['name'] = 0
        if 'phone' not in col_map and df.shape[1] >= 2: col_map['phone'] = 1
        return col_map

    # Iterate sheets
    for sheet_name, df in (all_sheets or {}).items():
        sheets_processed += 1
        if df is None or df.empty:
            continue

        col_map = build_column_map(df)

        # Validate minimum columns
        if 'name' not in col_map or 'phone' not in col_map:
            errors += 1
            error_details.append(f"Sheet '{sheet_name}': couldn't find Name/Phone columns.")
            continue

        for i, row in df.iterrows():
            try:
                def get(idx_key, default=''):
                    idx = col_map.get(idx_key)
                    if idx is None or idx >= len(row): return default
                    val = row.iloc[idx]
                    return '' if pd.isna(val) else str(val).strip()

                name = get('name')
                phone_raw = get('phone')

                if not name or not phone_raw:
                    continue

                # Clean phone (allow leading +)
                phone_clean = re.sub(r'[^\d+]', '', phone_raw)
                if len(re.sub(r'[^\d]', '', phone_clean)) < 10:
                    errors += 1
                    # +2 for typical header row; headerless uses +1, but message is informative enough
                    error_details.append(f"Sheet '{sheet_name}', Row {i + 2}: Invalid phone '{phone_raw}'")
                    continue

                # Optional fields
                raw_state = get('state') or 'N/A'
                state_code = state_mapping.get(raw_state.lower(), 'N/A')

                raw_gender = get('gender')
                raw_race = get('race')

                # Demographics processor (your helper functions)
                demographics = process_demographics(
                    name=name,
                    race=raw_race,
                    gender=raw_gender
                )
                gender_code = get_gender_code(demographics.get('gender', ''))
                race_code = get_race_code(demographics.get('race', ''))

                # date_added
                date_added = None
                raw_date = get('date_added', '')
                if raw_date:
                    try:
                        from datetime import datetime
                        if isinstance(row.iloc[col_map['date_added']], str):
                            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y'):
                                try:
                                    date_added = datetime.strptime(raw_date, fmt).date()
                                    break
                                except ValueError:
                                    continue
                        else:
                            date_added = pd.to_datetime(row.iloc[col_map['date_added']]).date()
                    except Exception:
                        date_added = None

                # event_source: prefer modal; fallback excel column
                excel_event_source = get('event_source', '')
                final_event_source = event_source_modal if event_source_modal != 'Manual Import' else (excel_event_source or event_source_modal)

                # event_date: prefer modal; fallback excel column
                excel_event_date = None
                if 'event_date' in col_map:
                    try:
                        raw_ev = row.iloc[col_map['event_date']]
                        if pd.notna(raw_ev):
                            from datetime import datetime
                            if isinstance(raw_ev, str):
                                for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y'):
                                    try:
                                        excel_event_date = datetime.strptime(raw_ev.strip(), fmt).date()
                                        break
                                    except ValueError:
                                        continue
                            else:
                                excel_event_date = pd.to_datetime(raw_ev).date()
                    except Exception:
                        excel_event_date = None

                final_event_date = event_date_modal if event_date_modal else excel_event_date

                all_contacts.append({
                    'name': name,
                    'phone': phone_clean,
                    'state': state_code,
                    'gender': gender_code,
                    'race': race_code,
                    'date_added': date_added,
                    'event_source': final_event_source,
                    'event_date': final_event_date,
                    'source': f"{sheet_name}:Row{i + (2 if not headerless else 1)}"
                })
                total_processed += 1
            except Exception as e:
                errors += 1
                error_details.append(f"Sheet '{sheet_name}', Row {i + 2}: {e}")

    if not all_contacts:
        return JsonResponse({
            'success': False,
            'message': 'No valid contacts found. Ensure your file has at least Name and Phone columns.'
        }, status=400)

    # De-dup within the upload by phone
    unique_by_phone = {}
    within_upload_dups = 0
    for c in all_contacts:
        if c['phone'] in unique_by_phone:
            within_upload_dups += 1
        else:
            unique_by_phone[c['phone']] = c

    # Insert/update
    from .models import Contact
    with transaction.atomic():
        for c in unique_by_phone.values():
            existing = Contact.objects.filter(phone_number=c['phone']).first()
            if existing:
                # Update events participation if this is a new event for the contact
                existing_events = (existing.events_participated or '').split(',')
                existing_events = [e.strip() for e in existing_events if e.strip()]
                if c['event_source'] and c['event_source'] not in existing_events:
                    existing_events.append(c['event_source'])
                    existing.events_participated = ','.join(existing_events)
                    existing.events_count = len(existing_events)
                    # Update event latest info (optional)
                    existing.event_source = c['event_source']
                    existing.event_date = c['event_date']
                    existing.save()
                duplicates += 1
                continue

            # Create new contact
            events_list = [c['event_source']] if c['event_source'] else []
            Contact.objects.create(
                name=c['name'],
                phone_number=c['phone'],
                state=c['state'],
                gender=c['gender'],
                race=c['race'],
                date_added=c['date_added'],
                event_source=c['event_source'],
                event_date=c['event_date'],
                events_participated=','.join(events_list),
                events_count=len(events_list)
            )
            added += 1

    duplicates += within_upload_dups

    msg = f"Successfully imported {added} new customer(s)."
    if duplicates: msg += f" {duplicates} duplicate(s) were skipped or updated."
    if errors: msg += f" {errors} error(s) encountered."

    return JsonResponse({
        'success': True,
        'message': msg,
        'summary': {
            'total_processed': total_processed,
            'added': added,
            'duplicates': duplicates,
            'errors': errors,
            'sheets_processed': sheets_processed,
            'event_source': event_source_modal,
            'event_date': event_date_modal.strftime('%Y-%m-%d') if event_date_modal else None
        },
        'error_details': error_details[:10]
    })


# CRM API Views
@csrf_exempt
def campaign_list(request):
    """List all campaigns"""
    if request.method == 'GET':
        campaigns = Campaign.objects.all().order_by('-created_at')
        campaigns_data = []
        
        for campaign in campaigns:
            campaigns_data.append({
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'objective': campaign.objective,
                'status': campaign.status,
                'total_recipients': campaign.get_total_recipients(),
                'total_sent': campaign.total_sent,
                'total_delivered': campaign.total_delivered,
                'total_read': campaign.total_read,
                'total_clicked': campaign.total_clicked,
                'total_converted': campaign.total_converted,
                'created_at': campaign.created_at.isoformat(),
                'scheduled_start': campaign.scheduled_start.isoformat() if campaign.scheduled_start else None,
                'scheduled_end': campaign.scheduled_end.isoformat() if campaign.scheduled_end else None,
            })
        
        return JsonResponse({'success': True, 'campaigns': campaigns_data})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_campaign(request):
    """Create a new campaign"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create campaign
            campaign = Campaign.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                objective=data.get('objective', 'ANNOUNCEMENT'),
                message_text=data.get('message', ''),
                landing_url=data.get('source_url'),
                scheduled_start=data.get('schedule', {}).get('start'),
                scheduled_end=data.get('schedule', {}).get('end'),
            )
            
            # Add segments
            segment_ids = data.get('segments', [])
            for segment_id in segment_ids:
                try:
                    segment = CustomerSegment.objects.get(id=segment_id)
                    campaign.segments.add(segment)
                except CustomerSegment.DoesNotExist:
                    pass
            
            # Add custom recipients
            recipient_ids = data.get('recipients', [])
            for recipient_id in recipient_ids:
                try:
                    contact = Contact.objects.get(id=recipient_id)
                    campaign.custom_recipients.add(contact)
                except Contact.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': True, 
                'message': 'Campaign created successfully',
                'campaign_id': campaign.id
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def campaign_detail(request, campaign_id):
    """Get campaign details"""
    if request.method == 'GET':
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Get segments
            segments = []
            for segment in campaign.segments.all():
                segments.append({
                    'id': segment.id,
                    'name': segment.name,
                    'customer_count': segment.get_customer_count()
                })
            
            # Get custom recipients
            recipients = []
            for contact in campaign.custom_recipients.all():
                recipients.append({
                    'id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone_number
                })
            
            campaign_data = {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'objective': campaign.objective,
                'status': campaign.status,
                'message_text': campaign.message_text,
                'landing_url': campaign.landing_url,
                'segments': segments,
                'custom_recipients': recipients,
                'total_recipients': campaign.get_total_recipients(),
                'total_sent': campaign.total_sent,
                'total_delivered': campaign.total_delivered,
                'total_read': campaign.total_read,
                'total_clicked': campaign.total_clicked,
                'total_converted': campaign.total_converted,
                'created_at': campaign.created_at.isoformat(),
                'scheduled_start': campaign.scheduled_start.isoformat() if campaign.scheduled_start else None,
                'scheduled_end': campaign.scheduled_end.isoformat() if campaign.scheduled_end else None,
            }
            
            return JsonResponse({'success': True, 'campaign': campaign_data})
            
        except Campaign.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Campaign not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def segment_list(request):
    """List all customer segments"""
    if request.method == 'GET':
        segments = CustomerSegment.objects.all().order_by('-created_at')
        segments_data = []
        
        for segment in segments:
            segments_data.append({
                'id': segment.id,
                'name': segment.name,
                'description': segment.description,
                'customer_count': segment.get_customer_count(),
                'min_spending': float(segment.min_spending) if segment.min_spending else None,
                'max_spending': float(segment.max_spending) if segment.max_spending else None,
                'min_age': segment.min_age,
                'max_age': segment.max_age,
                'gender_filter': segment.gender_filter,
                'marital_status_filter': segment.marital_status_filter,
                'state_filter': segment.state_filter,
                'customer_tier_filter': segment.customer_tier_filter,
                'created_at': segment.created_at.isoformat(),
            })
        
        return JsonResponse({'success': True, 'segments': segments_data})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_segment(request):
    """Create a new customer segment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            segment = CustomerSegment.objects.create(
                name=data.get('name'),
                description=data.get('description', ''),
                min_spending=data.get('min_spending'),
                max_spending=data.get('max_spending'),
                min_age=data.get('min_age'),
                max_age=data.get('max_age'),
                gender_filter=data.get('gender_filter', 'N/A'),
                marital_status_filter=data.get('marital_status_filter', 'N/A'),
                state_filter=data.get('state_filter', 'N/A'),
                customer_tier_filter=data.get('customer_tier_filter', ''),
                custom_filters=data.get('custom_filters', {})
            )
            
            return JsonResponse({
                'success': True, 
                'message': 'Segment created successfully',
                'segment_id': segment.id,
                'customer_count': segment.get_customer_count()
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def segment_detail(request, segment_id):
    """Get segment details and customers"""
    if request.method == 'GET':
        try:
            segment = CustomerSegment.objects.get(id=segment_id)
            customers = segment.get_customers()
            
            customers_data = []
            for customer in customers:
                customers_data.append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone_number,
                    'age': customer.age,
                    'gender': customer.gender,
                    'state': customer.state,
                    'marital_status': customer.marital_status,
                    'total_spent': float(customer.total_spent),
                    'customer_tier': customer.customer_tier,
                    'purchase_count': customer.purchase_count,
                    'last_purchase_date': customer.last_purchase_date.isoformat() if customer.last_purchase_date else None,
                })
            
            segment_data = {
                'id': segment.id,
                'name': segment.name,
                'description': segment.description,
                'customer_count': segment.get_customer_count(),
                'min_spending': float(segment.min_spending) if segment.min_spending else None,
                'max_spending': float(segment.max_spending) if segment.max_spending else None,
                'min_age': segment.min_age,
                'max_age': segment.max_age,
                'gender_filter': segment.gender_filter,
                'marital_status_filter': segment.marital_status_filter,
                'state_filter': segment.state_filter,
                'customer_tier_filter': segment.customer_tier_filter,
                'customers': customers_data,
                'created_at': segment.created_at.isoformat(),
            }
            
            return JsonResponse({'success': True, 'segment': segment_data})
            
        except CustomerSegment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Segment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def customer_purchases(request, customer_id):
    """Get customer purchase history"""
    if request.method == 'GET':
        try:
            customer = Contact.objects.get(id=customer_id)
            purchases = customer.purchases.all().order_by('-purchase_date')
            
            purchases_data = []
            for purchase in purchases:
                purchases_data.append({
                    'id': purchase.id,
                    'total_amount': float(purchase.total_amount),
                    'purchase_date': purchase.purchase_date.isoformat(),
                    'items': purchase.items,
                    'receipt_text': purchase.receipt_text,
                    'ocr_processed': purchase.ocr_processed,
                    'ocr_confidence': float(purchase.ocr_confidence) if purchase.ocr_confidence else None,
                    'created_at': purchase.created_at.isoformat(),
                })
            
            customer_data = {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone_number,
                'total_spent': float(customer.total_spent),
                'average_spend': float(customer.average_spend),
                'purchase_count': customer.purchase_count,
                'customer_tier': customer.customer_tier,
                'last_purchase_date': customer.last_purchase_date.isoformat() if customer.last_purchase_date else None,
                'purchases': purchases_data
            }
            
            return JsonResponse({'success': True, 'customer': customer_data})
            
        except Contact.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def process_ocr(request):
    """Process image with OCR"""
    if request.method == 'POST':
        try:
            # Get tenant
            tenant = _get_tenant(request)
            if not tenant:
                return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            
            phone_number = request.POST.get('phone_number', '')
            if not phone_number:
                return JsonResponse({'success': False, 'error': 'Phone number required'}, status=400)
            
            if request.FILES.get('image'):
                # Handle file upload
                image = request.FILES['image']
                
                # Upload to Cloudinary
                result = cloudinary_service.upload_file(image)
                
                if result['success']:
                    # Process with OCR
                    ocr_service = OCRService()
                    ocr_result = ocr_service.process_image(result['url'], tenant, phone_number)
                    
                    return JsonResponse({
                        'success': True,
                        'image_url': result['url'],
                        'ocr_result': ocr_result
                    })
                else:
                    return JsonResponse({'success': False, 'error': result['error']})
            
            elif request.POST.get('image_url'):
                # Handle URL
                image_url = request.POST.get('image_url')
                
                # Process with OCR
                ocr_service = OCRService()
                ocr_result = ocr_service.process_image(image_url, tenant, phone_number)
                
                return JsonResponse({
                    'success': True,
                    'image_url': image_url,
                    'ocr_result': ocr_result
                })
            
            else:
                return JsonResponse({'success': False, 'error': 'No image provided'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def incoming_messages(request):
    """Display incoming messages from customers/contestants"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    # Get incoming messages for this tenant
    messages = CoreMessage.objects.filter(
        tenant=tenant,
        direction='inbound'
    ).select_related('conversation__customer').order_by('-received_at', '-created_at')[:100]
    
    # Get unique customers who have sent messages
    customers_with_messages = Customer.objects.filter(
        tenant=tenant,
        conversations__messages__direction='inbound'
    ).distinct().order_by('name')
    
    # Filter by customer if specified
    customer_id = request.GET.get('customer_id')
    if customer_id:
        messages = messages.filter(conversation__customer__customer_id=customer_id)
    
    # Filter by date range if specified
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        messages = messages.filter(received_at__gte=date_from)
    if date_to:
        messages = messages.filter(received_at__lte=date_to)
    
    context = {
        'messages': messages,
        'customers': customers_with_messages,
        'selected_customer_id': customer_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'messaging/incoming_messages.html', context)


@login_required
def customer_detail(request, customer_id):
    """Display customer detail page with message history"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    try:
        customer = Customer.objects.get(customer_id=customer_id, tenant=tenant)
    except Customer.DoesNotExist:
        return redirect('manage_customers')
    
    # Get all conversations for this customer
    conversations = Conversation.objects.filter(
        tenant=tenant,
        customer=customer
    ).order_by('-last_message_at', '-created_at')
    
    # Get all messages for this customer across all conversations
    messages = CoreMessage.objects.filter(
        tenant=tenant,
        conversation__customer=customer
    ).select_related('conversation').order_by('-created_at')[:100]
    
    # Get message statistics
    total_messages = messages.count()
    inbound_messages = messages.filter(direction='inbound').count()
    outbound_messages = messages.filter(direction='outbound').count()
    
    # Get recent activity (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_messages = messages.filter(created_at__gte=thirty_days_ago).count()
    
    # Get consent information
    from .pdpa_service import PDPAConsentService
    pdpa_service = PDPAConsentService()
    consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
    
    # Get consent history
    consent_history = Consent.objects.filter(
        tenant=tenant,
        customer=customer,
        type='whatsapp'
    ).order_by('-occurred_at')[:10]
    
    context = {
        'customer': customer,
        'conversations': conversations,
        'messages': messages,
        'total_messages': total_messages,
        'inbound_messages': inbound_messages,
        'outbound_messages': outbound_messages,
        'recent_messages': recent_messages,
        'consent_status': consent_status,
        'consent_history': consent_history,
    }
    return render(request, 'messaging/customer_detail.html', context)


@login_required
def pdpa_settings(request):
    """PDPA consent management settings page"""
    tenant = _get_tenant(request)
    if not tenant:
        return redirect('auth_login')
    
    # Get consent statistics
    total_customers = Customer.objects.filter(tenant=tenant).count()
    granted_consents = Consent.objects.filter(
        tenant=tenant,
        type='whatsapp',
        status='granted'
    ).values('customer').distinct().count()
    
    withdrawn_consents = Consent.objects.filter(
        tenant=tenant,
        type='whatsapp',
        status='withdrawn'
    ).values('customer').distinct().count()
    
    no_consent = total_customers - granted_consents - withdrawn_consents
    
    # Get recent consent activities
    recent_consents = Consent.objects.filter(
        tenant=tenant,
        type='whatsapp'
    ).select_related('customer').order_by('-occurred_at')[:20]
    
    context = {
        'tenant': tenant,
        'total_customers': total_customers,
        'granted_consents': granted_consents,
        'withdrawn_consents': withdrawn_consents,
        'no_consent': no_consent,
        'recent_consents': recent_consents,
    }
    return render(request, 'messaging/pdpa_settings.html', context)


@login_required
@csrf_exempt
def toggle_contest_status(request):
    """Toggle contest active status via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    tenant = _get_tenant(request)
    if not tenant:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    if not _require_plan(tenant, 'contest'):
        return JsonResponse({'success': False, 'error': 'Contest plan required'}, status=403)
    
    try:
        import json
        data = json.loads(request.body)
        contest_id = data.get('contest_id')
        new_status = data.get('is_active', False)
        
        if not contest_id:
            return JsonResponse({'success': False, 'error': 'Contest ID required'}, status=400)
        
        # Handle hardcoded contests
        hardcoded_contests = {
            'merdeka_w1': {'name': 'Khind Merdeka W1', 'is_active': True},
            'merdeka_w2': {'name': 'Khind Merdeka W2', 'is_active': True},
            'merdeka_w3': {'name': 'Khind Merdeka W3', 'is_active': False}
        }
        
        if contest_id in hardcoded_contests:
            # For hardcoded contests, just return success (no actual database update)
            return JsonResponse({
                'success': True,
                'message': f'Contest {"activated" if new_status else "deactivated"} successfully',
                'is_active': new_status,
                'contest_name': hardcoded_contests[contest_id]['name']
            })
        else:
            # Try to find in database
            try:
                contest = Contest.objects.get(contest_id=contest_id, tenant=tenant)
                contest.is_active = new_status
                contest.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Contest {"activated" if new_status else "deactivated"} successfully',
                    'is_active': contest.is_active,
                    'contest_name': contest.name
                })
            except Contest.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Contest not found'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
