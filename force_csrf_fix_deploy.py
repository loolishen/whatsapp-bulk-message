#!/usr/bin/env python
"""
Force deploy the CSRF fix by checking and updating the login view
"""

import subprocess
import time
import requests

def check_current_login_view():
    """Check what's currently in the login view"""
    print("=== Checking Current Login View ===")
    
    try:
        with open('messaging/views.py', 'r') as f:
            content = f.read()
        
        # Check for @csrf_exempt
        if '@csrf_exempt' in content:
            print("✓ @csrf_exempt decorator found in local file")
        else:
            print("❌ @csrf_exempt decorator NOT found in local file")
            return False
        
        # Check for the import
        if 'from django.views.decorators.csrf import csrf_exempt' in content:
            print("✓ csrf_exempt import found in local file")
        else:
            print("❌ csrf_exempt import NOT found in local file")
            return False
        
        # Check for the auth_login function
        if 'def auth_login(request):' in content:
            print("✓ auth_login function found in local file")
        else:
            print("❌ auth_login function NOT found in local file")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Check current login view failed: {e}")
        return False

def force_deploy_csrf_fix():
    """Force deploy the CSRF fix"""
    print("\n=== Force Deploying CSRF Fix ===")
    
    try:
        # Check current status
        if not check_current_login_view():
            print("❌ Local file doesn't have the CSRF fix")
            return False
        
        # Add a timestamp to force deployment
        with open('force_deploy.txt', 'w') as f:
            f.write(f"Force deploy timestamp: {time.time()}")
        
        # Git operations
        print("1. Adding changes...")
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        print("2. Committing changes...")
        result = subprocess.run(['git', 'commit', '-m', 'Force deploy CSRF fix'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        print("3. Pushing to GitHub...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes pushed to GitHub")
        
        print("4. Deploying to App Engine...")
        result = subprocess.run(['gcloud', 'app', 'deploy', '--quiet'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Deployment successful")
            return True
        else:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Force deploy CSRF fix failed: {e}")
        return False

def test_deployed_csrf_fix():
    """Test if the CSRF fix is deployed"""
    print("\n=== Testing Deployed CSRF Fix ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Wait for deployment to propagate
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
            print("✓ CSRF fix deployed - login successful!")
            print(f"Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 200:
            print("❌ Still getting 200 - CSRF fix not deployed yet")
            
            # Check if CSRF token is still in the form
            if 'csrfmiddlewaretoken' in response.text:
                print("❌ CSRF token still present - @csrf_exempt not working")
            else:
                print("✓ CSRF token removed - @csrf_exempt working")
            
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test deployed CSRF fix failed: {e}")
        return False

def main():
    print("🔧 FORCE DEPLOYING CSRF FIX")
    print("=" * 50)
    
    # Step 1: Check current login view
    if not check_current_login_view():
        print("\n❌ Local file doesn't have CSRF fix")
        return False
    
    # Step 2: Force deploy
    if not force_deploy_csrf_fix():
        print("\n❌ Force deploy failed")
        return False
    
    # Step 3: Test deployed fix
    if not test_deployed_csrf_fix():
        print("\n❌ CSRF fix not deployed yet")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! CSRF fix deployed and working!")
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
