#!/usr/bin/env python
import requests
import re

try:
    response = requests.get('http://127.0.0.1:8000/')
    if response.status_code == 200:
        # Extract the JavaScript section
        script_match = re.search(r'<script>(.*?)</script>', response.text, re.DOTALL)
        if script_match:
            js_content = script_match.group(1)
            
            print("=== JAVASCRIPT SYNTAX CHECK ===")
            
            # Check for common JavaScript errors
            issues = []
            
            # Check for mismatched braces
            open_braces = js_content.count('{')
            close_braces = js_content.count('}')
            if open_braces != close_braces:
                issues.append(f"Mismatched braces: {open_braces} open, {close_braces} close")
            
            # Check for mismatched parentheses
            open_parens = js_content.count('(')
            close_parens = js_content.count(')')
            if open_parens != close_parens:
                issues.append(f"Mismatched parentheses: {open_parens} open, {close_parens} close")
            
            # Check for function definitions
            functions = re.findall(r'function\s+(\w+)', js_content)
            print(f"✅ Found functions: {', '.join(functions)}")
            
            # Check for variables
            variables = re.findall(r'(?:let|const|var)\s+(\w+)', js_content)
            print(f"✅ Found variables: {', '.join(variables)}")
            
            if issues:
                print("❌ JavaScript syntax issues found:")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("✅ No obvious JavaScript syntax errors found")
                
            # Check specific function calls in HTML
            html_calls = []
            if 'oninput="updatePreview()"' in response.text:
                html_calls.append('updatePreview')
            if 'onclick="toggleSelect(' in response.text:
                html_calls.append('toggleSelect')
            if 'onclick="selectAll()"' in response.text:
                html_calls.append('selectAll')
            if 'onclick="sendBulkMessage()"' in response.text:
                html_calls.append('sendBulkMessage')
                
            print(f"✅ HTML calls functions: {', '.join(html_calls)}")
            
            print(f"\n=== RECOMMENDED ACTIONS ===")
            print(f"1. Hard refresh the page (Ctrl+F5)")
            print(f"2. Open browser console and check for errors")
            print(f"3. Try typing in the message field")
            print(f"4. If errors persist, try: window.updatePreview() in console")
            
        else:
            print("❌ No JavaScript section found in HTML")
    else:
        print(f"❌ Page failed to load: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
