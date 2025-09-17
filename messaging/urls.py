from django.urls import path
from . import views
from .debug_webhook import debug_webhook

# Guard views that may import legacy models before migrations
def _safe(view_func):
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Exception:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': 'Endpoint temporarily unavailable during migration.'}, status=503)
    return wrapper
from .whatsapp_webhook import whatsapp_webhook

urlpatterns = [
    # Root -> contest
    path('', views.contest_home, name='dashboard'),

    # Auth
    path('login/', views.auth_login, name='auth_login'),
    path('logout/', views.auth_logout, name='auth_logout'),

    # Contest management
    path('contest/', views.contest_home, name='contest_home'),
    path('contest/create/', views.contest_create, name='contest_create'),
    path('contest/<str:contest_id>/', views.contest_detail, name='contest_detail'),
    path('contest/<str:contest_id>/entries/', views.contest_entries, name='contest_entries'),
    path('contest/entry/<str:entry_id>/verify/', views.contest_verify_entry, name='contest_verify_entry'),
    path('contest/analytics/', views.contest_analytics, name='contest_analytics'),
    
    # Legacy contest URLs (for backward compatibility)
    path('contest/contacts/', views.contest_contacts, name='contest_contacts'),
    path('contest/contacts/add/', views.contest_add_contact, name='contest_add_contact'),
    path('contest/send/', views.contest_send_message, name='contest_send_message'),
    path('contest/winner/', views.contest_select_winner, name='contest_select_winner'),

    # CRM
    path('crm/', views.crm_home, name='crm_home'),
    path('crm/prompts/', views.crm_prompt_replies, name='crm_prompt_replies'),
    path('crm/prompts/add/', views.crm_add_prompt_reply, name='crm_add_prompt_reply'),
    path('crm/schedule/', views.crm_schedule_message, name='crm_schedule_message'),
    path('crm/campaigns/', views.crm_campaigns, name='crm_campaigns'),
    path('crm/analytics/', views.crm_analytics, name='crm_analytics'),
    path('', _safe(views.main_page), name='main_page'),
    path('customers/', _safe(views.manage_customers), name='manage_customers'),
    path('customers/<str:customer_id>/', _safe(views.customer_detail), name='customer_detail'),
    path('add-contact/', _safe(views.add_contact), name='add_contact'),
    path('edit-contact/<str:contact_id>/', _safe(views.edit_contact), name='edit_contact'),
    path('delete-contact/<str:contact_id>/', _safe(views.delete_contact), name='delete_contact'),
    path('bulk-delete-customers/', _safe(views.bulk_delete_customers), name='bulk_delete_customers'),
    path('upload-image/', _safe(views.upload_image), name='upload_image'),
    path('temp-image/<str:file_id>/', _safe(views.serve_temp_image), name='serve_temp_image'),
    path('send-bulk/', _safe(views.send_bulk_message), name='send_bulk_message'),
    path('import-excel/', _safe(views.import_excel), name='import_excel'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),

    # Settings
    path('settings/whatsapp/', _safe(views.whatsapp_settings), name='whatsapp_settings'),
    path('settings/pdpa/', _safe(views.pdpa_settings), name='pdpa_settings'),
    
    # WhatsApp webhook
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
    path('debug-webhook/', debug_webhook, name='debug_webhook'),
    
    # Incoming messages
    path('messages/incoming/', _safe(views.incoming_messages), name='incoming_messages'),
    
    # CRM API endpoints
    path('api/campaigns/', _safe(views.campaign_list), name='campaign_list'),
    path('api/campaigns/create/', _safe(views.create_campaign), name='create_campaign'),
    path('api/campaigns/<int:campaign_id>/', _safe(views.campaign_detail), name='campaign_detail'),
    path('api/segments/', _safe(views.segment_list), name='segment_list'),
    path('api/segments/create/', _safe(views.create_segment), name='create_segment'),
    path('api/segments/<int:segment_id>/', _safe(views.segment_detail), name='segment_detail'),
    path('api/customers/<int:customer_id>/purchases/', _safe(views.customer_purchases), name='customer_purchases'),
    path('api/ocr/process/', _safe(views.process_ocr), name='process_ocr'),
]
