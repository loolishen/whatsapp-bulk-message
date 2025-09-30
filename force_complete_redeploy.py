#!/usr/bin/env python
"""
Force a complete redeploy to ensure the latest code is used
"""

import subprocess
import time
import requests
import os

def force_complete_redeploy():
    """Force a complete redeploy"""
    print("=== Force Complete Redeploy ===")
    
    try:
        # Step 1: Verify the local file has the fix
        print("1. Verifying local file has @csrf_exempt...")
        with open('messaging/views.py', 'r') as f:
            content = f.read()
        
        if '@csrf_exempt' not in content:
            print("❌ @csrf_exempt not found in local file")
            return False
        
        print("✓ @csrf_exempt found in local file")
        
        # Step 2: Create a unique timestamp file to force deployment
        print("2. Creating unique timestamp file...")
        timestamp = str(int(time.time() * 1000))
        with open('deploy_timestamp.txt', 'w') as f:
            f.write(f"Deploy timestamp: {timestamp}")
        
        # Step 3: Add all changes
        print("3. Adding all changes...")
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Step 4: Commit with unique message
        print("4. Committing changes...")
        commit_msg = f"Force redeploy with CSRF fix - {timestamp}"
        result = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Step 5: Push to GitHub
        print("5. Pushing to GitHub...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes pushed to GitHub")
        
        # Step 6: Deploy to App Engine with version
        print("6. Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--version', timestamp, '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Force complete redeploy failed: {e}")
        return False

def test_deployed_app():
    """Test the deployed app after redeploy"""
    print("\n=== Testing Deployed App ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment to propagate
        print("Waiting for deployment to propagate...")
        time.sleep(45)  # Wait longer for complete propagation
        
        # Test 1: Get login page
        print("1. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Check for CSRF token
        print("2. Checking for CSRF token...")
        if 'csrfmiddlewaretoken' in response.text:
            print("   ❌ CSRF token still present - @csrf_exempt not working")
            return False
        else:
            print("   ✓ CSRF token removed - @csrf_exempt working")
        
        # Test 3: Test login POST
        print("3. Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=15)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected!")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 200:
            print("   ❌ Still getting 200 - checking response...")
            
            # Check for specific error messages
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
            return False
            
    except Exception as e:
        print(f"❌ Test deployed app failed: {e}")
        return False

def main():
    print("🚀 FORCE COMPLETE REDEPLOY")
    print("=" * 50)
    
    # Step 1: Force complete redeploy
    if not force_complete_redeploy():
        print("\n❌ Force complete redeploy failed")
        return False
    
    # Step 2: Test deployed app
    if not test_deployed_app():
        print("\n❌ Deployed app test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Complete redeploy successful!")
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
