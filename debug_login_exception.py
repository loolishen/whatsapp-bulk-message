#!/usr/bin/env python
"""
Debug the login exception to see what's actually causing the error
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def debug_login_step_by_step():
    """Debug login step by step to find the exact error"""
    print("=== Debugging Login Step by Step ===")
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        from messaging.models import Tenant, TenantUser
        
        client = Client()
        User = get_user_model()
        
        print("1. Testing user authentication...")
        user = User.objects.filter(username='tenant').first()
        if user:
            print(f"   ✓ User found: {user.username}")
            print(f"   ✓ User is active: {user.is_active}")
        else:
            print("   ❌ User not found")
            return False
        
        print("\n2. Testing password verification...")
        if user.check_password('Tenant123!'):
            print("   ✓ Password is correct")
        else:
            print("   ❌ Password is incorrect")
            return False
        
        print("\n3. Testing tenant relationship...")
        try:
            tenant_profile = user.tenant_profile
            print(f"   ✓ Tenant profile found: {tenant_profile.tenant.name}")
        except Exception as e:
            print(f"   ❌ Tenant profile error: {e}")
            return False
        
        print("\n4. Testing Django authenticate...")
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='tenant', password='Tenant123!')
        if auth_user:
            print(f"   ✓ Django authenticate successful: {auth_user.username}")
        else:
            print("   ❌ Django authenticate failed")
            return False
        
        print("\n5. Testing login process...")
        try:
            from django.contrib.auth import login
            from django.test import RequestFactory
            from django.contrib.sessions.middleware import SessionMiddleware
            from django.contrib.auth.middleware import AuthenticationMiddleware
            
            factory = RequestFactory()
            request = factory.post('/login/', {
                'username': 'tenant',
                'password': 'Tenant123!',
            })
            request.META['HTTP_HOST'] = 'testserver'
            
            # Add session middleware
            middleware = SessionMiddleware(lambda req: None)
            middleware.process_request(request)
            request.session.save()
            
            # Add auth middleware
            auth_middleware = AuthenticationMiddleware(lambda req: None)
            auth_middleware.process_request(request)
            
            # Test login
            login(request, auth_user)
            print("   ✓ Login process successful")
            
        except Exception as e:
            print(f"   ❌ Login process error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n6. Testing complete login flow...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Complete login flow successful")
            return True
        else:
            print(f"   ❌ Complete login flow failed: {response.status_code}")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Debug login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_with_detailed_logging():
    """Test login with detailed logging to see the exact error"""
    print("\n=== Testing Login with Detailed Logging ===")
    
    try:
        from django.test import Client
        import logging
        
        # Set up detailed logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger('django')
        
        client = Client()
        
        print("Testing login POST with detailed logging...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"Status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
        
        # Check if there are any messages
        from django.contrib import messages
        if hasattr(response, 'context') and response.context:
            messages_list = response.context.get('messages', [])
            for message in messages_list:
                print(f"Message: {message}")
        
        return response.status_code == 302
        
    except Exception as e:
        print(f"❌ Detailed logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_login_view_code():
    """Check the actual login view code to see what might be wrong"""
    print("\n=== Checking Login View Code ===")
    
    try:
        with open('messaging/views.py', 'r') as f:
            content = f.read()
        
        # Find the auth_login function
        lines = content.split('\n')
        in_auth_login = False
        auth_login_lines = []
        
        for i, line in enumerate(lines):
            if 'def auth_login(request):' in line:
                in_auth_login = True
                auth_login_lines.append(f"{i+1}: {line}")
            elif in_auth_login and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                break
            elif in_auth_login:
                auth_login_lines.append(f"{i+1}: {line}")
        
        print("Current auth_login function:")
        for line in auth_login_lines:
            print(line)
        
        return True
        
    except Exception as e:
        print(f"❌ Check login view code failed: {e}")
        return False

def main():
    print("🔍 DEBUGGING LOGIN EXCEPTION")
    print("=" * 50)
    
    # Step 1: Check login view code
    if not check_login_view_code():
        print("\n❌ Check login view code failed")
        return False
    
    # Step 2: Debug login step by step
    if not debug_login_step_by_step():
        print("\n❌ Debug login step by step failed")
        return False
    
    # Step 3: Test with detailed logging
    if not test_login_with_detailed_logging():
        print("\n❌ Detailed logging test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Login debugging complete!")
    print("=" * 50)
    print("Check the output above for the specific error details.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
