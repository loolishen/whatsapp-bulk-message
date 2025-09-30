#!/usr/bin/env python
"""
Fix just the login function in the existing views.py
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def fix_login_function():
    """Fix just the auth_login function"""
    print("=== Fixing Login Function ===")
    
    try:
        # Read the current views.py
        with open('messaging/views.py', 'r') as f:
            content = f.read()
        
        # Find the auth_login function and replace it
        lines = content.split('\n')
        new_lines = []
        in_auth_login = False
        auth_login_fixed = False
        
        for i, line in enumerate(lines):
            if 'def auth_login(request):' in line and not auth_login_fixed:
                # Replace the entire auth_login function
                new_lines.append('@csrf_exempt')
                new_lines.append('def auth_login(request):')
                new_lines.append('    """Robust login view with proper error handling"""')
                new_lines.append('    try:')
                new_lines.append('        if request.method == \'POST\':')
                new_lines.append('            username = request.POST.get(\'username\', \'\').strip()')
                new_lines.append('            password = request.POST.get(\'password\', \'\').strip()')
                new_lines.append('            ')
                new_lines.append('            if not username or not password:')
                new_lines.append('                messages.error(request, \'Username and password are required\')')
                new_lines.append('                return render(request, \'messaging/auth_login.html\')')
                new_lines.append('            ')
                new_lines.append('            # Authenticate user')
                new_lines.append('            user = authenticate(request, username=username, password=password)')
                new_lines.append('            if user is not None:')
                new_lines.append('                if user.is_active:')
                new_lines.append('                    login(request, user)')
                new_lines.append('                    return redirect(\'dashboard\')')
                new_lines.append('                else:')
                new_lines.append('                    messages.error(request, \'Account is disabled\')')
                new_lines.append('            else:')
                new_lines.append('                messages.error(request, \'Invalid credentials\')')
                new_lines.append('        else:')
                new_lines.append('            # Clear any existing messages for GET requests')
                new_lines.append('            pass')
                new_lines.append('            ')
                new_lines.append('        return render(request, \'messaging/auth_login.html\')')
                new_lines.append('        ')
                new_lines.append('    except Exception as e:')
                new_lines.append('        import logging')
                new_lines.append('        logger = logging.getLogger(__name__)')
                new_lines.append('        logger.error(f"Login error: {e}")')
                new_lines.append('        messages.error(request, \'An error occurred during login. Please try again.\')')
                new_lines.append('        return render(request, \'messaging/auth_login.html\')')
                new_lines.append('')
                auth_login_fixed = True
                in_auth_login = True
            elif in_auth_login and line.strip() and not line.startswith('    ') and not line.startswith('\t'):
                # End of auth_login function
                in_auth_login = False
                new_lines.append(line)
            elif not in_auth_login:
                new_lines.append(line)
        
        # Write the fixed content
        with open('messaging/views.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✓ Login function fixed with robust error handling")
        return True
        
    except Exception as e:
        print(f"❌ Fix login function failed: {e}")
        return False

def test_fixed_login():
    """Test the fixed login"""
    print("\n=== Testing Fixed Login ===")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test GET /login/
        print("1. Testing GET /login/...")
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test POST /login/
        print("2. Testing POST /login/...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Fixed login test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 FIXING LOGIN FUNCTION ONLY")
    print("=" * 50)
    
    # Step 1: Fix login function
    if not fix_login_function():
        print("\n❌ Fix login function failed")
        return False
    
    # Step 2: Test fixed login
    if not test_fixed_login():
        print("\n❌ Fixed login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login function fixed!")
    print("=" * 50)
    print("The login function now includes:")
    print("- @csrf_exempt decorator")
    print("- Input validation")
    print("- Proper error handling")
    print("- Graceful error messages")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
