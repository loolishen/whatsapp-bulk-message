#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

print("Testing basic Django setup...")

from messaging.models import Contest, Customer, Tenant
from django.utils import timezone

# Get tenant
tenant = Tenant.objects.first()
print(f"Tenant: {tenant.name if tenant else 'None'}")

# Get contests
contests = Contest.objects.filter(tenant=tenant)
print(f"Contests: {contests.count()}")

# Get active contests
now = timezone.now()
active_contests = contests.filter(
    is_active=True,
    starts_at__lte=now,
    ends_at__gte=now
)
print(f"Active contests: {active_contests.count()}")

for contest in active_contests:
    print(f"  - {contest.name}")
    print(f"    Custom PDPA: {bool(contest.post_pdpa_text)}")
    print(f"    Custom Instructions: {bool(contest.contest_instructions)}")

print("Test completed!")