import requests
import json
from django.conf import settings

class WhatsAppAPIService:
    """Service class to handle WhatsApp API communications"""
    
    def __init__(self):
        # Get configuration from Django settings
        whatsapp_config = getattr(settings, 'WHATSAPP_API', {})
        self.access_token = whatsapp_config.get('ACCESS_TOKEN', '68a0a10422130')
        # Use static instance ID - no dynamic creation
        self.instance_id = whatsapp_config.get('DEFAULT_INSTANCE_ID', '68A0A11A89A8D')
        self.base_url = whatsapp_config.get('BASE_URL', 'https://app.wabot.my/api')
    
    # DISABLED: Static instance ID configuration - no dynamic instance creation needed
    # def create_instance(self):
    #     """Create a new WhatsApp instance"""
    #     url = f"{self.base_url}/create_instance"
    #     params = {
    #         'access_token': self.access_token
    #     }
    #     
    #     try:
    #         response = requests.get(url, params=params)
    #         response.raise_for_status()
    #         data = response.json()
    #         
    #         if 'instance_id' in data:
    #             self.instance_id = data['instance_id']
    #             return {'success': True, 'instance_id': self.instance_id, 'data': data}
    #         else:
    #             return {'success': False, 'error': 'No instance_id in response', 'data': data}
    #             
    #     except requests.exceptions.RequestException as e:
    #         return {'success': False, 'error': str(e)}
    
    def set_webhook(self, webhook_url, enable=True):
        """Set webhook for receiving WhatsApp events"""
        url = f"{self.base_url}/set_webhook"
        params = {
            'webhook_url': webhook_url,
            'enable': str(enable).lower(),
            'instance_id': self.instance_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def send_text_message(self, number, message):
        """Send a text message to a phone number"""
        url = f"{self.base_url}/send"
        
        # Clean the phone number (remove + and any non-digits)
        clean_number = ''.join(filter(str.isdigit, number))
        
        payload = {
            "number": clean_number,
            "type": "text",
            "message": message,
            "instance_id": self.instance_id,
            "access_token": self.access_token
        }
        
        try:
            response = requests.post(
                url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def send_media_message(self, number, message, media_url, filename=None):
        """Send a media message to a phone number"""
        url = f"{self.base_url}/send"
        
        # Clean the phone number (remove + and any non-digits)
        clean_number = ''.join(filter(str.isdigit, number))
        
        payload = {
            "number": clean_number,
            "type": "media",
            "message": message,
            "media_url": media_url,
            "instance_id": self.instance_id,
            "access_token": self.access_token
        }
        
        if filename:
            payload["filename"] = filename
        
        try:
            response = requests.post(
                url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def set_instance_id(self, instance_id):
        """Manually set instance ID if you already have one"""
        self.instance_id = instance_id
    
    def get_media_url(self, media_id):
        """Get media URL from WhatsApp API"""
        url = f"{self.base_url}/get_media"
        params = {
            'media_id': media_id,
            'instance_id': self.instance_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'url' in data:
                return data['url']
            else:
                return None
                
        except requests.exceptions.RequestException as e:
            return None
    
    def download_media(self, media_url):
        """Download media content from URL"""
        try:
            response = requests.get(media_url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            return None
    
    def send_template_message(self, number, template_name, parameters=None):
        """Send template message to a phone number"""
        url = f"{self.base_url}/send"
        
        # Clean the phone number
        clean_number = ''.join(filter(str.isdigit, number))
        
        payload = {
            "number": clean_number,
            "type": "template",
            "template_name": template_name,
            "instance_id": self.instance_id,
            "access_token": self.access_token
        }
        
        if parameters:
            payload["parameters"] = parameters
        
        try:
            response = requests.post(
                url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def get_instance_status(self):
        """Get instance status and QR code"""
        url = f"{self.base_url}/status"
        params = {
            'instance_id': self.instance_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def restart_instance(self):
        """Restart WhatsApp instance"""
        url = f"{self.base_url}/restart"
        params = {
            'instance_id': self.instance_id,
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}