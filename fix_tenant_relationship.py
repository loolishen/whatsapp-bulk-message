#!/usr/bin/env python
"""
Fix tenant relationship issues
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Tenant, TenantUser
from django.utils import timezone

def fix_tenant_relationship():
    """Fix any tenant relationship issues"""
    print("=== Fixing Tenant Relationship ===")
    
    try:
        User = get_user_model()
        
        # Get the user
        user = User.objects.filter(username='tenant').first()
        if not user:
            print("❌ User 'tenant' not found")
            return False
        
        print(f"✓ Found user: {user.username}")
        
        # Get the tenant
        tenant = Tenant.objects.filter(name='Demo Tenant').first()
        if not tenant:
            print("❌ Tenant 'Demo Tenant' not found")
            return False
        
        print(f"✓ Found tenant: {tenant.name}")
        
        # Check if TenantUser relationship exists
        tenant_user = TenantUser.objects.filter(user=user, tenant=tenant).first()
        if not tenant_user:
            print("❌ TenantUser relationship not found - creating it")
            tenant_user = TenantUser.objects.create(
                user=user,
                tenant=tenant,
                role='owner'
            )
            print(f"✓ Created TenantUser relationship: {user.username} @ {tenant.name}")
        else:
            print(f"✓ TenantUser relationship exists: {user.username} @ {tenant.name} (role: {tenant_user.role})")
        
        # Test the relationship
        try:
            tenant_profile = user.tenant_profile
            print(f"✓ User.tenant_profile works: {tenant_profile.tenant.name}")
            print(f"✓ Tenant plan: {tenant_profile.tenant.plan}")
            print(f"✓ User role: {tenant_profile.role}")
            return True
        except Exception as e:
            print(f"❌ User.tenant_profile failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Fix tenant relationship failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_flow():
    """Test the complete login flow"""
    print("\n=== Testing Complete Login Flow ===")
    
    try:
        from django.test import Client
        from django.contrib.auth import authenticate, login
        from django.contrib.auth.models import User
        
        client = Client()
        
        # Test 1: Get login page
        print("1. Testing GET /login/...")
        response = client.get('/login/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        # Test 2: Authenticate user
        print("2. Testing authentication...")
        user = authenticate(username='tenant', password='Tenant123!')
        if not user:
            print("   ❌ Authentication failed")
            return False
        print(f"   ✓ Authentication successful: {user.username}")
        
        # Test 3: Test tenant relationship
        print("3. Testing tenant relationship...")
        try:
            tenant_profile = user.tenant_profile
            print(f"   ✓ Tenant profile: {tenant_profile.tenant.name}")
            print(f"   ✓ Tenant plan: {tenant_profile.tenant.plan}")
        except Exception as e:
            print(f"   ❌ Tenant profile failed: {e}")
            return False
        
        # Test 4: Test dashboard access
        print("4. Testing dashboard access...")
        client.force_login(user)
        response = client.get('/')
        print(f"   Dashboard status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Dashboard accessible")
            return True
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 FIXING TENANT RELATIONSHIP")
    print("=" * 50)
    
    # Step 1: Fix tenant relationship
    if not fix_tenant_relationship():
        print("\n❌ Failed to fix tenant relationship")
        return False
    
    # Step 2: Test login flow
    if not test_login_flow():
        print("\n❌ Login flow test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Tenant relationship fixed!")
    print("=" * 50)
    print("Try logging in now with:")
    print("  Username: tenant")
    print("  Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
