#!/usr/bin/env python
"""
Test the deployed login functionality and capture errors
"""

import requests
import json

def test_deployed_login():
    """Test the deployed login functionality"""
    print("=== Testing Deployed Login ===")
    
    base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
    
    try:
        # Step 1: Get the login page to get CSRF token
        print("1. Getting login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Step 2: Extract CSRF token (simplified)
        csrf_token = "test"  # We'll use a test token
        
        # Step 3: Test POST to login
        print("2. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'Referer': f"{base_url}/login/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 500:
            print("   ❌ 500 error confirmed")
            print(f"   Response headers: {dict(response.headers)}")
            print(f"   Response content: {response.text[:1000]}")
            
            # Try to extract error details
            if "Traceback" in response.text:
                print("\n   === Python Traceback Found ===")
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if "Traceback" in line or "Exception" in line or "Error" in line:
                        print(f"   {line}")
                        # Show a few lines after the error
                        for j in range(1, 5):
                            if i + j < len(lines):
                                print(f"   {lines[i + j]}")
                        break
            
            return False
        elif response.status_code == 302:
            print("   ✓ Login successful - redirected")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_health():
    """Test basic app health"""
    print("\n=== Testing App Health ===")
    
    base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
    
    try:
        # Test root URL
        print("1. Testing root URL...")
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("   ✓ Root URL accessible")
        else:
            print(f"   ❌ Root URL failed: {response.status_code}")
            return False
        
        # Test static files
        print("2. Testing static files...")
        response = requests.get(f"{base_url}/static/admin/css/base.css", timeout=10)
        print(f"   Static files status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Static files accessible")
        else:
            print(f"   ⚠ Static files issue: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    print("🧪 TESTING DEPLOYED APP")
    print("=" * 50)
    
    # Test 1: App health
    if not test_app_health():
        print("\n❌ App health check failed")
        return False
    
    # Test 2: Login functionality
    if not test_deployed_login():
        print("\n❌ Login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Deployed app is working!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
