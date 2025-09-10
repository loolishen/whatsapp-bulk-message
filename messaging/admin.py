from django.contrib import admin
from .models import Contact, Message, BulkMessage

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'created_at']
    search_fields = ['name', 'phone_number']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['text_content', 'created_at']
    list_filter = ['created_at']

@admin.register(BulkMessage)
class BulkMessageAdmin(admin.ModelAdmin):
    list_display = ['message', 'sent_at']
    list_filter = ['sent_at']
