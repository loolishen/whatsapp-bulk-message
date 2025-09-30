#!/usr/bin/env python
"""
Final deployment script to fix the login issue
"""

import subprocess
import os
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_git_status():
    """Check git status"""
    print("=== Checking Git Status ===")
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Git status:")
            print(result.stdout)
            return True
        else:
            print(f"Git status failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Git status error: {e}")
        return False

def commit_and_push():
    """Commit and push changes"""
    print("\n=== Committing and Pushing Changes ===")
    
    # Add all changes
    if not run_command("git add .", "Adding changes"):
        return False
    
    # Commit changes
    if not run_command('git commit -m "Fix login CSRF issue"', "Committing changes"):
        return False
    
    # Push to origin
    if not run_command("git push origin main", "Pushing to GitHub"):
        return False
    
    return True

def deploy_to_app_engine():
    """Deploy to App Engine"""
    print("\n=== Deploying to App Engine ===")
    
    if not run_command("gcloud app deploy --quiet", "Deploying to App Engine"):
        return False
    
    return True

def test_deployment():
    """Test the deployment"""
    print("\n=== Testing Deployment ===")
    
    try:
        import requests
        
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
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
            return True
        elif response.status_code == 500:
            print("   ❌ 500 error - checking response")
            print(f"   Response: {response.text[:500]}")
            return False
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")
        return False

def main():
    print("🚀 FINAL DEPLOYMENT FIX")
    print("=" * 50)
    
    # Step 1: Check git status
    if not check_git_status():
        print("\n❌ Git status check failed")
        return False
    
    # Step 2: Commit and push
    if not commit_and_push():
        print("\n❌ Commit and push failed")
        return False
    
    # Step 3: Deploy to App Engine
    if not deploy_to_app_engine():
        print("\n❌ App Engine deployment failed")
        return False
    
    # Step 4: Test deployment
    if not test_deployment():
        print("\n❌ Deployment test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login issue fixed!")
    print("=" * 50)
    print("You can now log in to your app at:")
    print("https://whatsapp-bulk-messaging-473607.as.r.appspot.com/login/")
    print("Username: tenant")
    print("Password: Tenant123!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
