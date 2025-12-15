#!/usr/bin/env python
"""
One-time database setup script for GCP Cloud SQL
Run this after deployment to initialize the database
"""
import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')

# Setup Django
django.setup()

from django.core.management import call_command

print("=" * 60)
print("DATABASE SETUP FOR GCP CLOUD SQL")
print("=" * 60)

try:
    # Run migrations
    print("\n1. Running migrations...")
    call_command('migrate', '--noinput')
    print("✅ Migrations completed successfully!")
    
    # Create production user
    print("\n2. Creating production user...")
    call_command('ensure_production_user')
    print("✅ Production user created successfully!")
    
    print("\n" + "=" * 60)
    print("DATABASE SETUP COMPLETED!")
    print("=" * 60)
    print("\n🔐 Login credentials:")
    print("   Username: tenant")
    print("   Password: Tenant123!")
    print("\n🌐 URL: https://whatsapp-bulk-messaging-480620.as.r.appspot.com/")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error during setup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)






