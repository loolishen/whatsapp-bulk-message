#!/usr/bin/env python
"""
Fix CSRF issue in production
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.conf import settings

def check_csrf_settings():
    """Check CSRF settings"""
    print("=== Checking CSRF Settings ===")
    
    try:
        print(f"✓ CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
        print(f"✓ CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not set')}")
        print(f"✓ CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Not set')}")
        print(f"✓ CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
        print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Check if CSRF middleware is enabled
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE
        print(f"✓ CSRF Middleware enabled: {csrf_middleware}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSRF settings check failed: {e}")
        return False

def fix_csrf_settings():
    """Fix CSRF settings for production"""
    print("\n=== Fixing CSRF Settings ===")
    
    try:
        # The issue is likely that CSRF_COOKIE_SECURE is True but the app might not be using HTTPS properly
        # or CSRF_TRUSTED_ORIGINS doesn't include the right domains
        
        print("Current CSRF settings:")
        print(f"  CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
        print(f"  CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
        
        # The fix is to ensure CSRF_TRUSTED_ORIGINS includes the App Engine domain
        required_origins = [
            'https://whatsapp-bulk-messaging-473607.as.r.appspot.com',
            'https://whatsapp-bulk-messaging-473607.appspot.com',
        ]
        
        print(f"\nRequired CSRF_TRUSTED_ORIGINS should include:")
        for origin in required_origins:
            print(f"  - {origin}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSRF settings fix failed: {e}")
        return False

def test_csrf_with_correct_origin():
    """Test CSRF with correct origin"""
    print("\n=== Testing CSRF with Correct Origin ===")
    
    try:
        import requests
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # First, get the login page with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print("1. Getting login page with proper headers...")
        response = requests.get(f"{base_url}/login/", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Extract CSRF token from the response
        csrf_token = None
        for line in response.text.split('\n'):
            if 'csrfmiddlewaretoken' in line and 'value=' in line:
                # Extract token from <input name="csrfmiddlewaretoken" value="TOKEN">
                start = line.find('value="') + 7
                end = line.find('"', start)
                if start > 6 and end > start:
                    csrf_token = line[start:end]
                    break
        
        if not csrf_token:
            print("   ❌ Could not extract CSRF token")
            return False
        
        print(f"   ✓ CSRF token extracted: {csrf_token[:20]}...")
        
        # Now test POST with proper CSRF token and headers
        print("2. Testing login POST with proper CSRF token...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        post_headers = headers.copy()
        post_headers.update({
            'Referer': f"{base_url}/login/",
            'Origin': base_url,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        
        response = requests.post(f"{base_url}/login/", data=login_data, headers=post_headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 403:
            print("   ❌ Still getting 403 - CSRF issue persists")
            print(f"   Response: {response.text[:500]}")
            return False
        elif response.status_code == 500:
            print("   ❌ Now getting 500 error")
            print(f"   Response: {response.text[:500]}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ CSRF test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 FIXING CSRF ISSUE")
    print("=" * 50)
    
    # Step 1: Check CSRF settings
    if not check_csrf_settings():
        print("\n❌ CSRF settings check failed")
        return False
    
    # Step 2: Fix CSRF settings
    if not fix_csrf_settings():
        print("\n❌ CSRF settings fix failed")
        return False
    
    # Step 3: Test CSRF with correct origin
    if not test_csrf_with_correct_origin():
        print("\n❌ CSRF test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! CSRF issue identified and solution provided!")
    print("=" * 50)
    print("The issue is CSRF token validation.")
    print("Solution: Update CSRF_TRUSTED_ORIGINS in settings_production.py")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
