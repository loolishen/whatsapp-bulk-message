#!/usr/bin/env python3
"""
Comprehensive Python Test Script for Contest Flow
Tests: Contest Creation -> WhatsApp Webhook -> Auto Reply -> OCR -> Data Saving
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# Configuration
PROJECT_ID = "whatsapp-bulk-messaging-480620"
APP_URL = "https://whatsapp-bulk-messaging-480620.as.r.appspot.com"
WEBHOOK_URL = f"{APP_URL}/webhook/whatsapp/"
TEST_PHONE = "60123456789"  # Change this to your test phone number
TEST_KEYWORD = "JOIN"  # Change this to your contest keyword

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{NC}")

def test_app_accessibility():
    """Test 1: Check if app is accessible"""
    print("\n" + "="*50)
    print("Test 1: App Accessibility")
    print("="*50)
    
    try:
        response = requests.get(APP_URL, timeout=10, allow_redirects=True)
        if response.status_code in [200, 302]:
            print_success(f"App is accessible (HTTP {response.status_code})")
            return True
        else:
            print_error(f"App returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        return False

def send_webhook_message(message_body, message_type="text", image_id=None):
    """Send a webhook message"""
    timestamp = str(int(time.time()))
    message_id = f"wamid.test_{timestamp}_{int(time.time() * 1000) % 10000}"
    
    if message_type == "text":
        message = {
            "from": TEST_PHONE,
            "id": message_id,
            "timestamp": timestamp,
            "text": {"body": message_body},
            "type": "text"
        }
    elif message_type == "image":
        message = {
            "from": TEST_PHONE,
            "id": message_id,
            "timestamp": timestamp,
            "image": {
                "id": image_id or f"img_{timestamp}",
                "mime_type": "image/jpeg",
                "sha256": "test_hash_sha256",
                "caption": "Test Receipt"
            },
            "type": "image"
        }
    
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [message],
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": TEST_PHONE
                    }]
                }
            }]
        }]
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)

def test_initial_keyword():
    """Test 2: Send initial keyword to trigger contest"""
    print("\n" + "="*50)
    print(f"Test 2: Initial Keyword Message ({TEST_KEYWORD})")
    print("="*50)
    
    success, response = send_webhook_message(TEST_KEYWORD)
    if success:
        print_success("Initial keyword message sent successfully")
        print_info(f"Response: {response[:200]}")
        return True
    else:
        print_error(f"Failed to send message: {response}")
        return False

def test_pdpa_response():
    """Test 3: Send PDPA agreement"""
    print("\n" + "="*50)
    print("Test 3: PDPA Agreement Response")
    print("="*50)
    
    time.sleep(2)  # Wait a bit for previous message to process
    success, response = send_webhook_message("YES")
    if success:
        print_success("PDPA agreement sent successfully")
        return True
    else:
        print_error(f"Failed to send PDPA response: {response}")
        return False

def test_nric_submission():
    """Test 4: Send NRIC number"""
    print("\n" + "="*50)
    print("Test 4: NRIC Submission")
    print("="*50)
    
    time.sleep(2)
    success, response = send_webhook_message("123456789012")
    if success:
        print_success("NRIC submission sent successfully")
        return True
    else:
        print_error(f"Failed to send NRIC: {response}")
        return False

def test_receipt_image():
    """Test 5: Send receipt image for OCR"""
    print("\n" + "="*50)
    print("Test 5: Receipt Image Upload (OCR)")
    print("="*50)
    
    time.sleep(2)
    image_id = f"test_receipt_{int(time.time())}"
    success, response = send_webhook_message("", message_type="image", image_id=image_id)
    if success:
        print_success("Receipt image sent successfully")
        print_info("OCR processing should happen automatically")
        print_info(f"Image ID: {image_id}")
        return True
    else:
        print_error(f"Failed to send receipt image: {response}")
        return False

def test_contest_manager():
    """Test 6: Check Contest Manager page"""
    print("\n" + "="*50)
    print("Test 6: Contest Manager Page")
    print("="*50)
    
    url = f"{APP_URL}/contest/manager/"
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == 200:
            print_success(f"Contest Manager accessible (HTTP 200)")
            return True
        elif response.status_code == 302:
            print_info(f"Contest Manager requires login (HTTP 302 - redirect)")
            return True  # This is expected if not logged in
        else:
            print_error(f"Contest Manager returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to check Contest Manager: {e}")
        return False

def test_participants_manager():
    """Test 7: Check Participants Manager page"""
    print("\n" + "="*50)
    print("Test 7: Participants Manager Page")
    print("="*50)
    
    url = f"{APP_URL}/participants/"
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == 200:
            print_success(f"Participants Manager accessible (HTTP 200)")
            return True
        elif response.status_code == 302:
            print_info(f"Participants Manager requires login (HTTP 302 - redirect)")
            return True  # This is expected if not logged in
        else:
            print_error(f"Participants Manager returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to check Participants Manager: {e}")
        return False

def verify_database_entry():
    """Test 8: Verify data was saved (requires database access)"""
    print("\n" + "="*50)
    print("Test 8: Database Verification")
    print("="*50)
    
    print_info("To verify database entries, run this in Cloud Shell with Cloud SQL Proxy:")
    print_info("""
    python3 << 'EOF'
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_production')
    django.setup()
    
    from messaging.models import ContestEntry, Contest, Customer
    
    # Find entries for test phone
    entries = ContestEntry.objects.filter(contestant_phone__contains='123456789')
    print(f"Found {entries.count()} entries")
    for entry in entries:
        print(f"\\nEntry ID: {entry.entry_id}")
        print(f"  Status: {entry.status}")
        print(f"  Verified: {entry.is_verified}")
        print(f"  Store: {entry.store_name or 'N/A'}")
        print(f"  Amount: {entry.receipt_amount or 'N/A'}")
        print(f"  Products: {entry.products_purchased or 'N/A'}")
    EOF
    """)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE CONTEST FLOW TEST")
    print("="*60)
    print(f"App URL: {APP_URL}")
    print(f"Test Phone: {TEST_PHONE}")
    print(f"Test Keyword: {TEST_KEYWORD}")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("App Accessibility", test_app_accessibility()))
    results.append(("Initial Keyword", test_initial_keyword()))
    results.append(("PDPA Response", test_pdpa_response()))
    results.append(("NRIC Submission", test_nric_submission()))
    results.append(("Receipt Image (OCR)", test_receipt_image()))
    results.append(("Contest Manager", test_contest_manager()))
    results.append(("Participants Manager", test_participants_manager()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{NC}" if result else f"{RED}FAIL{NC}"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("All tests passed!")
    else:
        print_error(f"{total - passed} test(s) failed")
    
    # Additional info
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print_info("1. Check WhatsApp for automated replies")
    print_info(f"2. View Contest Manager: {APP_URL}/contest/manager/")
    print_info(f"3. View Participants Manager: {APP_URL}/participants/")
    print_info("4. Check logs: gcloud app logs tail --project=" + PROJECT_ID)
    print_info("5. Verify database entries (see Test 8 output above)")
    print("")
    
    verify_database_entry()

if __name__ == "__main__":
    main()

