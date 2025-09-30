#!/usr/bin/env python
"""
Check what's actually deployed and test the dashboard
"""

import requests
import time

def check_deployed_dashboard():
    """Check the deployed dashboard"""
    print("=== Checking Deployed Dashboard ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test 1: Get login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Check for CSRF token
        print("2. Checking for CSRF token...")
        if 'csrfmiddlewaretoken' in response.text:
            print("   ❌ CSRF token still present - old code deployed")
            return False
        else:
            print("   ✓ CSRF token removed - new code deployed")
        
        # Test 3: Test login POST
        print("3. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected!")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            
            # Test 4: Test dashboard access
            print("4. Testing dashboard access...")
            dashboard_response = requests.get(f"{base_url}/", cookies=response.cookies, timeout=10)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✓ Dashboard accessible")
                return True
            elif dashboard_response.status_code == 500:
                print("   ❌ Dashboard 500 error")
                print(f"   Response: {dashboard_response.text[:500]}")
                return False
            else:
                print(f"   ❌ Unexpected dashboard status: {dashboard_response.status_code}")
                return False
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Check deployed dashboard failed: {e}")
        return False

def force_fresh_deployment():
    """Force a fresh deployment"""
    print("\n=== Force Fresh Deployment ===")
    
    try:
        import subprocess
        import time
        
        # Create a unique timestamp file
        timestamp = str(int(time.time() * 1000))
        with open('force_deploy_timestamp.txt', 'w') as f:
            f.write(f"Force deploy timestamp: {timestamp}")
        
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', f'Force fresh deployment - {timestamp}'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Push changes
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes pushed to GitHub")
        
        # Deploy to App Engine with version
        print("Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--version', timestamp, '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Force fresh deployment failed: {e}")
        return False

def test_after_deployment():
    """Test after deployment"""
    print("\n=== Testing After Deployment ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment to propagate
        print("Waiting for deployment to propagate...")
        time.sleep(45)
        
        # Test login and dashboard
        print("Testing login and dashboard...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        # Login
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=15)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful")
            
            # Test dashboard
            dashboard_response = requests.get(f"{base_url}/", cookies=response.cookies, timeout=15)
            print(f"Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✓ Dashboard accessible")
                return True
            else:
                print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                print(f"Response: {dashboard_response.text[:500]}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test after deployment failed: {e}")
        return False

def main():
    print("🔍 CHECKING AND FIXING DEPLOYED DASHBOARD")
    print("=" * 50)
    
    # Step 1: Check deployed dashboard
    if not check_deployed_dashboard():
        print("\n❌ Deployed dashboard check failed")
        print("The deployed app is still using old code or has issues.")
        
        # Step 2: Force fresh deployment
        if not force_fresh_deployment():
            print("\n❌ Force fresh deployment failed")
            return False
        
        # Step 3: Test after deployment
        if not test_after_deployment():
            print("\n❌ Test after deployment failed")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Dashboard is working!")
    print("=" * 50)
    print("Your login and dashboard should now work at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
