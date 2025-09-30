#!/usr/bin/env python
"""
Force a fresh deployment and test
"""

import subprocess
import time
import requests

def force_deploy():
    """Force a fresh deployment"""
    print("=== Force Fresh Deployment ===")
    
    try:
        # Create a small change to force deployment
        with open('deploy_timestamp.txt', 'w') as f:
            f.write(f"Deploy timestamp: {time.time()}")
        
        # Add and commit the change
        subprocess.run(['git', 'add', 'deploy_timestamp.txt'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Force deploy - {time.time()}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("✓ Changes pushed to GitHub")
        
        # Deploy to App Engine
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Force deploy failed: {e}")
        return False

def test_deployed_app():
    """Test the deployed app"""
    print("\n=== Testing Deployed App ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait a moment for deployment to propagate
        print("Waiting for deployment to propagate...")
        time.sleep(30)
        
        # Test login POST
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful - redirected")
            print(f"Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 500:
            print("❌ Still getting 500 error")
            print(f"Response: {response.text[:500]}")
            return False
        elif response.status_code == 403:
            print("❌ Getting 403 error - CSRF issue")
            print(f"Response: {response.text[:500]}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Deployed app test failed: {e}")
        return False

def check_app_status():
    """Check app status"""
    print("\n=== Checking App Status ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test root URL
        response = requests.get(base_url, timeout=10)
        print(f"Root URL status: {response.status_code}")
        
        # Test login page
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"Login page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ App is accessible")
            return True
        else:
            print("❌ App is not accessible")
            return False
            
    except Exception as e:
        print(f"❌ App status check failed: {e}")
        return False

def main():
    print("🚀 FORCE FRESH DEPLOYMENT")
    print("=" * 50)
    
    # Step 1: Check app status
    if not check_app_status():
        print("\n❌ App status check failed")
        return False
    
    # Step 2: Force deploy
    if not force_deploy():
        print("\n❌ Force deploy failed")
        return False
    
    # Step 3: Test deployed app
    if not test_deployed_app():
        print("\n❌ Deployed app test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Fresh deployment completed!")
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
