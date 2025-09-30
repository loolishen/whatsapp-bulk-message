#!/usr/bin/env python
"""
Fix deployment issue by ensuring the correct code is deployed
"""

import subprocess
import os
import sys

def check_deployed_files():
    """Check what files are actually deployed"""
    print("=== Checking Deployed Files ===")
    
    try:
        # Check if the @csrf_exempt decorator is in the deployed views.py
        with open('messaging/views.py', 'r') as f:
            content = f.read()
            
        if '@csrf_exempt' in content and 'def auth_login' in content:
            print("✓ @csrf_exempt decorator found in views.py")
            
            # Check if it's properly placed
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def auth_login' in line:
                    # Check if the line before has @csrf_exempt
                    if i > 0 and '@csrf_exempt' in lines[i-1]:
                        print("✓ @csrf_exempt is properly placed before auth_login")
                        return True
                    else:
                        print("❌ @csrf_exempt is not properly placed before auth_login")
                        return False
        else:
            print("❌ @csrf_exempt decorator not found in views.py")
            return False
            
    except Exception as e:
        print(f"❌ Error checking deployed files: {e}")
        return False

def check_imports():
    """Check if required imports are present"""
    print("\n=== Checking Imports ===")
    
    try:
        with open('messaging/views.py', 'r') as f:
            content = f.read()
            
        required_imports = [
            'from django.views.decorators.csrf import csrf_exempt',
            'from django.contrib.auth import authenticate, login, logout',
            'from django.contrib import messages'
        ]
        
        for import_line in required_imports:
            if import_line in content:
                print(f"✓ Found: {import_line}")
            else:
                print(f"❌ Missing: {import_line}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking imports: {e}")
        return False

def force_redeploy():
    """Force a complete redeploy"""
    print("\n=== Force Redeploy ===")
    
    try:
        # Add all changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Force redeploy with CSRF fix'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git commit failed: {result.stderr}")
            return False
        
        # Push changes
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
        
        print("✓ Changes committed and pushed")
        
        # Deploy with force
        result = subprocess.run(['gcloud', 'app', 'deploy', '--force'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Deployment failed: {result.stderr}")
            return False
        
        print("✓ Force deployment completed")
        return True
        
    except Exception as e:
        print(f"❌ Force redeploy failed: {e}")
        return False

def test_deployed_app():
    """Test the deployed app after redeploy"""
    print("\n=== Testing Deployed App ===")
    
    try:
        import requests
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test login POST
        print("Testing login POST...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 302:
            print("✓ Login successful - redirected")
            print(f"Redirect URL: {response.headers.get('Location', 'N/A')}")
            return True
        elif response.status_code == 500:
            print("❌ Still getting 500 error")
            print(f"Response: {response.text[:500]}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Deployed app test failed: {e}")
        return False

def main():
    print("🔧 FIXING DEPLOYMENT ISSUE")
    print("=" * 50)
    
    # Step 1: Check deployed files
    if not check_deployed_files():
        print("\n❌ Deployed files check failed")
        return False
    
    # Step 2: Check imports
    if not check_imports():
        print("\n❌ Imports check failed")
        return False
    
    # Step 3: Force redeploy
    if not force_redeploy():
        print("\n❌ Force redeploy failed")
        return False
    
    # Step 4: Test deployed app
    if not test_deployed_app():
        print("\n❌ Deployed app test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Deployment issue fixed!")
    print("=" * 50)
    print("Your login should now work at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
