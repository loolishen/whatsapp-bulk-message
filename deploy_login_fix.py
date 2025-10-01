#!/usr/bin/env python
"""
Deploy the fixed login function
"""

import subprocess
import requests
import time
import sys

def check_git_status():
    """Check git status and show what needs to be committed"""
    print("=== Checking Git Status ===")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                print("Changes to commit:")
                print(changes)
                return True
            else:
                print("No changes to commit")
                return False
        else:
            print(f"❌ Git status failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Check git status failed: {e}")
        return False

def deploy_fixed_login():
    """Deploy the fixed login function"""
    print("🔧 DEPLOYING FIXED LOGIN FUNCTION")
    print("=" * 50)
    
    try:
        # Check git status first
        if not check_git_status():
            print("No changes to commit, proceeding with deployment...")
        else:
            # Add changes
            print("Adding changes to git...")
            result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Git add failed: {result.stderr}")
                return False
            
            # Commit changes
            print("Committing changes...")
            result = subprocess.run(['git', 'commit', '-m', 'Fix login function - minimal error handling'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Git commit failed: {result.stderr}")
                print("Trying to commit with --allow-empty...")
                result = subprocess.run(['git', 'commit', '--allow-empty', '-m', 'Fix login function - minimal error handling'], capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Git commit with --allow-empty also failed: {result.stderr}")
                    return False
            
            # Push changes
            print("Pushing changes to GitHub...")
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
        print(f"❌ Deploy fixed login failed: {e}")
        return False

def test_fixed_login():
    """Test the fixed login function"""
    print("\n=== Testing Fixed Login Function ===")
    
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
        print(f"❌ Test fixed login failed: {e}")
        return False

def main():
    print("🔧 FIXING LOGIN FUNCTION")
    print("=" * 50)
    
    # Step 1: Deploy fixed login
    if not deploy_fixed_login():
        print("❌ Deploy fixed login failed")
        return False
    
    # Step 2: Test fixed login
    if not test_fixed_login():
        print("❌ Test fixed login failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Login function fixed!")
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
