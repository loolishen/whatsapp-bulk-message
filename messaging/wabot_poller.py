"""
WABOT Message Poller - Polls WABOT API for new messages
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Customer, CoreMessage, Conversation, WhatsAppConnection, Tenant
from .pdpa_service import PDPAConsentService

logger = logging.getLogger(__name__)

class WABOTPoller:
    def __init__(self):
        self.base_url = "https://app.wabot.my/api"
        self.access_token = "68a0a10422130"
        self.instance_id = "68A0A11A89A8D"
        self.pdpa_service = PDPAConsentService()
    
    def poll_messages(self):
        """Poll WABOT for new messages"""
        try:
            # Get messages from WABOT
            url = f"{self.base_url}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get messages from last 5 minutes
            since = datetime.now() - timedelta(minutes=5)
            params = {
                'instance_id': self.instance_id,
                'since': since.isoformat()
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('data', [])
                
                for message in messages:
                    self._process_message(message)
                    
                logger.info(f"Processed {len(messages)} messages from WABOT")
                return True
            else:
                logger.error(f"Failed to poll WABOT: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error polling WABOT: {str(e)}")
            return False
    
    def _process_message(self, message_data):
        """Process a single message from WABOT"""
        try:
            # Extract message details
            from_number = message_data.get('from')
            message_text = message_data.get('body', '')
            message_id = message_data.get('id')
            timestamp = message_data.get('timestamp')
            
            if not from_number or not message_text:
                return
            
            # Get or create customer
            customer = self._get_or_create_customer(from_number)
            if not customer:
                return
            
            # Get tenant (assuming first tenant for now)
            tenant = Tenant.objects.first()
            if not tenant:
                logger.error("No tenant found")
                return
            
            # Get WhatsApp connection
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if not conn:
                logger.error("No WhatsApp connection found")
                return
            
            # Create conversation
            conversation, _ = Conversation.objects.get_or_create(
                tenant=tenant,
                customer=customer,
                whatsapp_connection=conn,
                defaults={}
            )
            
            # Create message record
            CoreMessage.objects.create(
                tenant=tenant,
                conversation=conversation,
                direction='inbound',
                status='delivered',
                text_body=message_text,
                provider_msg_id=message_id,
                created_at=timezone.now()
            )
            
            # Process with PDPA service
            self.pdpa_service.handle_incoming_message(customer, message_text, tenant)
            
            logger.info(f"Processed message from {from_number}: {message_text[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    def _get_or_create_customer(self, phone_number):
        """Get or create customer from phone number"""
        try:
            # Clean phone number
            clean_number = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            if not clean_number.startswith('60'):
                clean_number = '60' + clean_number
            
            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                phone_number=clean_number,
                defaults={
                    'name': f'Customer {clean_number}',
                    'email': '',
                    'address': '',
                    'created_at': timezone.now()
                }
            )
            
            if created:
                logger.info(f"Created new customer: {customer.name} ({customer.phone_number})")
            
            return customer
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return None

