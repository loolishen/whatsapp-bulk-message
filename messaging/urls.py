from django.urls import path
from . import views
from .whatsapp_webhook import whatsapp_webhook

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('customers/', views.manage_customers, name='manage_customers'),
    path('add-contact/', views.add_contact, name='add_contact'),
    path('edit-contact/<int:contact_id>/', views.edit_contact, name='edit_contact'),
    path('delete-contact/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('temp-image/<str:file_id>/', views.serve_temp_image, name='serve_temp_image'),
    path('send-bulk/', views.send_bulk_message, name='send_bulk_message'),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('crm/', views.crm_dashboard, name='crm_dashboard'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # WhatsApp webhook
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
    
    # CRM API endpoints
    path('api/campaigns/', views.campaign_list, name='campaign_list'),
    path('api/campaigns/create/', views.create_campaign, name='create_campaign'),
    path('api/campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('api/segments/', views.segment_list, name='segment_list'),
    path('api/segments/create/', views.create_segment, name='create_segment'),
    path('api/segments/<int:segment_id>/', views.segment_detail, name='segment_detail'),
    path('api/customers/<int:customer_id>/purchases/', views.customer_purchases, name='customer_purchases'),
    path('api/ocr/process/', views.process_ocr, name='process_ocr'),
]
