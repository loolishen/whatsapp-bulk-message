#!/usr/bin/env python
"""
App Engine startup script to ensure production user exists
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings_production')
django.setup()

from django.core.management import call_command

def ensure_production_user():
    """Ensure production user exists"""
    try:
        print("Ensuring production user exists...")
        call_command('ensure_production_user')
        print("Production user setup completed!")
        return True
    except Exception as e:
        print(f"Failed to ensure production user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    ensure_production_user()
