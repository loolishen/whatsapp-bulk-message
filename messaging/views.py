from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import json
import base64
import pandas as pd
import re
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Contact, Message, BulkMessage, Campaign, CustomerSegment, Purchase, WhatsAppMessage, OCRProcessingLog
from .whatsapp_service import WhatsAppAPIService
from .temp_image_storage import TemporaryImageStorage
from .cloudinary_service import cloudinary_service
from safe_demographics import process_demographics, get_race_code, get_gender_code

def main_page(request):
    """Main page with message preview and recipient selection"""
    contacts = Contact.objects.all()
    
    # Filter functionality
    state_filter = request.GET.get('state')
    gender_filter = request.GET.get('gender')
    race_filter = request.GET.get('race')
    
    if state_filter:
        contacts = contacts.filter(state=state_filter)
    if gender_filter:
        contacts = contacts.filter(gender=gender_filter)
    if race_filter:
        contacts = contacts.filter(race=race_filter)
    
    # Convert contacts to JSON for safe JavaScript usage
    contacts_json = json.dumps([
        {
            'id': contact.id, 
            'name': contact.name, 
            'phone': contact.phone_number,
            'state': contact.state,
            'gender': contact.gender,
            'race': contact.race,
            'state_display': contact.get_state_display(),
            'gender_display': contact.get_gender_display(),
            'race_display': contact.get_race_display(),
        } 
        for contact in contacts
    ])
    
    context = {
        'contacts': contacts,
        'contacts_json': contacts_json,
        'state_choices': Contact.STATE_CHOICES,
        'gender_choices': Contact.GENDER_CHOICES,
        'race_choices': Contact.RACE_CHOICES,
        'selected_state': state_filter,
        'selected_gender': gender_filter,
        'selected_race': race_filter,
    }
    
    return render(request, 'messaging/recipients_and_preview.html', context)

def manage_customers(request):
    """Customer management page - add, edit, delete contacts"""
    contacts = Contact.objects.all()
    
    # Filter functionality
    state_filter = request.GET.get('state')
    gender_filter = request.GET.get('gender')
    race_filter = request.GET.get('race')
    
    if state_filter:
        contacts = contacts.filter(state=state_filter)
    if gender_filter:
        contacts = contacts.filter(gender=gender_filter)
    if race_filter:
        contacts = contacts.filter(race=race_filter)
    
    # Get choices for dropdowns
    context = {
        'contacts': contacts,
        'state_choices': Contact.STATE_CHOICES,
        'gender_choices': Contact.GENDER_CHOICES,
        'race_choices': Contact.RACE_CHOICES,
        'selected_state': state_filter,
        'selected_gender': gender_filter,
        'selected_race': race_filter,
    }
    
    return render(request, 'messaging/manage_customers.html', context)


def crm_dashboard(request):
    """Render the CRM dashboard page."""
    return render(request, 'messaging/crm_dashboard.html')  # Use your new CRM HTML template

