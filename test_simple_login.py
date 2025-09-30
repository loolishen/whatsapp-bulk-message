#!/usr/bin/env python
"""
Test the simplified login function
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

def test_simple_login():
    """Test the simplified login function"""
    print("=== Testing Simplified Login ===")
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test 1: Get login page
        print("1. Testing login page...")
        response = client.get('/login/', HTTP_HOST='testserver')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login page failed: {response.status_code}")
            return False
        
        print("   ✓ Login page accessible")
        
        # Test 2: Check for CSRF token
        print("2. Checking for CSRF token...")
        content = response.content.decode()
        if 'csrfmiddlewaretoken' in content:
            print("   ❌ CSRF token found - @csrf_exempt not working")
            print("   This means the decorator is not being applied correctly")
            return False
        else:
            print("   ✓ CSRF token removed - @csrf_exempt working")
        
        # Test 3: Test login POST
        print("3. Testing login POST...")
        response = client.post('/login/', {
            'username': 'tenant',
            'password': 'Tenant123!',
        }, HTTP_HOST='testserver')
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print("   ✓ Login successful - redirected!")
            print(f"   Redirect URL: {response.get('Location', 'N/A')}")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.content.decode()[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test simple login failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def deploy_simple_login():
    """Deploy the simplified login"""
    print("\n=== Deploying Simplified Login ===")
    
    try:
        import subprocess
        
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Simplify auth_login function'], capture_output=True, text=True)
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
        print(f"❌ Deploy simple login failed: {e}")
        return False

def main():
    print("🔧 TESTING AND DEPLOYING SIMPLIFIED LOGIN")
    print("=" * 50)
    
    # Step 1: Test locally
    if not test_simple_login():
        print("\n❌ Local test failed")
        print("The @csrf_exempt decorator is not working locally.")
        print("This suggests there might be a Django configuration issue.")
        return False
    
    # Step 2: Deploy
    if not deploy_simple_login():
        print("\n❌ Deploy failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Simplified login deployed!")
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
