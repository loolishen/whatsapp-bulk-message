#!/usr/bin/env python
import requests
import json

try:
    response = requests.get('http://localhost:4040/api/tunnels')
    data = response.json()
    
    if 'tunnels' in data and len(data['tunnels']) > 0:
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                public_url = tunnel['public_url']
                webhook_url = f"{public_url}/webhook/whatsapp/"
                print(f"🌐 Your ngrok URL: {public_url}")
                print(f"🔗 Webhook URL: {webhook_url}")
                print(f"\n📋 Use this webhook URL in WABOT dashboard:")
                print(f"   {webhook_url}")
                break
    else:
        print("❌ No ngrok tunnels found. Make sure ngrok is running.")
        
except Exception as e:
    print(f"❌ Error getting ngrok URL: {e}")
    print("💡 Make sure ngrok is running: ngrok http 8000")

