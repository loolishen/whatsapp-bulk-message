#!/usr/bin/env python
"""
Check deployment issues and fix them
"""

import subprocess
import requests
import time

def check_requirements_file():
    """Check if requirements.txt exists and has all dependencies"""
    print("=== Checking Requirements File ===")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        print("Current requirements.txt:")
        print(content)
        
        # Check for essential Django packages
        essential_packages = [
            'Django',
            'django-cors-headers',
            'Pillow',
            'pandas',
            'requests',
            'cloudinary',
            'gunicorn'
        ]
        
        missing_packages = []
        for package in essential_packages:
            if package.lower() not in content.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {missing_packages}")
            return False
        else:
            print("✓ All essential packages present")
            return True
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False
    except Exception as e:
        print(f"❌ Check requirements file failed: {e}")
        return False

def create_proper_requirements():
    """Create a proper requirements.txt file"""
    print("\n=== Creating Proper Requirements File ===")
    
    try:
        requirements = """Django>=4.2.0
django-cors-headers>=4.0.0
Pillow>=9.0.0
pandas>=1.5.0
requests>=2.28.0
cloudinary>=1.30.0
gunicorn>=20.1.0
psycopg2-binary>=2.9.0
"""
        
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        
        print("✓ Proper requirements.txt created")
        return True
        
    except Exception as e:
        print(f"❌ Create proper requirements failed: {e}")
        return False

def check_app_yaml():
    """Check app.yaml configuration"""
    print("\n=== Checking app.yaml Configuration ===")
    
    try:
        with open('app.yaml', 'r') as f:
            content = f.read()
        
        print("Current app.yaml:")
        print(content)
        
        # Check for essential configurations
        if 'runtime: python311' in content:
            print("✓ Python 3.11 runtime specified")
        else:
            print("❌ Python runtime not specified")
            return False
        
        if 'DJANGO_SETTINGS_MODULE' in content:
            print("✓ Django settings module specified")
        else:
            print("❌ Django settings module not specified")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Check app.yaml failed: {e}")
        return False

def create_proper_app_yaml():
    """Create a proper app.yaml file"""
    print("\n=== Creating Proper app.yaml ===")
    
    try:
        app_yaml = """runtime: python311
env: standard

# Basic handlers
handlers:
- url: /static
  static_dir: staticfiles/
- url: /.*
  script: auto

# Environment variables
env_variables:
  DJANGO_SETTINGS_MODULE: "whatsapp_bulk.settings_production"
  SECRET_KEY: "your-secret-key-here-change-this-in-production"
  DEBUG: "False"
  ALLOWED_HOSTS: "*.appspot.com,whatsapp-bulk-messaging-473607.as.r.appspot.com"
  WHATSAPP_API_ACCESS_TOKEN: "68a0a10422130"
  WHATSAPP_API_BASE_URL: "https://app.wabot.my/api"
  WHATSAPP_API_INSTANCE_ID: "68A0A11A89A8D"
  CLOUDINARY_CLOUD_NAME: "dzbje38xw"
  CLOUDINARY_API_KEY: "645993869662484"
  CLOUDINARY_API_SECRET: "43OPTPwCt8cWEim-L9GHtwmj7_w"

# Automatic scaling
automatic_scaling:
  min_instances: 1
  max_instances: 10
"""
        
        with open('app.yaml', 'w') as f:
            f.write(app_yaml)
        
        print("✓ Proper app.yaml created")
        return True
        
    except Exception as e:
        print(f"❌ Create proper app.yaml failed: {e}")
        return False

def check_main_py():
    """Check main.py configuration"""
    print("\n=== Checking main.py Configuration ===")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
        
        print("Current main.py:")
        print(content)
        
        if 'get_wsgi_application' in content:
            print("✓ WSGI application configured")
        else:
            print("❌ WSGI application not configured")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Check main.py failed: {e}")
        return False

def deploy_fixed_configuration():
    """Deploy the fixed configuration"""
    print("\n=== Deploying Fixed Configuration ===")
    
    try:
        # Add changes
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False
        
        # Commit changes
        result = subprocess.run(['git', 'commit', '-m', 'Fix deployment configuration'], capture_output=True, text=True)
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
        print(f"❌ Deploy fixed configuration failed: {e}")
        return False

def test_fixed_deployment():
    """Test the fixed deployment"""
    print("\n=== Testing Fixed Deployment ===")
    
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
            return True
        else:
            print(f"❌ Login POST still failing: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test fixed deployment failed: {e}")
        return False

def main():
    print("🔧 CHECKING AND FIXING DEPLOYMENT ISSUES")
    print("=" * 50)
    
    # Step 1: Check requirements file
    if not check_requirements_file():
        print("\n❌ Check requirements file failed")
        if not create_proper_requirements():
            print("\n❌ Create proper requirements failed")
            return False
    
    # Step 2: Check app.yaml
    if not check_app_yaml():
        print("\n❌ Check app.yaml failed")
        if not create_proper_app_yaml():
            print("\n❌ Create proper app.yaml failed")
            return False
    
    # Step 3: Check main.py
    if not check_main_py():
        print("\n❌ Check main.py failed")
        return False
    
    # Step 4: Deploy fixed configuration
    if not deploy_fixed_configuration():
        print("\n❌ Deploy fixed configuration failed")
        return False
    
    # Step 5: Test fixed deployment
    if not test_fixed_deployment():
        print("\n❌ Test fixed deployment failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Deployment issues fixed!")
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
