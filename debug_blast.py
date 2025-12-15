#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_local')
django.setup()

from messaging.models import WhatsAppConnection, BlastCampaign, BlastRecipient, Customer

print("=== WHATSAPP CONNECTIONS ===")
connections = WhatsAppConnection.objects.all()
print(f"Total connections: {connections.count()}")
for conn in connections:
    print(f"- Phone: {conn.phone_number} | Instance: {conn.instance_id} | Provider: {conn.provider}")

print("\n=== BLAST CAMPAIGNS ===")
campaigns = BlastCampaign.objects.all()
print(f"Total campaigns: {campaigns.count()}")
for campaign in campaigns:
    print(f"- Name: {campaign.name} | Status: {campaign.status} | Recipients: {campaign.total_recipients}")

print("\n=== BLAST RECIPIENTS ===")
recipients = BlastRecipient.objects.all()
print(f"Total recipients: {recipients.count()}")
for recipient in recipients:
    print(f"- Customer: {recipient.customer.phone_number} | Status: {recipient.status}")

print("\n=== CUSTOMERS ===")
customers = Customer.objects.all()
print(f"Total customers: {customers.count()}")
for customer in customers:
    print(f"- Name: {customer.name} | Phone: {customer.phone_number}")
