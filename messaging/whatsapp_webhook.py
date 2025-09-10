"""
WhatsApp Webhook Handler for receiving messages and images from customers
"""
import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from .models import Contact, WhatsAppMessage, OCRProcessingLog, Purchase
from .ocr_service import OCRService
from .whatsapp_service import WhatsAppAPIService
import requests

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """
    Handle incoming WhatsApp webhook events
    """
    
    def post(self, request):
        """Handle incoming webhook POST requests"""
        try:
            # Parse webhook data
            data = json.loads(request.body)
            logger.info(f"Received webhook data: {data}")
            
            # Handle different types of webhook events
            if 'entry' in data:
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
            
            # Get or create contact
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
            
            # Create WhatsApp message record
            WhatsAppMessage.objects.create(
                contact=contact,
                message_type='RECEIVED',
                message_text=text_content,
                whatsapp_message_id=message_data.get('id'),
                status='DELIVERED'
            )
            
            # Check if message contains IC number or receipt information
            self._check_for_ic_or_receipt_info(contact, text_content)
            
            # Auto-respond if needed
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
                WhatsAppMessage.objects.create(
                    contact=contact,
                    message_type='RECEIVED',
                    message_text='[Image received]',
                    media_url=image_url,
                    media_type='image',
                    whatsapp_message_id=message_data.get('id'),
                    status='DELIVERED'
                )
                
                # Process image with OCR
                self._process_image_with_ocr(contact, image_url, 'OTHER')
            
        except Exception as e:
            logger.error(f"Error processing image message: {str(e)}")
    
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
                WhatsAppMessage.objects.create(
                    contact=contact,
                    message_type='RECEIVED',
                    message_text=f'[Document received: {filename}]',
                    media_url=document_url,
                    media_type='document',
                    whatsapp_message_id=message_data.get('id'),
                    status='DELIVERED'
                )
                
                # Process document if it's an image
                if mime_type.startswith('image/'):
                    self._process_image_with_ocr(contact, document_url, 'OTHER')
            
        except Exception as e:
            logger.error(f"Error processing document message: {str(e)}")
    
    def _process_image_with_ocr(self, contact, image_url, image_type):
        """Process image with OCR service"""
        try:
            # Create OCR processing log
            ocr_log = OCRProcessingLog.objects.create(
                image_url=image_url,
                image_type=image_type,
                contact=contact,
                status='PROCESSING'
            )
            
            # Process with OCR service
            ocr_service = OCRService()
            result = ocr_service.process_image(image_url, image_type)
            
            # Update OCR log
            ocr_log.status = 'COMPLETED' if result['success'] else 'FAILED'
            ocr_log.extracted_text = result.get('extracted_text', '')
            ocr_log.confidence_score = result.get('confidence', 0.0)
            ocr_log.extracted_data = result.get('extracted_data', {})
            ocr_log.processing_errors = result.get('error', '')
            ocr_log.processed_at = datetime.now()
            ocr_log.save()
            
            # Process extracted data
            if result['success']:
                self._process_ocr_results(contact, ocr_log)
            
        except Exception as e:
            logger.error(f"Error processing image with OCR: {str(e)}")
    
    def _process_ocr_results(self, contact, ocr_log):
        """Process OCR results and update contact/purchase data"""
        try:
            extracted_data = ocr_log.extracted_data
            
            if ocr_log.image_type == 'IC' and 'valid' in extracted_data and extracted_data['valid']:
                # Update contact with IC information
                contact.ic_number = extracted_data.get('ic_number')
                contact.age = extracted_data.get('age')
                contact.gender = extracted_data.get('gender')
                contact.state = extracted_data.get('state')
                if extracted_data.get('birth_date'):
                    from datetime import datetime
                    contact.date_of_birth = datetime.strptime(extracted_data['birth_date'], '%Y-%m-%d').date()
                contact.save()
                
                # Send confirmation message
                self._send_ic_confirmation(contact, extracted_data)
                
            elif ocr_log.image_type == 'RECEIPT' and 'valid' in extracted_data and extracted_data['valid']:
                # Create purchase record
                purchase = Purchase.objects.create(
                    customer=contact,
                    receipt_image=ocr_log.image_url,
                    receipt_text=ocr_log.extracted_text,
                    total_amount=extracted_data.get('total_amount', 0),
                    purchase_date=datetime.strptime(extracted_data['purchase_date'], '%Y-%m-%d').date() if extracted_data.get('purchase_date') else datetime.now().date(),
                    items=extracted_data.get('items', []),
                    ocr_processed=True,
                    ocr_confidence=ocr_log.confidence_score
                )
                
                # Send confirmation message
                self._send_receipt_confirmation(contact, purchase)
                
        except Exception as e:
            logger.error(f"Error processing OCR results: {str(e)}")
    
    def _check_for_ic_or_receipt_info(self, contact, text):
        """Check if text message contains IC or receipt information"""
        try:
            ocr_service = OCRService()
            
            # Check for IC number in text
            ic_data = ocr_service.extract_ic_from_text(text)
            if ic_data and ic_data.get('valid'):
                # Update contact with IC information
                contact.ic_number = ic_data.get('ic_number')
                contact.age = ic_data.get('age')
                contact.gender = ic_data.get('gender')
                contact.state = ic_data.get('state')
                if ic_data.get('birth_date'):
                    from datetime import datetime
                    contact.date_of_birth = datetime.strptime(ic_data['birth_date'], '%Y-%m-%d').date()
                contact.save()
                
                # Send confirmation
                self._send_ic_confirmation(contact, ic_data)
            
            # Check for receipt information
            receipt_data = ocr_service.extract_receipt_data_from_text(text)
            if receipt_data and receipt_data.get('valid'):
                # Create purchase record
                purchase = Purchase.objects.create(
                    customer=contact,
                    receipt_text=text,
                    total_amount=receipt_data.get('total_amount', 0),
                    purchase_date=datetime.strptime(receipt_data['purchase_date'], '%Y-%m-%d').date() if receipt_data.get('purchase_date') else datetime.now().date(),
                    items=receipt_data.get('items', []),
                    ocr_processed=True
                )
                
                # Send confirmation
                self._send_receipt_confirmation(contact, purchase)
                
        except Exception as e:
            logger.error(f"Error checking for IC/receipt info: {str(e)}")
    
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
    
    def _send_whatsapp_message(self, contact, message_text):
        """Send WhatsApp message to contact"""
        try:
            wa_service = WhatsAppAPIService()
            result = wa_service.send_text_message(contact.phone_number, message_text)
            
            if result['success']:
                # Create message record
                WhatsAppMessage.objects.create(
                    contact=contact,
                    message_type='SENT',
                    message_text=message_text,
                    whatsapp_message_id=result.get('message_id'),
                    status='SENT',
                    sent_at=datetime.now()
                )
            
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
            
            # Try to find existing contact
            contact = Contact.objects.filter(phone_number__icontains=clean_phone).first()
            
            if not contact:
                # Create new contact
                contact = Contact.objects.create(
                    name=f"Customer {clean_phone[-4:]}",  # Temporary name
                    phone_number=clean_phone,
                    event_source='WhatsApp Webhook'
                )
            
            return contact
            
        except Exception as e:
            logger.error(f"Error getting/creating contact: {str(e)}")
            return None
    
    def _process_message_status(self, status_data):
        """Process message status updates"""
        try:
            message_id = status_data.get('id')
            status = status_data.get('status')
            timestamp = status_data.get('timestamp')
            
            # Update message status in database
            try:
                wa_message = WhatsAppMessage.objects.get(whatsapp_message_id=message_id)
                
                if status == 'delivered':
                    wa_message.status = 'DELIVERED'
                    wa_message.delivered_at = datetime.fromtimestamp(int(timestamp))
                elif status == 'read':
                    wa_message.status = 'READ'
                    wa_message.read_at = datetime.fromtimestamp(int(timestamp))
                elif status == 'failed':
                    wa_message.status = 'FAILED'
                
                wa_message.save()
                
            except WhatsAppMessage.DoesNotExist:
                logger.warning(f"Message not found for status update: {message_id}")
                
        except Exception as e:
            logger.error(f"Error processing message status: {str(e)}")


# URL patterns for webhook
whatsapp_webhook = WhatsAppWebhookView.as_view()
