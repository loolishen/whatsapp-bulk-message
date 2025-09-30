#!/usr/bin/env python
"""
Check what code is actually deployed
"""

import requests

def check_deployed_code():
    """Check what code is actually deployed"""
    print("=== Checking Deployed Code ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test the login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test login POST to see what error we get
        print("2. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - CSRF fix is deployed!")
            return True
        elif response.status_code == 403:
            print("   ❌ 403 Forbidden - CSRF fix NOT deployed")
            print("   The @csrf_exempt decorator is missing")
            return False
        elif response.status_code == 500:
            print("   ❌ 500 Internal Server Error")
            print("   There's a different issue - checking response...")
            print(f"   Response: {response.text[:1000]}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Check failed: {e}")
        return False

def main():
    print("🔍 CHECKING DEPLOYED CODE")
    print("=" * 50)
    
    if check_deployed_code():
        print("\n🎉 SUCCESS! The CSRF fix is deployed and working!")
    else:
        print("\n❌ The CSRF fix is NOT deployed yet.")
        print("You need to run the deployment commands in Cloud Shell:")
        print("1. git add .")
        print("2. git commit -m 'Fix login CSRF issue'")
        print("3. git push origin main")
        print("4. gcloud app deploy")
    
    return True

if __name__ == '__main__':
    main()
