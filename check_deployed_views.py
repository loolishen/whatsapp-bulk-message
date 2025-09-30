#!/usr/bin/env python
"""
Check what's actually deployed in the views.py file
"""

import requests
import re

def check_deployed_views():
    """Check what's actually deployed by examining the response"""
    print("=== Checking Deployed Views ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Get the login page
        print("1. Getting login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Login page failed: {response.status_code}")
            return False
        
        print("✓ Login page accessible")
        
        # Check for CSRF token in the form
        print("2. Checking for CSRF token...")
        if 'csrfmiddlewaretoken' in response.text:
            print("❌ CSRF token found - @csrf_exempt NOT working")
            csrf_active = True
        else:
            print("✓ CSRF token NOT found - @csrf_exempt working")
            csrf_active = False
        
        # Try to extract any error information from the response
        print("3. Analyzing response...")
        
        # Check if there are any Django error messages
        if 'Invalid credentials' in response.text:
            print("❌ Invalid credentials error found")
        elif 'Username and password are required' in response.text:
            print("❌ Username/password required error found")
        elif 'An error occurred during login' in response.text:
            print("❌ General login error found")
        else:
            print("✓ No error messages found in response")
        
        # Check the form action
        form_action_match = re.search(r'<form[^>]*action="([^"]*)"', response.text)
        if form_action_match:
            form_action = form_action_match.group(1)
            print(f"Form action: {form_action}")
        
        # Check if there are any JavaScript errors or console messages
        if 'console.error' in response.text or 'console.log' in response.text:
            print("❌ JavaScript errors found in response")
        
        return not csrf_active
        
    except Exception as e:
        print(f"❌ Check deployed views failed: {e}")
        return False

def check_local_views():
    """Check what's in the local views.py file"""
    print("\n=== Checking Local Views ===")
    
    try:
        with open('messaging/views.py', 'r') as f:
            content = f.read()
        
        # Check for @csrf_exempt
        if '@csrf_exempt' in content:
            print("✓ @csrf_exempt found in local file")
        else:
            print("❌ @csrf_exempt NOT found in local file")
        
        # Check for the import
        if 'from django.views.decorators.csrf import csrf_exempt' in content:
            print("✓ csrf_exempt import found in local file")
        else:
            print("❌ csrf_exempt import NOT found in local file")
        
        # Check for the auth_login function
        if 'def auth_login(request):' in content:
            print("✓ auth_login function found in local file")
        else:
            print("❌ auth_login function NOT found in local file")
        
        # Show the auth_login function
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
        
        print("\nLocal auth_login function:")
        for line in auth_login_lines[:10]:  # Show first 10 lines
            print(line)
        
        return True
        
    except Exception as e:
        print(f"❌ Check local views failed: {e}")
        return False

def main():
    print("🔍 CHECKING DEPLOYED VS LOCAL VIEWS")
    print("=" * 50)
    
    # Check local views
    if not check_local_views():
        print("\n❌ Check local views failed")
        return False
    
    # Check deployed views
    if not check_deployed_views():
        print("\n❌ Check deployed views failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Analysis complete!")
    print("=" * 50)
    print("The issue is that the @csrf_exempt decorator is in the local file")
    print("but it's not being deployed to App Engine.")
    print("This suggests there might be a deployment issue or the wrong file is being used.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    main()
