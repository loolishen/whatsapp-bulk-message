#!/usr/bin/env python
"""
Local development server runner
This script sets up and runs the Django development server with local settings
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_local_environment():
    """Set up the local development environment"""
    print("Setting up local development environment...")
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_local')
    
    # Check if we're in the right directory
    if not Path('manage_local.py').exists():
        print("Error: manage_local.py not found. Make sure you're in the project root directory.")
        return False
    
    print("Local environment configured")
    return True

def run_migrations():
    """Run database migrations for local development"""
    print("Running database migrations...")
    try:
        subprocess.run([sys.executable, 'manage_local.py', 'migrate'], check=True)
        print("Migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        return False

def create_superuser_if_needed():
    """Create a superuser if none exists"""
    print("Setting up admin user...")
    try:
        # Try to create superuser and tenant setup
        subprocess.run([
            sys.executable, 'manage_local.py', 'shell', '-c',
            'import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatsapp_bulk.settings_local"); '
            'import django; django.setup(); '
            'from django.contrib.auth.models import User; '
            'from messaging.models import Tenant, TenantUser; '
            'user, created = User.objects.get_or_create(username="admin", defaults={"is_superuser": True, "is_staff": True, "email": "admin@example.com"}); '
            'user.set_password("admin123"); user.save(); '
            'tenant, created = Tenant.objects.get_or_create(name="Khind", defaults={"plan": "contest"}); '
            'TenantUser.objects.get_or_create(user=user, defaults={"tenant": tenant, "role": "owner"}); '
            'print("Setup complete")'
        ], check=True, capture_output=True)
        print("Admin user ready (admin/admin123)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Admin user setup failed: {e}")
        print("Continuing without admin user...")
        return True

def run_server():
    """Run the Django development server"""
    print("Starting Django development server...")
    print("   Server will be available at: http://127.0.0.1:8000")
    print("   Admin panel: http://127.0.0.1:8000/admin/")
    print("   Username: admin, Password: admin123")
    print("\n   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([sys.executable, 'manage_local.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Server failed to start: {e}")

def main():
    """Main function to set up and run local development"""
    print("WhatsApp Bulk Message - Local Development Setup")
    print("=" * 50)
    
    # Setup environment
    if not setup_local_environment():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    # Create superuser if needed
    if not create_superuser_if_needed():
        return
    
    # Run server
    run_server()

if __name__ == '__main__':
    main()