def analytics_dashboard(request):
    """Analytics dashboard with data visualizations"""
    from django.db.models import Count, Q
    from collections import defaultdict
    import json
    from datetime import datetime, timedelta
    
    contacts = Contact.objects.all()
    
    # Basic statistics
    total_contacts = contacts.count()
    
    # Distribution by State
    state_distribution = []
    for state_code, state_name in Contact.STATE_CHOICES:
        if state_code != 'N/A':
            count = contacts.filter(state=state_code).count()
            if count > 0:
                state_distribution.append({'name': state_name, 'value': count})
    
    # Distribution by Race
    race_distribution = []
    for race_code, race_name in Contact.RACE_CHOICES:
        if race_code != 'N/A':
            count = contacts.filter(race=race_code).count()
            if count > 0:
                race_distribution.append({'name': race_name, 'value': count})
    
    # Distribution by Gender
    gender_distribution = []
    for gender_code, gender_name in Contact.GENDER_CHOICES:
        if gender_code != 'N/A':
            count = contacts.filter(gender=gender_code).count()
            if count > 0:
                gender_distribution.append({'name': gender_name, 'value': count})
    
    # Event Source Distribution
    event_sources = contacts.exclude(Q(event_source='') | Q(event_source__isnull=True)).values('event_source').annotate(count=Count('id')).order_by('-count')
    event_distribution = [{'name': item['event_source'] or 'Unknown Event', 'value': item['count']} for item in event_sources]
    
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
        
        count = contacts.filter(created_at__date__range=[month_start, month_end]).count()
        timeline_data.append({
            'date': month_start.strftime('%Y-%m'),
            'count': count,
            'month': month_start.strftime('%b %Y')
        })
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Event timeline (when events were carried out)
    event_timeline_data = []
    if contacts.filter(event_date__isnull=False).exists():
        event_dates = contacts.exclude(event_date__isnull=True).values('event_date').annotate(count=Count('id')).order_by('event_date')
        for item in event_dates:
            event_timeline_data.append({
                'date': item['event_date'].strftime('%Y-%m-%d'),
                'count': item['count'],
                'display_date': item['event_date'].strftime('%b %d, %Y')
            })
    
    # Cross-tabulation: State vs Race
    state_race_matrix = []
    for state_code, state_name in Contact.STATE_CHOICES:
        if state_code != 'N/A':
            state_data = {'state': state_name}
            for race_code, race_name in Contact.RACE_CHOICES:
                if race_code != 'N/A':
                    count = contacts.filter(state=state_code, race=race_code).count()
                    state_data[race_name.lower()] = count
            if any(v > 0 for k, v in state_data.items() if k != 'state'):
                state_race_matrix.append(state_data)
    
    # Recent registrations (last 30 days)
    recent_date = end_date - timedelta(days=30)
    recent_contacts = contacts.filter(created_at__date__gte=recent_date).order_by('-created_at')[:10]
    
    # Prepare data for Chart.js (separate labels and data arrays)
    state_labels = [item['name'] for item in state_distribution]
    state_data = [item['value'] for item in state_distribution]
    
    race_labels = [item['name'] for item in race_distribution]
    race_data = [item['value'] for item in race_distribution]
    
    gender_labels = [item['name'] for item in gender_distribution]
    gender_data = [item['value'] for item in gender_distribution]
    
    event_source_labels = [item['name'] for item in event_distribution]
    event_source_data = [item['value'] for item in event_distribution]
    
    timeline_labels = [item['month'] for item in timeline_data]
    timeline_counts = [item['count'] for item in timeline_data]
    
    event_timeline_labels = [item['display_date'] for item in event_timeline_data]
    event_timeline_counts = [item['count'] for item in event_timeline_data]
    
    # Cross-tabulation data for template
    cross_tab_races = [race_name for race_code, race_name in Contact.RACE_CHOICES if race_code != 'N/A']
    cross_tabulation = {}
    
    for state_code, state_name in Contact.STATE_CHOICES:
        if state_code != 'N/A':
            race_counts = {}
            total_for_state = 0
            for race_code, race_name in Contact.RACE_CHOICES:
                if race_code != 'N/A':
                    count = contacts.filter(state=state_code, race=race_code).count()
                    race_counts[race_name] = count
                    total_for_state += count
            
            if total_for_state > 0:  # Only include states with contacts
                race_counts['total'] = total_for_state
                cross_tabulation[state_name] = race_counts
    
    context = {
        'total_contacts': total_contacts,
        'unique_states': len([s for s in state_distribution if s['value'] > 0]),
        'unique_events': len([e for e in event_distribution if e['value'] > 0]),
        'recent_additions': contacts.filter(created_at__date__gte=recent_date).count(),
        
        # Chart.js data
        'state_labels': json.dumps(state_labels),
        'state_data': json.dumps(state_data),
        'race_labels': json.dumps(race_labels),
        'race_data': json.dumps(race_data),
        'gender_labels': json.dumps(gender_labels),
        'gender_data': json.dumps(gender_data),
        'event_source_labels': json.dumps(event_source_labels),
        'event_source_data': json.dumps(event_source_data),
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_data': json.dumps(timeline_counts),
        'event_timeline_labels': json.dumps(event_timeline_labels),
        'event_timeline_data': json.dumps(event_timeline_counts),
        
        # Cross-tabulation data
        'cross_tabulation': cross_tabulation,
        'cross_tab_races': cross_tab_races,
        
        # Recent contacts
        'recent_contacts': recent_contacts,
    }
    
    return render(request, 'messaging/analytics_dashboard.html', context)

