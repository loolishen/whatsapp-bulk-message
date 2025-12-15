#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_local')
django.setup()

from messaging.models import CustomerGroup, Tenant, TenantUser
from django.contrib.auth.models import User

print("=== DEBUGGING TENANT/GROUP RELATIONSHIP ===")

# Get admin user and their tenant
user = User.objects.get(username='admin')
tenant_user = TenantUser.objects.get(user=user)
print(f"Admin user tenant: {tenant_user.tenant.name} (ID: {tenant_user.tenant.tenant_id})")

# Check groups for this tenant
groups = CustomerGroup.objects.filter(tenant=tenant_user.tenant)
print(f"Groups for this tenant: {groups.count()}")
for group in groups:
    print(f"  - {group.name} (ID: {group.group_id}) - Members: {group.member_count}")

# Check all groups in database
all_groups = CustomerGroup.objects.all()
print(f"\nAll groups in database: {all_groups.count()}")
for group in all_groups:
    print(f"  - {group.name} (Tenant: {group.tenant.name}) - Members: {group.member_count}")

# Check if there are any groups with different tenants
print(f"\n=== TENANT ANALYSIS ===")
tenants = Tenant.objects.all()
for tenant in tenants:
    tenant_groups = CustomerGroup.objects.filter(tenant=tenant)
    print(f"Tenant '{tenant.name}': {tenant_groups.count()} groups")
