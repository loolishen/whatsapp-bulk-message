#!/usr/bin/env python
"""
Debug the dashboard 500 error
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def debug_dashboard_500():
    """Debug the dashboard 500 error"""
    print("=== Debugging Dashboard 500 Error ===")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from messaging.models import Tenant, TenantUser
        
        client = Client()
        User = get_user_model()
        
        # Test 1: Check user and tenant relationship
        print("1. Checking user and tenant relationship...")
        user = User.objects.filter(username='tenant').first()
        if not user:
            print("   ❌ User 'tenant' not found")
            return False
        
        print(f"   ✓ User found: {user.username}")
        print(f"   ✓ User is authenticated: {user.is_authenticated}")
        
        # Check tenant_profile
        if hasattr(user, 'tenant_profile'):
            print(f"   ✓ User has tenant_profile: {user.tenant_profile}")
            tenant = user.tenant_profile.tenant
            print(f"   ✓ Tenant: {tenant.name} (plan: {tenant.plan})")
        else:
            print("   ❌ User has no tenant_profile")
            return False
        
        # Test 2: Test login and dashboard flow
        print("\n2. Testing login and dashboard flow...")
        
        # Login first
        login_response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Login status: {login_response.status_code}")
        if login_response.status_code != 302:
            print("   ❌ Login failed")
            return False
        
        print("   ✓ Login successful")
        
        # Test dashboard access
        print("3. Testing dashboard access...")
        dashboard_response = client.get('/', HTTP_HOST='testserver')
        print(f"   Dashboard status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("   ✓ Dashboard accessible")
            return True
        elif dashboard_response.status_code == 500:
            print("   ❌ Dashboard 500 error")
            
            # Try to get more details about the error
            print("   Checking response content...")
            content = dashboard_response.content.decode()
            if 'error' in content.lower():
                print(f"   Error content: {content[:500]}")
            
            return False
        else:
            print(f"   ❌ Unexpected dashboard status: {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug dashboard 500 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashboard_directly():
    """Test the dashboard view directly"""
    print("\n=== Testing Dashboard View Directly ===")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from messaging.views import dashboard, _get_tenant
        
        client = Client()
        User = get_user_model()
        
        # Login first
        login_response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        if login_response.status_code != 302:
            print("❌ Login failed")
            return False
        
        print("✓ Login successful")
        
        # Test _get_tenant function directly
        print("Testing _get_tenant function...")
        user = User.objects.get(username='tenant')
        
        # Create a mock request with the user
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        
        tenant = _get_tenant(request)
        if tenant:
            print(f"✓ _get_tenant successful: {tenant.name}")
        else:
            print("❌ _get_tenant failed")
            return False
        
        # Test dashboard view directly
        print("Testing dashboard view directly...")
        try:
            response = dashboard(request)
            print(f"✓ Dashboard view successful: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Dashboard view failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Test dashboard directly failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 DEBUGGING DASHBOARD 500 ERROR")
    print("=" * 50)
    
    # Step 1: Debug dashboard 500
    if not debug_dashboard_500():
        print("\n❌ Dashboard debug failed")
        return False
    
    # Step 2: Test dashboard directly
    if not test_dashboard_directly():
        print("\n❌ Direct dashboard test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Dashboard debugging complete!")
    print("=" * 50)
    print("Check the output above for the specific error details.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