def add_contact(request):
    """Add a new contact"""
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        state = request.POST.get('state', 'N/A')
        gender = request.POST.get('gender', 'N/A')
        race = request.POST.get('race', 'N/A')
        event_source = request.POST.get('event_source', 'Manual Entry')
        date_added = request.POST.get('date_added')
        
        if name and phone:
            contact_data = {
                'name': name,
                'phone_number': phone,
                'state': state,
                'gender': gender,
                'race': race,
                'event_source': event_source
            }
            
            # Handle date_added - convert to proper format or set to None
            if date_added:
                try:
                    from datetime import datetime
                    contact_data['date_added'] = datetime.strptime(date_added, '%Y-%m-%d').date()
                except ValueError:
                    contact_data['date_added'] = None
            else:
                contact_data['date_added'] = None
                
            Contact.objects.create(**contact_data)
            
        # Redirect based on where the form was submitted from
        if request.POST.get('redirect_to') == 'customers':
            return redirect('manage_customers')
        else:
            return redirect('main_page')
    
    return redirect('main_page')

def edit_contact(request, contact_id):
    """Edit an existing contact"""
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == 'POST':
        contact.name = request.POST.get('name', contact.name)
        contact.phone_number = request.POST.get('phone', contact.phone_number)
        contact.state = request.POST.get('state', contact.state)
        contact.gender = request.POST.get('gender', contact.gender)
        contact.race = request.POST.get('race', contact.race)
        contact.event_source = request.POST.get('event_source', contact.event_source)
        
        # Handle date_added
        date_added = request.POST.get('date_added')
        if date_added:
            try:
                from datetime import datetime
                contact.date_added = datetime.strptime(date_added, '%Y-%m-%d').date()
            except ValueError:
                contact.date_added = None
        else:
            contact.date_added = None
            
        contact.save()
        return redirect('manage_customers')
    
    return redirect('manage_customers')

def delete_contact(request, contact_id):
    """Delete a contact"""
    contact = get_object_or_404(Contact, id=contact_id)
    contact.delete()
    return redirect('manage_customers')

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
                contact = Contact.objects.get(id=recipient_id)
                bulk_message.recipients.add(contact)
                
                print(f"DEBUG: Sending to {contact.name} ({contact.phone_number})")  # Debug log
                
                # Send via WhatsApp API
                if image_url:
                    print(f"DEBUG: Sending media message with URL: {image_url}")  # Debug log
                    # Send media message
                    result = wa_service.send_media_message(
                        contact.phone_number, 
                        data.get('message', ''), 
                        image_url
                    )
                else:
                    print(f"DEBUG: Sending text message: {data.get('message', '')}")  # Debug log
                    # Send text message
                    result = wa_service.send_text_message(
                        contact.phone_number, 
                        data.get('message', '')
                    )
                
                print(f"DEBUG: WhatsApp API result: {result}")  # Debug log
                
                if result['success']:
                    successful_sends += 1
                    print(f"DEBUG: Successfully sent to {contact.phone_number}")  # Debug log
                else:
                    failed_sends += 1
                    print(f"DEBUG: Failed to send to {contact.phone_number}: {result.get('error', 'Unknown error')}")  # Debug log
                    
            except Contact.DoesNotExist:
                failed_sends += 1
                print(f"DEBUG: Contact with ID {recipient_id} not found")  # Debug log
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
            if request.FILES.get('image'):
                # Handle file upload
                image = request.FILES['image']
                image_type = request.POST.get('image_type', 'OTHER')
                
                # Upload to Cloudinary
                result = cloudinary_service.upload_file(image)
                
                if result['success']:
                    # Process with OCR
                    from .ocr_service import OCRService
                    ocr_service = OCRService()
                    ocr_result = ocr_service.process_image(result['url'], image_type)
                    
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
                image_type = request.POST.get('image_type', 'OTHER')
                
                # Process with OCR
                from .ocr_service import OCRService
                ocr_service = OCRService()
                ocr_result = ocr_service.process_image(image_url, image_type)
                
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

