#!/usr/bin/env python
"""
Test the deployed login directly to see what's happening
"""

import requests

def test_deployed_login():
    """Test the deployed login directly"""
    print("=== Testing Deployed Login Directly ===")
    
    base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
    
    try:
        # Test 1: Get login page
        print("1. Getting login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Check if CSRF token is in the form
        print("2. Checking for CSRF token...")
        if 'csrfmiddlewaretoken' in response.text:
            print("   ✓ CSRF token found in form")
        else:
            print("   ❌ CSRF token NOT found in form")
        
        # Test 3: Try login with proper headers
        print("3. Testing login with proper headers...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': f"{base_url}/login/",
        }
        
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 200:
            print("   ❌ Login returned 200 - checking response...")
            
            # Check if there are error messages
            if 'Invalid credentials' in response.text:
                print("   ❌ Invalid credentials error")
            elif 'Username and password are required' in response.text:
                print("   ❌ Username/password required error")
            elif 'An error occurred during login' in response.text:
                print("   ❌ General login error")
            else:
                print("   ❌ Unknown error - showing response snippet:")
                print(f"   {response.text[:500]}")
            
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test deployed login failed: {e}")
        return False

def main():
    print("🔍 TESTING DEPLOYED LOGIN DIRECTLY")
    print("=" * 50)
    
    if test_deployed_login():
        print("\n🎉 SUCCESS! Login is working!")
    else:
        print("\n❌ Login is still not working")
        print("The issue might be:")
        print("1. CSRF protection is still active")
        print("2. The @csrf_exempt decorator wasn't deployed")
        print("3. There's a different error in the login view")
    
    return True

if __name__ == '__main__':
    main()
