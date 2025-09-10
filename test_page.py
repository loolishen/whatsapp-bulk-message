#!/usr/bin/env python
import requests
import json

# Test if the main page loads without errors
try:
    response = requests.get('http://127.0.0.1:8000/')
    print(f"Main page status code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Main page loads successfully")
        
        # Check if the page contains our JavaScript
        if 'const contacts =' in response.text:
            print("✅ JavaScript contacts array is present")
        else:
            print("❌ JavaScript contacts array not found")
            
        # Check if LI SHEN is in the HTML
        if 'LI SHEN' in response.text:
            print("✅ Contact 'LI SHEN' is present in HTML")
        else:
            print("❌ Contact 'LI SHEN' not found in HTML")
            
        # Look for any obvious JavaScript syntax errors
        if 'SyntaxError' in response.text or 'ReferenceError' in response.text:
            print("❌ JavaScript errors detected in HTML")
        else:
            print("✅ No obvious JavaScript errors in HTML")
            
    else:
        print(f"❌ Main page failed to load: {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Django server. Make sure it's running on http://127.0.0.1:8000/")
except Exception as e:
    print(f"❌ Error testing main page: {e}")

print("\nTo manually test:")
print("1. Open http://127.0.0.1:8000/ in your browser")
print("2. Open browser console (F12 -> Console tab)")
print("3. Look for any JavaScript errors")
print("4. Try typing a message and selecting contacts")
