#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

try:
    response = requests.get('http://127.0.0.1:8000/')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("=== DEBUGGING PREVIEW FUNCTIONALITY ===")
        
        # Check if required elements exist
        elements_to_check = [
            'waMessage',
            'waTime', 
            'waPreviewName',
            'receiverMessage',
            'receiverTime',
            'headerName',
            'headerAvatar',
            'receiverAvatar'
        ]
        
        missing_elements = []
        for elem_id in elements_to_check:
            element = soup.find(id=elem_id)
            if element:
                print(f"✅ Element #{elem_id} found: {element.name}")
            else:
                print(f"❌ Element #{elem_id} NOT FOUND")
                missing_elements.append(elem_id)
        
        # Check if JavaScript functions are present
        js_functions = ['updatePreview', 'updatePreviewName', 'loadLocalImage']
        for func in js_functions:
            if func in response.text:
                print(f"✅ Function {func}() found")
            else:
                print(f"❌ Function {func}() NOT FOUND")
        
        # Check if contacts JSON is properly formatted
        if 'const contacts =' in response.text:
            print("✅ Contacts array found")
            # Extract the contacts line
            lines = response.text.split('\n')
            for line in lines:
                if 'const contacts =' in line:
                    print(f"📋 Contacts line: {line.strip()}")
                    break
        else:
            print("❌ Contacts array NOT FOUND")
        
        print(f"\n=== SUMMARY ===")
        if missing_elements:
            print(f"❌ Missing {len(missing_elements)} required elements: {', '.join(missing_elements)}")
        else:
            print("✅ All required elements found")
            
        print(f"\nTo debug further:")
        print(f"1. Open http://127.0.0.1:8000/ in browser")
        print(f"2. Press F12 -> Console tab")
        print(f"3. Type: updatePreview()")
        print(f"4. Check for any JavaScript errors")
        
    else:
        print(f"❌ Page failed to load: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
