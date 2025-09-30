#!/usr/bin/env python
"""
Test basic Django app functionality on App Engine
"""

import requests
import time

def test_basic_app():
    """Test basic Django app functionality"""
    print("=== Testing Basic Django App ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test 1: Root URL
        print("1. Testing root URL...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Root URL accessible")
        elif response.status_code == 302:
            print("   ✓ Root URL redirects (expected for login required)")
        else:
            print(f"   ❌ Root URL failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
        
        # Test 2: Login page
        print("2. Testing login page...")
        response = requests.get(f"{base_url}/login/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✓ Login page accessible")
        else:
            print(f"   ❌ Login page failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
        
        # Test 3: Check if Django is working
        print("3. Checking Django functionality...")
        if 'Django' in response.text or 'login' in response.text.lower():
            print("   ✓ Django is working")
        else:
            print("   ❌ Django might not be working properly")
            print(f"   Response content: {response.text[:200]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test basic app failed: {e}")
        return False

def create_simple_login_test():
    """Create a simple login test endpoint"""
    print("\n=== Creating Simple Login Test ===")
    
    try:
        # Create a simple test view
        test_view_content = '''
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_login(request):
    """Simple test login endpoint"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if username == 'tenant' and password == 'Tenant123!':
            return JsonResponse({'status': 'success', 'message': 'Login successful'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
    
    return JsonResponse({'status': 'info', 'message': 'Send POST with username and password'})
'''
        
        # Write to a test file
        with open('test_login_view.py', 'w') as f:
            f.write(test_view_content)
        
        print("✓ Test login view created")
        return True
        
    except Exception as e:
        print(f"❌ Create simple login test failed: {e}")
        return False

def test_simple_login():
    """Test the simple login endpoint"""
    print("\n=== Testing Simple Login ===")
    
    try:
        base_url = "https://whatsapp-bulk-messaging-473607.as.r.appspot.com"
        
        # Test simple login endpoint
        print("Testing simple login endpoint...")
        login_data = {
            'username': 'tenant',
            'password': 'Tenant123!',
        }
        
        response = requests.post(f"{base_url}/test-login/", data=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Simple login endpoint working")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ Simple login endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test simple login failed: {e}")
        return False

def check_app_engine_logs_detailed():
    """Check App Engine logs for detailed errors"""
    print("\n=== Checking App Engine Logs (Detailed) ===")
    
    try:
        import subprocess
        
        # Get detailed logs
        result = subprocess.run(['gcloud', 'app', 'logs', 'read', '--service=default', '--limit=50'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Recent logs:")
            print(result.stdout)
        else:
            print(f"❌ Failed to get logs: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Check App Engine logs detailed failed: {e}")
        return False

def main():
    print("🔍 TESTING BASIC DJANGO APP FUNCTIONALITY")
    print("=" * 50)
    
    # Step 1: Test basic app
    if not test_basic_app():
        print("\n❌ Test basic app failed")
        return False
    
    # Step 2: Check detailed logs
    if not check_app_engine_logs_detailed():
        print("\n❌ Check detailed logs failed")
        return False
    
    # Step 3: Create simple login test
    if not create_simple_login_test():
        print("\n❌ Create simple login test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🔍 Basic app testing complete!")
    print("=" * 50)
    print("The issue might be:")
    print("1. Django configuration problem")
    print("2. App Engine deployment issue")
    print("3. Missing dependencies or imports")
    print("4. Database connection issue")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    main()
