#!/usr/bin/env python
"""
Deploy the login and dashboard fixes
"""

import subprocess
import time
import requests

def deploy_fixes():
    """Deploy the fixes to App Engine"""
    print("=== Deploying Fixes ===")
    
    try:
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Fix login and dashboard errors'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Push changes
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes pushed to GitHub")
        
        # Deploy to App Engine
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Deploy fixes failed: {e}")
        return False

def test_deployed_app():
    """Test the deployed app after deployment"""
    print("\n=== Testing Deployed App ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment to propagate
        print("Waiting for deployment to propagate...")
        time.sleep(30)
        
        # Test login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test login POST
        print("2. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            
            # Test dashboard access
            print("3. Testing dashboard access...")
            dashboard_response = requests.get(f"{base_url}/", cookies=response.cookies, timeout=10)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✓ Dashboard accessible")
                return True
            else:
                print(f"   ❌ Dashboard failed: {dashboard_response.status_code}")
                return False
        elif response.status_code == 500:
            print("   ❌ Still getting 500 error")
            print(f"   Response: {response.text[:500]}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Deployed app test failed: {e}")
        return False

def main():
    print("🚀 DEPLOYING LOGIN AND DASHBOARD FIXES")
    print("=" * 50)
    
    # Step 1: Deploy fixes
    if not deploy_fixes():
        print("\n❌ Deploy fixes failed")
        return False
    
    # Step 2: Test deployed app
    if not test_deployed_app():
        print("\n❌ Deployed app test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! All fixes deployed and working!")
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
