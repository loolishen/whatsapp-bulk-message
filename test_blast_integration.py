"""
Quick test script to verify WhatsApp Blasting integration
Run with: python test_blast_integration.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_bulk.settings')
django.setup()

from messaging.models import Tenant, Customer, WhatsAppConnection, CustomerGroup, BlastCampaign
from messaging.whatsapp_service import WhatsAppAPIService

def test_whatsapp_service():
    """Test WABot service connection"""
    print("Testing WABot service...")
    try:
        wa_service = WhatsAppAPIService()
        print(f"[OK] WABot service initialized")
        print(f"   - Base URL: {wa_service.base_url}")
        print(f"   - Instance ID: {wa_service.instance_id}")
        print(f"   - Access Token: {wa_service.access_token[:10]}...")
        return True
    except Exception as e:
        print(f"[FAIL] Error initializing WABot service: {e}")
        return False

def test_models():
    """Test that models are available"""
    print("\nTesting models...")
    try:
        tenant_count = Tenant.objects.count()
        customer_count = Customer.objects.count()
        group_count = CustomerGroup.objects.count()
        campaign_count = BlastCampaign.objects.count()
        
        print(f"[OK] Models loaded successfully")
        print(f"   - Tenants: {tenant_count}")
        print(f"   - Customers: {customer_count}")
        print(f"   - Groups: {group_count}")
        print(f"   - Campaigns: {campaign_count}")
        return True
    except Exception as e:
        print(f"[FAIL] Error accessing models: {e}")
        return False

def test_blast_views():
    """Test that blast views are importable"""
    print("\nTesting blast views...")
    try:
        from messaging import blast_views
        from messaging import blast_tasks
        
        functions = [
            'blast_groups_list',
            'blast_create_campaign',
            'blast_send_campaign',
            'blast_campaign_progress'
        ]
        
        for func_name in functions:
            if hasattr(blast_views, func_name):
                print(f"   [OK] {func_name}")
            else:
                print(f"   [FAIL] {func_name} not found")
                return False
        
        print(f"[OK] All blast views are available")
        return True
    except Exception as e:
        print(f"[FAIL] Error importing blast views: {e}")
        return False

def test_urls():
    """Test that blast URLs are registered"""
    print("\nTesting URL configuration...")
    try:
        from django.urls import reverse
        
        urls = [
            ('blast_groups_list', []),
            ('blast_campaigns_list', []),
            ('blast_create_campaign', []),
        ]
        
        for url_name, args in urls:
            try:
                url = reverse(url_name, args=args)
                print(f"   [OK] {url_name}: {url}")
            except Exception as e:
                print(f"   [FAIL] {url_name}: {e}")
                return False
        
        print(f"[OK] All URLs configured correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Error testing URLs: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("="*60)
    print("WhatsApp Blasting Integration Test")
    print("="*60)
    
    results = []
    results.append(("WABot Service", test_whatsapp_service()))
    results.append(("Database Models", test_models()))
    results.append(("Blast Views", test_blast_views()))
    results.append(("URL Configuration", test_urls()))
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("SUCCESS! All tests passed! Integration is ready to use.")
        print("\nNext steps:")
        print("1. Go to http://localhost:8000/blast/groups/")
        print("2. Create a customer group")
        print("3. Create a blast campaign")
        print("4. Send your first blast!")
    else:
        print("WARNING: Some tests failed. Please check the errors above.")
    print("="*60)

if __name__ == "__main__":
    run_tests()

