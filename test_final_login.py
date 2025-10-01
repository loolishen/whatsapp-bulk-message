#!/usr/bin/env python
"""
Test final login after deployment
"""

import requests
import time

def test_production_login():
    """Test production login"""
    print("TESTING FINAL PRODUCTION LOGIN")
    print("=" * 50)
    
    base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
    
    try:
        # Test 1: Get login page
        print("1. Testing login page access...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   GET /login/ Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   [ERROR] Login page not accessible")
            return False
        
        print("   [OK] Login page accessible")
        
        # Test 2: Try login with correct credentials
        print("\n2. Testing login with credentials...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   POST /login/ Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   [OK] Login successful - redirecting to: {redirect_url}")
            
            # Test 3: Follow redirect to dashboard
            print("\n3. Testing dashboard access...")
            dashboard_response = requests.get(f"{base_url}{redirect_url}", timeout=10)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   [OK] Dashboard accessible after login!")
                print("\n" + "=" * 50)
                print("SUCCESS! Login is working perfectly!")
                print("=" * 50)
                return True
            else:
                print(f"   [ERROR] Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"   [ERROR] Login failed: {response.status_code}")
            
            # Check response content for error messages
            content = response.text
            if 'error' in content.lower():
                print("   Response contains error message")
                # Try to extract error message
                import re
                error_match = re.search(r'<div class="error-msg">(.*?)</div>', content)
                if error_match:
                    print(f"   Error message: {error_match.group(1)}")
            
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def main():
    print("FINAL LOGIN TEST")
    print("=" * 50)
    
    if test_production_login():
        print("\n🎉 SUCCESS! Your login is working!")
        print("You can now access your app at:")
        print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
        print("Username: tenant")
        print("Password: Tenant123!")
        return True
    else:
        print("\n❌ FAILED! Login is still not working.")
        print("The startup fix may need more time to take effect.")
        print("Try waiting a few minutes and running this test again.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
