#!/bin/bash
# =============================================================================
# TEST WEBHOOK ENDPOINT AND CHECK CONFIGURATION
# =============================================================================

cd ~/app-full && python3 << 'PYTHON_SCRIPT'
import os, sys, django, requests
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
django.setup()

from messaging.models import Tenant, WhatsAppConnection

GREEN, RED, YELLOW, BLUE, NC = '\033[0;32m', '\033[0;31m', '\033[1;33m', '\033[0;34m', '\033[0m'
def ps(msg): print(f"{GREEN}✅ {msg}{NC}")
def pe(msg): print(f"{RED}❌ {msg}{NC}")
def pi(msg): print(f"{YELLOW}ℹ️  {msg}{NC}")
def pstep(msg): print(f"\n{BLUE}📋 {msg}{NC}\n" + "-" * 40)

APP_URL = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
WEBHOOK_URL = f"{APP_URL}/webhook/whatsapp/"

pstep("CHECKING WEBHOOK CONFIGURATION")

# Check tenant
tenant = Tenant.objects.first()
if not tenant:
    pe("No tenant found")
    sys.exit(1)
pi(f"Tenant: {tenant.name}")

# Check WhatsApp connections
whatsapp_conns = WhatsAppConnection.objects.filter(tenant=tenant)
pi(f"\nWhatsApp Connections: {whatsapp_conns.count()}")
for conn in whatsapp_conns:
    print(f"  - Phone: {conn.phone_number}")
    print(f"    Provider: {conn.provider}")
    print(f"    Instance ID: {conn.instance_id}")

pstep("TESTING WEBHOOK ENDPOINT")

# Test webhook with a sample message
test_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "from": "+60123456789",
                    "type": "text",
                    "text": {"body": "TEST"},
                    "id": "test_msg_123",
                    "timestamp": "1234567890"
                }],
                "contacts": [{
                    "profile": {"name": "Test User"},
                    "wa_id": "+60123456789"
                }]
            }
        }]
    }]
}

try:
    pi(f"Sending test message to: {WEBHOOK_URL}")
    response = requests.post(WEBHOOK_URL, json=test_payload, timeout=10)
    if response.status_code in [200, 201]:
        ps(f"Webhook responded: HTTP {response.status_code}")
        pi("Webhook endpoint is accessible and working!")
    else:
        pe(f"Webhook returned: HTTP {response.status_code}")
        pi(f"Response: {response.text[:200]}")
except Exception as e:
    pe(f"Webhook test failed: {e}")

pstep("WEBHOOK URL FOR WABOT CONFIGURATION")
print(f"\nYour webhook URL should be set to:")
print(f"  {WEBHOOK_URL}")
print(f"\nIn your WABot dashboard, make sure:")
print(f"  1. Webhook URL is set to: {WEBHOOK_URL}")
print(f"  2. Webhook is enabled/active")
print(f"  3. Message events are enabled")
print(f"  4. Your phone number is connected")

pstep("CHECKING RECENT WEBHOOK LOGS")
print("\nRun this command to see recent webhook activity:")
print(f"  gcloud app logs read --limit=200 --project=whatsapp-bulk-messaging-480620 | grep -i 'webhook\\|POST.*whatsapp'")
print("\nIf you see no POST requests to /webhook/whatsapp/, the webhook is not receiving messages.")
print("This means the issue is in WABot configuration, not your code.")

PYTHON_SCRIPT

