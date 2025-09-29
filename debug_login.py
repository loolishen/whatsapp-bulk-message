#!/usr/bin/env python
"""
Debug script to identify the exact login error
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from messaging.models import Tenant, TenantUser
from django.db import connection
from django.core.management import execute_from_command_line

def check_database_connection():
    """Check if database is accessible"""
    print("=== Database Connection Test ===")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ Database connection successful: {result}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_tables():
    """Check if required tables exist"""
    print("\n=== Database Tables Check ===")
    try:
        with connection.cursor() as cursor:
            # Check auth_user table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
            auth_user = cursor.fetchone()
            print(f"✓ auth_user table exists: {auth_user is not None}")
            
            # Check messaging_tenant table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messaging_tenant'")
            tenant_table = cursor.fetchone()
            print(f"✓ messaging_tenant table exists: {tenant_table is not None}")
            
            # Check messaging_tenantuser table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messaging_tenantuser'")
            tenantuser_table = cursor.fetchone()
            print(f"✓ messaging_tenantuser table exists: {tenantuser_table is not None}")
            
            return auth_user and tenant_table and tenantuser_table
    except Exception as e:
        print(f"✗ Table check failed: {e}")
        return False

def check_users():
    """Check if users exist"""
    print("\n=== Users Check ===")
    try:
        User = get_user_model()
        users = User.objects.all()
        print(f"✓ Total users in database: {users.count()}")
        
        for user in users:
            print(f"  - User: {user.username} (active: {user.is_active})")
            
        # Check specific user
        tenant_user = User.objects.filter(username='tenant').first()
        if tenant_user:
            print(f"✓ 'tenant' user found: {tenant_user.username}")
            print(f"✓ User is active: {tenant_user.is_active}")
            print(f"✓ User email: {tenant_user.email}")
        else:
            print("✗ 'tenant' user not found")
            
        return users.count() > 0
    except Exception as e:
        print(f"✗ Users check failed: {e}")
        return False

def check_tenants():
    """Check if tenants exist"""
    print("\n=== Tenants Check ===")
    try:
        tenants = Tenant.objects.all()
        print(f"✓ Total tenants in database: {tenants.count()}")
        
        for tenant in tenants:
            print(f"  - Tenant: {tenant.name} (plan: {tenant.plan})")
            
        return tenants.count() > 0
    except Exception as e:
        print(f"✗ Tenants check failed: {e}")
        return False

def check_tenant_users():
    """Check tenant-user relationships"""
    print("\n=== Tenant-User Relationships Check ===")
    try:
        tenant_users = TenantUser.objects.all()
        print(f"✓ Total tenant-user relationships: {tenant_users.count()}")
        
        for tu in tenant_users:
            print(f"  - {tu.user.username} @ {tu.tenant.name} (role: {tu.role})")
            
        return tenant_users.count() > 0
    except Exception as e:
        print(f"✗ Tenant-user relationships check failed: {e}")
        return False

def test_authentication():
    """Test authentication process"""
    print("\n=== Authentication Test ===")
    try:
        # Test with correct credentials
        user = authenticate(username='tenant', password='Tenant123!')
        if user:
            print(f"✓ Authentication successful: {user.username}")
            return True
        else:
            print("✗ Authentication failed with correct credentials")
            
            # Test with wrong password
            user_wrong = authenticate(username='tenant', password='wrong')
            if user_wrong:
                print("✓ Authentication works with wrong password (unexpected)")
            else:
                print("✓ Authentication correctly rejects wrong password")
            
            return False
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        return False

def run_migrations():
    """Run migrations to ensure database is up to date"""
    print("\n=== Running Migrations ===")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--settings=whatsapp_bulk.settings_production'])
        print("✓ Migrations completed")
        return True
    except Exception as e:
        print(f"✗ Migrations failed: {e}")
        return False

def create_user_if_missing():
    """Create user if missing"""
    print("\n=== Creating User if Missing ===")
    try:
        User = get_user_model()
        
        # Create or get tenant
        tenant, created_tenant = Tenant.objects.get_or_create(
            name='Demo Tenant',
            defaults={
                'plan': 'pro',
                'creation_date': django.utils.timezone.now(),
            }
        )
        print(f"✓ Tenant: {tenant.name} (created: {created_tenant})")
        
        # Create or get user
        user, created_user = User.objects.get_or_create(
            username='tenant',
            defaults={'email': 'tenant@example.com'}
        )
        
        if created_user:
            user.set_password('Tenant123!')
            user.save()
            print(f"✓ Created user: {user.username}")
        else:
            user.set_password('Tenant123!')
            user.save()
            print(f"✓ Updated user: {user.username}")
        
        # Create or get TenantUser link
        tenant_user, created_link = TenantUser.objects.get_or_create(
            user=user,
            tenant=tenant,
            defaults={'role': 'owner'}
        )
        print(f"✓ TenantUser link: {user.username} @ {tenant.name} (created: {created_link})")
        
        return True
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        return False

def main():
    print("🔍 DEBUGGING LOGIN ISSUE")
    print("=" * 50)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n❌ Database connection failed - cannot proceed")
        return False
    
    # Step 2: Check tables
    if not check_tables():
        print("\n❌ Required tables missing - running migrations")
        if not run_migrations():
            print("❌ Migrations failed")
            return False
    
    # Step 3: Check users
    if not check_users():
        print("\n❌ No users found - creating user")
        if not create_user_if_missing():
            print("❌ User creation failed")
            return False
    
    # Step 4: Check tenants
    if not check_tenants():
        print("\n❌ No tenants found - creating tenant")
        if not create_user_if_missing():
            print("❌ Tenant creation failed")
            return False
    
    # Step 5: Check tenant-user relationships
    if not check_tenant_users():
        print("\n❌ No tenant-user relationships found - creating relationships")
        if not create_user_if_missing():
            print("❌ Relationship creation failed")
            return False
    
    # Step 6: Test authentication
    if not test_authentication():
        print("\n❌ Authentication test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All checks passed - login should work now!")
    print("=" * 50)
    print("Try logging in with:")
    print("  Username: tenant")
    print("  Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
