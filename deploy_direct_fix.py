#!/usr/bin/env python
"""
Deploy the URL fix directly without git
"""

import subprocess
import requests
import time
import sys

def deploy_direct():
    """Deploy directly to App Engine"""
    print("🚀 DEPLOYING URL FIX DIRECTLY TO APP ENGINE")
    print("=" * 50)
    
    try:
        # Deploy to App Engine directly
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            print("Deployment output:")
            print(result.stdout)
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            print("Deployment output:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Deploy direct failed: {e}")
        return False

def test_direct_fix():
    """Test the direct fix"""
    print("\n=== Testing Direct Fix ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment
        print("Waiting for deployment to propagate...")
        time.sleep(30)
        
        # Test login POST
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"✓ Login successful - redirecting to: {redirect_url}")
            
            # Follow the redirect
            print("Following redirect...")
            dashboard_response = requests.get(f"{base_url}{redirect_url}", timeout=10)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✓ Dashboard accessible after login!")
                print("✓ SUCCESS! Login and dashboard are working!")
                return True
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Test direct fix failed: {e}")
        return False

def main():
    print("🚀 DIRECT DEPLOYMENT OF URL FIX")
    print("=" * 50)
    
    # Deploy directly
    if not deploy_direct():
        print("❌ Deploy direct failed")
        return False
    
    # Test direct fix
    if not test_direct_fix():
        print("❌ Test direct fix failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login and dashboard are now working!")
    print("=" * 50)
    print("Your app is fully functional at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
