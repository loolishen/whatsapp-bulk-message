"""
WhatsApp Webhook Handler for receiving messages and images from customers
"""
import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .models import Customer, CoreMessage
from .ocr_service import OCRService
from .whatsapp_service import WhatsAppAPIService
from .pdpa_service import PDPAConsentService
from .step_by_step_contest_service import StepByStepContestService
from .keyword_autoreply_service import KeywordAutoReplyService
import requests

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """
    Handle incoming WhatsApp webhook events
    """
    
    def post(self, request):
        """Handle incoming webhook POST requests from WABOT"""
        try:
            # Parse webhook data
            try:
                data = json.loads(request.body)
                logger.info(f"Received WABOT webhook data: {data}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in webhook request: {e}")
                logger.error(f"Raw request body: {request.body}")
                logger.error(f"Content-Type: {request.META.get('CONTENT_TYPE', 'Not set')}")
                logger.error(f"Request method: {request.method}")
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
            
            # WABOT webhook format handling
            if 'type' in data:
                if data['type'] == 'message':
                    self._process_wabot_message(data)
                elif data['type'] == 'status':
                    self._process_wabot_status(data)
                elif data['type'] == 'qr':
                    logger.info("QR code received - instance ready for scanning")
                else:
                    logger.info(f"Unknown WABOT event type: {data['type']}")
            
            # Also handle Facebook/Meta webhook format for compatibility
            elif 'entry' in data:
                for entry in data['entry']:
                    if 'changes' in entry:
                        for change in entry['changes']:
                            if change.get('field') == 'messages':
                                self._handle_message_changes(change['value'])
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook request")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return JsonResponse({'error': 'Processing failed'}, status=500)
    
    def get(self, request):
        """Handle webhook verification"""
        # WhatsApp webhook verification
        verify_token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        expected_token = getattr(settings, 'WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'your_verify_token')
        
        if verify_token == expected_token:
            return HttpResponse(challenge)
        else:
            return HttpResponse('Verification failed', status=403)
    
    def _handle_message_changes(self, value):
        """Handle message changes from webhook"""
        try:
            # Handle incoming messages
            if 'messages' in value:
                for message in value['messages']:
                    self._process_incoming_message(message)
            
            # Handle message status updates
            if 'statuses' in value:
                for status in value['statuses']:
                    self._process_message_status(status)
                    
        except Exception as e:
            logger.error(f"Error handling message changes: {str(e)}")
    
    def _process_incoming_message(self, message_data):
        """Process incoming message from customer"""
        try:
            # Extract message details
            message_id = message_data.get('id')
            from_number = message_data.get('from')
            timestamp = message_data.get('timestamp')
            message_type = message_data.get('type')
            
            # Get or create customer
            contact = self._get_or_create_contact(from_number)
            
            # Process different message types
            if message_type == 'text':
                self._process_text_message(contact, message_data)
            elif message_type == 'image':
                self._process_image_message(contact, message_data)
            elif message_type == 'document':
                self._process_document_message(contact, message_data)
            
            # Update contact's last interaction
            contact.last_whatsapp_interaction = datetime.now()
            contact.message_count += 1
            contact.save()
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")
    
    def _process_text_message(self, contact, message_data):
        """Process incoming text message"""
        try:
            text_content = message_data.get('text', {}).get('body', '')
            
            # Get tenant from contact (assuming first tenant for now)
            from .models import Tenant
            tenant = Tenant.objects.first()
            
            # Get or create conversation
            from .models import WhatsAppConnection, Conversation
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if conn:
                conversation, _ = Conversation.objects.get_or_create(
                    tenant=tenant,
                    customer=contact,
                    whatsapp_connection=conn,
                    defaults={}
                )
            else:
                conversation = None
            
            # Create WhatsApp message record
                CoreMessage.objects.create(
                    tenant=tenant,
                    conversation=conversation,
                    direction='inbound',
                    status='delivered',
                    text_body=text_content,
                    provider_msg_id=message_data.get('id'),
                    created_at=timezone.now()
                )
            
            # Handle PDPA consent management first
            pdpa_service = PDPAConsentService()
            pdpa_handled = pdpa_service.handle_incoming_message(contact, text_content, tenant)
            
            # If PDPA didn't handle the message, use normal auto-response
            if not pdpa_handled:
                self._auto_respond_to_message(contact, text_content)
            
        except Exception as e:
            logger.error(f"Error processing text message: {str(e)}")
    
    def _process_image_message(self, contact, message_data):
        """Process incoming image message"""
        try:
            image_data = message_data.get('image', {})
            image_id = image_data.get('id')
            mime_type = image_data.get('mime_type', '')
            
            # Download image from WhatsApp
            image_url = self._download_whatsapp_media(image_id)
            
            if image_url:
                # Create WhatsApp message record
                CoreMessage.objects.create(
                    tenant=None,
                    conversation=None,
                    direction='inbound',
                    status='delivered',
                    text_body='[Image received]',
                    provider_msg_id=message_data.get('id')
                )
                
                # Process image with OCR
                self._process_image_with_ocr(contact, image_url)
            
        except Exception as e:
            logger.error(f"Error processing image message: {str(e)}")
    
    def _process_image_with_ocr(self, contact, image_path):
        """Process image with OCR to extract customer information"""
        try:
            # Get tenant (assuming first tenant for now - in production, determine from contact)
            from .models import Tenant
            tenant = Tenant.objects.first()
            
            if not tenant:
                logger.error("No tenant found for OCR processing")
                return
            
            # Initialize OCR service
            ocr_service = OCRService()
            
            # Process image
            result = ocr_service.process_image(image_path, tenant, contact.phone_number)
            
            if result['success']:
                # Send confirmation message
                self._send_ocr_confirmation(contact, result['extracted_data'])
            else:
                # Send error message
                self._send_ocr_error(contact, result.get('error', 'Unknown error'))
                
        except Exception as e:
            logger.error(f"Error processing image with OCR: {str(e)}")
            self._send_ocr_error(contact, str(e))
    
    def _process_document_message(self, contact, message_data):
        """Process incoming document message"""
        try:
            document_data = message_data.get('document', {})
            document_id = document_data.get('id')
            filename = document_data.get('filename', '')
            mime_type = document_data.get('mime_type', '')
            
            # Download document from WhatsApp
            document_url = self._download_whatsapp_media(document_id)
            
            if document_url:
                # Create WhatsApp message record
                CoreMessage.objects.create(
                    tenant=None,
                    conversation=None,
                    direction='inbound',
                    status='delivered',
                    text_body=f'[Document received: {filename}]',
                    provider_msg_id=message_data.get('id')
                )
                
                # Process document if it's an image
                # OCR processing disabled in this simplified handler
            
        except Exception as e:
            logger.error(f"Error processing document message: {str(e)}")
    
    # OCR and text extraction features are disabled in this simplified webhook handler.
    
    def _auto_respond_to_message(self, contact, text):
        """Auto-respond to customer messages"""
        try:
            text_lower = text.lower()
            
            # Simple auto-response logic
            if any(word in text_lower for word in ['hello', 'hi', 'hai', 'salam']):
                response = f"Hello {contact.name}! Thank you for contacting us. How can I help you today?"
            elif any(word in text_lower for word in ['help', 'bantuan']):
                response = "I can help you with:\n1. Submit your IC for registration\n2. Submit receipts for purchase tracking\n3. Check your account status\n\nPlease send your IC photo or receipt image."
            elif any(word in text_lower for word in ['status', 'account']):
                response = f"Your account status:\n- Total purchases: {contact.purchase_count}\n- Total spent: RM{contact.total_spent}\n- Customer tier: {contact.customer_tier}"
            else:
                response = "Thank you for your message. Please send your IC photo or receipt image for processing."
            
            # Send response
            self._send_whatsapp_message(contact, response)
            
        except Exception as e:
            logger.error(f"Error in auto-response: {str(e)}")
    
    def _send_ic_confirmation(self, contact, ic_data):
        """Send IC confirmation message"""
        try:
            message = f"✅ IC processed successfully!\n\n"
            message += f"Name: {contact.name}\n"
            message += f"Age: {ic_data.get('age')} years\n"
            message += f"Gender: {ic_data.get('gender')}\n"
            message += f"State: {ic_data.get('state')}\n"
            message += f"Birth Date: {ic_data.get('birth_date')}\n\n"
            message += "Your information has been updated in our system."
            
            self._send_whatsapp_message(contact, message)
            
        except Exception as e:
            logger.error(f"Error sending IC confirmation: {str(e)}")
    
    def _send_receipt_confirmation(self, contact, purchase):
        """Send receipt confirmation message"""
        try:
            message = f"✅ Receipt processed successfully!\n\n"
            message += f"Purchase Date: {purchase.purchase_date}\n"
            message += f"Total Amount: RM{purchase.total_amount}\n"
            message += f"Items: {len(purchase.items)}\n\n"
            message += f"Your total spending is now RM{contact.total_spent}\n"
            message += f"Customer Tier: {contact.customer_tier}"
            
            self._send_whatsapp_message(contact, message)
            
        except Exception as e:
            logger.error(f"Error sending receipt confirmation: {str(e)}")
    
    def _send_ocr_confirmation(self, contact, extracted_data):
        """Send OCR processing confirmation message"""
        try:
            message = "✅ Image processed successfully!\n\n"
            
            # Add extracted information
            if extracted_data.get('name'):
                message += f"Name: {extracted_data['name']}\n"
            
            if extracted_data.get('nric'):
                message += f"NRIC: {extracted_data['nric']}\n"
            
            if extracted_data.get('store_name'):
                message += f"Store: {extracted_data['store_name']}\n"
            
            if extracted_data.get('total_spent'):
                message += f"Amount: RM{extracted_data['total_spent']:.2f}\n"
            
            if extracted_data.get('products'):
                message += f"Products: {len(extracted_data['products'])} items\n"
            
            message += "\nYour information has been updated in our system."
            
            self._send_whatsapp_message(contact, message)
            
        except Exception as e:
            logger.error(f"Error sending OCR confirmation: {str(e)}")
    
    def _send_ocr_error(self, contact, error_message):
        """Send OCR processing error message"""
        try:
            message = f"❌ Sorry, I couldn't process your image.\n\n"
            message += f"Error: {error_message}\n\n"
            message += "Please try sending a clearer image of your receipt or IC."
            
            self._send_whatsapp_message(contact, message)
            
        except Exception as e:
            logger.error(f"Error sending OCR error message: {str(e)}")
    
    def _send_whatsapp_message(self, contact, message_text):
        """Send WhatsApp message to contact"""
        try:
            wa_service = WhatsAppAPIService()
            result = wa_service.send_text_message(contact.phone_number, message_text)
            
            if result['success']:
                # Get tenant and conversation
                from .models import Tenant, WhatsAppConnection, Conversation
                tenant = Tenant.objects.first()
                conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
                
                conversation = None
                if conn:
                    conversation, _ = Conversation.objects.get_or_create(
                        tenant=tenant,
                        customer=contact,
                        whatsapp_connection=conn,
                        defaults={}
                    )
                
                # Create outbound message record
                CoreMessage.objects.create(
                    tenant=tenant,
                    conversation=conversation,
                    direction='outbound',
                    status='sent',
                    text_body=message_text,
                    provider_msg_id=result.get('data', {}).get('id'),
                    sent_at=datetime.now()
                )
                
                logger.info(f"Sent message to {contact.name}: {message_text[:50]}...")
            else:
                logger.error(f"Failed to send message to {contact.name}: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
    
    def _download_whatsapp_media(self, media_id):
        """Download media from WhatsApp API"""
        try:
            # Get media URL from WhatsApp API
            wa_service = WhatsAppAPIService()
            media_url = wa_service.get_media_url(media_id)
            
            if media_url:
                # Download media content
                response = requests.get(media_url)
                if response.status_code == 200:
                    # Upload to your storage (Cloudinary, etc.)
                    from .cloudinary_service import cloudinary_service
                    result = cloudinary_service.upload_file_from_url(media_url)
                    if result['success']:
                        return result['url']
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading WhatsApp media: {str(e)}")
            return None
    
    def _get_or_create_contact(self, phone_number):
        """Get or create contact from phone number"""
        try:
            # Clean phone number
            clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
            if not clean_phone.startswith('60'):
                clean_phone = '60' + clean_phone
            
            # Get tenant (assuming first tenant for now)
            from .models import Tenant
            tenant = Tenant.objects.first()
            if not tenant:
                logger.error("No tenant found for customer creation")
                return None
            
            # Try to find existing contact
            contact = Customer.objects.filter(
                phone_number__icontains=clean_phone,
                tenant=tenant
            ).first()
            
            if not contact:
                # Create new contact with tenant
                contact = Customer.objects.create(
                    name=f"Customer {clean_phone[-4:]}",
                    phone_number=clean_phone,
                    tenant=tenant,
                    gender='N/A',
                    marital_status='N/A'
                )
                logger.info(f"Created new customer: {contact.name} ({contact.phone_number})")
            else:
                logger.info(f"Found existing customer: {contact.name} ({contact.phone_number})")
            
            return contact
            
        except Exception as e:
            logger.error(f"Error getting/creating contact: {str(e)}")
            return None
    
    def _process_wabot_message(self, data):
        """Process incoming message from WABOT webhook"""
        try:
            # Extract WABOT message data
            message_data = data.get('data', {})
            from_number = message_data.get('from')
            message_text = message_data.get('message', '')
            message_id = message_data.get('id')
            timestamp = message_data.get('timestamp')
            
            logger.info(f"Processing WABOT message from {from_number}: {message_text}")
            
            # Get or create customer
            contact = self._get_or_create_contact(from_number)
            if not contact:
                logger.error(f"Failed to create/find contact for {from_number}")
                return
            
            # Get tenant
            from .models import Tenant
            tenant = Tenant.objects.first()
            if not tenant:
                logger.error("No tenant found")
                return
            
            # Get or create conversation
            from .models import WhatsAppConnection, Conversation
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if conn:
                conversation, _ = Conversation.objects.get_or_create(
                    tenant=tenant,
                    customer=contact,
                    whatsapp_connection=conn,
                    defaults={}
                )
            else:
                conversation = None
            
            # Create inbound message record
            CoreMessage.objects.create(
                tenant=tenant,
                conversation=conversation,
                direction='inbound',
                status='delivered',
                text_body=message_text,
                provider_msg_id=message_id,
                created_at=datetime.now()
            )
            
            # Handle PDPA consent management
            pdpa_service = PDPAConsentService()
            pdpa_handled = pdpa_service.handle_incoming_message(contact, message_text, tenant)
            
            # Process step-by-step contest flow (after PDPA)
            step_contest_service = StepByStepContestService()
            contest_results = step_contest_service.process_message_for_contests(
                contact, message_text, tenant, conversation
            )
            
            # Log contest processing results
            if contest_results['flows_processed'] > 0:
                logger.info(f"Step-by-step contest processing: {contest_results}")
            
            # Process keyword-based auto-replies
            keyword_service = KeywordAutoReplyService()
            keyword_results = keyword_service.process_message(
                customer=contact,
                message_text=message_text,
                tenant=tenant,
                conversation=conversation
            )
            
            # Log keyword matching results
            if keyword_results['matched']:
                logger.info(f"Keyword auto-reply: {keyword_results['replies_sent']} replies sent for keywords: {keyword_results['keywords_matched']}")
            
            # If nothing handled the message, use fallback auto-response
            if not pdpa_handled and not keyword_results['matched']:
                self._auto_respond_to_message(contact, message_text)
            
            # Update contact's last interaction
            contact.last_whatsapp_interaction = datetime.now()
            contact.save()
            
            logger.info(f"Successfully processed message from {contact.name}")
            
        except Exception as e:
            logger.error(f"Error processing WABOT message: {str(e)}")
    
    def _process_wabot_status(self, data):
        """Process message status updates from WABOT"""
        try:
            status_data = data.get('data', {})
            message_id = status_data.get('id')
            status = status_data.get('status')
            timestamp = status_data.get('timestamp')
            
            logger.info(f"Message status update: {message_id} -> {status}")
            
            # Update message status in database
            if message_id:
                CoreMessage.objects.filter(provider_msg_id=message_id).update(
                    status=status,
                    updated_at=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error processing WABOT status: {str(e)}")
    
    def _process_message_status(self, status_data):
        """Process message status updates"""
        try:
            message_id = status_data.get('id')
            status = status_data.get('status')
            timestamp = status_data.get('timestamp')
            
            # Update message status in database
            # TODO: Update CoreMessage by provider_msg_id if desired
                
        except Exception as e:
            logger.error(f"Error processing message status: {str(e)}")


# URL patterns for webhook
whatsapp_webhook = WhatsAppWebhookView.as_view()
