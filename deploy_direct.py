#!/usr/bin/env python
"""
Deploy directly to App Engine without git
"""

import subprocess
import requests
import time
import sys

def deploy_direct():
    """Deploy directly to App Engine"""
    print("🚀 DEPLOYING DIRECTLY TO APP ENGINE")
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

def test_deployed_login():
    """Test the deployed login function"""
    print("\n=== Testing Deployed Login Function ===")
    
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
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login POST successful - fixed!")
            print("Redirect URL:", response.headers.get('Location', 'Unknown'))
            return True
        elif response.status_code == 200:
            print("❌ Login returned 200 instead of 302")
            print("Response preview:", response.text[:200])
            return False
        else:
            print(f"❌ Login POST still failing: {response.status_code}")
            print("Response preview:", response.text[:200])
            return False
            
    except Exception as e:
        print(f"❌ Test deployed login failed: {e}")
        return False

def main():
    print("🚀 DIRECT DEPLOYMENT TO APP ENGINE")
    print("=" * 50)
    
    # Step 1: Deploy directly
    if not deploy_direct():
        print("❌ Deploy direct failed")
        return False
    
    # Step 2: Test deployed login
    if not test_deployed_login():
        print("❌ Test deployed login failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login function deployed and working!")
    print("=" * 50)
    print("Your login should now work at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
