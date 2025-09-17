"""
PDPA Consent Management Service
Handles automatic consent collection and management for WhatsApp messaging
"""
import re
import logging
from datetime import datetime
from django.utils import timezone
from .models import Customer, Consent, Tenant, WhatsAppConnection, Conversation, CoreMessage, Contest, ContestEntry
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)

class PDPAConsentService:
    """Service for managing PDPA consent collection and responses"""
    
    # Consent response patterns
    CONSENT_YES_PATTERNS = [
        r'\b(yes|ya|setuju|ok|start|agree|consent)\b',
        r'\b(ya|setuju|ok|start)\b',  # BM patterns
    ]
    
    CONSENT_NO_PATTERNS = [
        r'\b(no|tak|tdk|nope|stop|batal|decline|reject)\b',
        r'\b(tak|tdk|batal)\b',  # BM patterns
    ]
    
    OPT_OUT_PATTERNS = [
        r'\b(stop|berhenti|unsubscribe)\b',
        r'\b(stop|berhenti)\b',  # BM patterns
    ]
    
    OPT_IN_PATTERNS = [
        r'\b(start|mulakan|subscribe)\b',
        r'\b(start|mulakan)\b',  # BM patterns
    ]
    
    def __init__(self):
        self.wa_service = WhatsAppAPIService()
    
    def handle_incoming_message(self, customer, message_text, tenant=None):
        """
        Handle incoming message and determine appropriate PDPA response
        Enhanced with contest integration
        """
        try:
            # Get tenant if not provided
            if not tenant:
                tenant = self._get_tenant_for_customer(customer)
            
            if not tenant:
                logger.error(f"No tenant found for customer {customer.customer_id}")
                return
            
            # Check current consent status
            consent_status = self._get_consent_status(tenant, customer, 'whatsapp')
            
            # Parse message for consent keywords
            message_lower = message_text.lower()
            
            # Check for opt-out first (highest priority)
            if self._is_opt_out_message(message_lower):
                return self._handle_opt_out(tenant, customer, message_text)
            
            # Check for opt-in
            if self._is_opt_in_message(message_lower):
                return self._handle_opt_in(tenant, customer, message_text)
            
            # Check for consent responses
            if self._is_consent_yes(message_lower):
                return self._handle_consent_yes(tenant, customer, message_text)
            
            if self._is_consent_no(message_lower):
                return self._handle_consent_no(tenant, customer, message_text)
            
            # Handle based on current consent status
            if consent_status == 'no_consent':
                return self._send_first_contact_template(tenant, customer)
            elif consent_status == 'withdrawn':
                return self._handle_withdrawn_consent(tenant, customer, message_text)
            else:  # granted
                return self._handle_normal_message(tenant, customer, message_text)
                
        except Exception as e:
            logger.error(f"Error handling incoming message for PDPA: {str(e)}")
            return None
    
    def _get_tenant_for_customer(self, customer):
        """Get tenant for customer"""
        try:
            return customer.tenant
        except:
            # Fallback to first tenant if no direct relationship
            return Tenant.objects.first()
    
    def _get_consent_status(self, tenant, customer, consent_type):
        """Get current consent status for customer"""
        try:
            latest_consent = Consent.objects.filter(
                tenant=tenant,
                customer=customer,
                type=consent_type
            ).order_by('-occurred_at').first()
            
            if not latest_consent:
                return 'no_consent'
            
            return latest_consent.status
            
        except Exception as e:
            logger.error(f"Error getting consent status: {str(e)}")
            return 'no_consent'
    
    def _is_opt_out_message(self, message_lower):
        """Check if message contains opt-out keywords"""
        for pattern in self.OPT_OUT_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _is_opt_in_message(self, message_lower):
        """Check if message contains opt-in keywords"""
        for pattern in self.OPT_IN_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _is_consent_yes(self, message_lower):
        """Check if message contains consent yes keywords"""
        for pattern in self.CONSENT_YES_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _is_consent_no(self, message_lower):
        """Check if message contains consent no keywords"""
        for pattern in self.CONSENT_NO_PATTERNS:
            if re.search(pattern, message_lower):
                return True
        return False
    
    def _send_first_contact_template(self, tenant, customer):
        """Send first contact PDPA template"""
        try:
            # Get brand name from tenant
            brand_name = tenant.name or "Our Company"
            customer_name = customer.name or "Valued Customer"
            
            # Send both BM and EN versions
            bm_message = self._get_first_contact_template_bm(brand_name, customer_name)
            en_message = self._get_first_contact_template_en(brand_name, customer_name)
            
            # Send BM version first
            self._send_message_to_customer(tenant, customer, bm_message)
            
            # Send EN version after a short delay (in real implementation)
            # For now, we'll send both immediately
            self._send_message_to_customer(tenant, customer, en_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending first contact template: {str(e)}")
            return False
    
    def _handle_consent_yes(self, tenant, customer, message_text):
        """Handle consent yes response"""
        try:
            # Record consent as granted
            self._record_consent(tenant, customer, 'whatsapp', 'granted', message_text)
            
            # Send confirmation messages
            bm_message = self._get_consent_confirmed_template_bm()
            en_message = self._get_consent_confirmed_template_en()
            
            self._send_message_to_customer(tenant, customer, bm_message)
            self._send_message_to_customer(tenant, customer, en_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling consent yes: {str(e)}")
            return False
    
    def _handle_consent_no(self, tenant, customer, message_text):
        """Handle consent no response"""
        try:
            # Record consent as withdrawn
            self._record_consent(tenant, customer, 'whatsapp', 'withdrawn', message_text)
            
            # Send decline confirmation
            bm_message = self._get_consent_declined_template_bm()
            en_message = self._get_consent_declined_template_en()
            
            self._send_message_to_customer(tenant, customer, bm_message)
            self._send_message_to_customer(tenant, customer, en_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling consent no: {str(e)}")
            return False
    
    def _handle_opt_out(self, tenant, customer, message_text):
        """Handle opt-out request"""
        try:
            # Record consent as withdrawn
            self._record_consent(tenant, customer, 'whatsapp', 'withdrawn', message_text)
            
            # Send opt-out confirmation
            bm_message = self._get_opt_out_template_bm()
            en_message = self._get_opt_out_template_en()
            
            self._send_message_to_customer(tenant, customer, bm_message)
            self._send_message_to_customer(tenant, customer, en_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling opt-out: {str(e)}")
            return False
    
    def _handle_opt_in(self, tenant, customer, message_text):
        """Handle opt-in request"""
        try:
            # Record consent as granted
            self._record_consent(tenant, customer, 'whatsapp', 'granted', message_text)
            
            # Send confirmation
            bm_message = self._get_consent_confirmed_template_bm()
            en_message = self._get_consent_confirmed_template_en()
            
            self._send_message_to_customer(tenant, customer, bm_message)
            self._send_message_to_customer(tenant, customer, en_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling opt-in: {str(e)}")
            return False
    
    def _handle_withdrawn_consent(self, tenant, customer, message_text):
        """Handle message from customer with withdrawn consent"""
        try:
            # Only send service/support replies, no marketing
            response = "Thank you for your message. For support inquiries, please contact us directly. Type START to opt-in for promotional messages."
            
            self._send_message_to_customer(tenant, customer, response)
            return True
            
        except Exception as e:
            logger.error(f"Error handling withdrawn consent: {str(e)}")
            return False
    
    def _handle_normal_message(self, tenant, customer, message_text):
        """Handle normal message from customer with granted consent"""
        try:
            # Check if customer needs to provide information
            if self._needs_customer_info(customer):
                return self._handle_info_collection(tenant, customer, message_text)
            
            # Normal handling - could be support, campaigns, etc.
            response = "Thank you for your message. We'll get back to you soon!"
            
            self._send_message_to_customer(tenant, customer, response)
            return True
            
        except Exception as e:
            logger.error(f"Error handling normal message: {str(e)}")
            return False
    
    def _needs_customer_info(self, customer):
        """Check if customer needs to provide more information"""
        # Check if customer has minimal information
        return (
            not customer.ic_number or 
            customer.gender == 'N/A' or 
            customer.marital_status == 'N/A' or
            not customer.age
        )
    
    def _handle_info_collection(self, tenant, customer, message_text):
        """Handle information collection from customer"""
        try:
            # Check if message contains IC number
            ic_match = self._extract_ic_number(message_text)
            if ic_match:
                return self._process_ic_number(tenant, customer, ic_match)
            
            # Check if message is a response to a question
            if hasattr(customer, '_waiting_for_response'):
                return self._process_info_response(tenant, customer, message_text)
            
            # Send information collection prompt
            return self._send_info_collection_prompt(tenant, customer)
            
        except Exception as e:
            logger.error(f"Error handling info collection: {str(e)}")
            return False
    
    def _extract_ic_number(self, message_text):
        """Extract IC number from message text"""
        import re
        # Malaysian IC pattern: 12 digits, format: YYMMDD-GG-####
        ic_pattern = r'\b\d{6}-\d{2}-\d{4}\b'
        match = re.search(ic_pattern, message_text)
        if match:
            return match.group()
        
        # Alternative pattern: 12 digits without dashes
        ic_pattern_alt = r'\b\d{12}\b'
        match = re.search(ic_pattern_alt, message_text)
        if match:
            ic = match.group()
            # Format with dashes
            return f"{ic[:6]}-{ic[6:8]}-{ic[8:]}"
        
        return None
    
    def _process_ic_number(self, tenant, customer, ic_number):
        """Process IC number and extract information"""
        try:
            # Parse IC number to extract birth date, gender, state
            birth_year = int(ic_number[:2])
            birth_month = int(ic_number[2:4])
            birth_day = int(ic_number[4:6])
            gender_code = int(ic_number[7:8])
            state_code = int(ic_number[8:10])
            
            # Convert 2-digit year to 4-digit
            current_year = datetime.now().year
            if birth_year > current_year % 100:
                birth_year += 1900
            else:
                birth_year += 2000
            
            # Calculate age
            from datetime import date
            today = date.today()
            age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
            
            # Determine gender
            gender = 'F' if gender_code % 2 == 0 else 'M'
            
            # Determine state (simplified mapping)
            state_mapping = {
                1: 'JHR', 2: 'KDH', 3: 'KTN', 4: 'MLK', 5: 'NSN',
                6: 'PHG', 7: 'PNG', 8: 'PRK', 9: 'SBH', 10: 'SWK',
                11: 'SEL', 12: 'TRG', 13: 'KUL', 14: 'LBN', 15: 'PJY'
            }
            state = state_mapping.get(state_code, 'N/A')
            
            # Update customer information
            customer.ic_number = ic_number
            customer.age = age
            customer.gender = gender
            customer.state = state
            customer.save()
            
            # Send confirmation
            response = f"""✅ IC processed successfully!

Name: {customer.name}
Age: {age} years
Gender: {gender}
State: {state}
IC: {ic_number}

Your information has been updated. Thank you!"""
            
            self._send_message_to_customer(tenant, customer, response)
            return True
            
        except Exception as e:
            logger.error(f"Error processing IC number: {str(e)}")
            # Send error message
            error_response = "❌ Sorry, I couldn't process your IC number. Please make sure it's in the correct format (e.g., 901231-01-1234) and try again."
            self._send_message_to_customer(tenant, customer, error_response)
            return False
    
    def _send_info_collection_prompt(self, tenant, customer):
        """Send information collection prompt to customer"""
        try:
            response = """📋 Hi! To provide you with better service, please share your information:

1️⃣ **IC Number**: Send your IC number (e.g., 901231-01-1234)
2️⃣ **Gender**: Reply with M (Male), F (Female), or NB (Non-binary)
3️⃣ **Marital Status**: Reply with SINGLE, MARRIED, DIVORCED, or WIDOWED

You can send your IC number first, and I'll automatically extract your age, gender, and state information!"""
            
            self._send_message_to_customer(tenant, customer, response)
            return True
            
        except Exception as e:
            logger.error(f"Error sending info collection prompt: {str(e)}")
            return False
    
    def _record_consent(self, tenant, customer, consent_type, status, message_text):
        """Record consent event in database"""
        try:
            Consent.objects.create(
                tenant=tenant,
                customer=customer,
                type=consent_type,
                status=status,
                occurred_at=timezone.now()
            )
            logger.info(f"Recorded consent: {consent_type} - {status} for customer {customer.customer_id}")
            
        except Exception as e:
            logger.error(f"Error recording consent: {str(e)}")
    
    def _send_message_to_customer(self, tenant, customer, message_text):
        """Send message to customer via WhatsApp"""
        try:
            # Get WhatsApp connection
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if not conn:
                logger.error(f"No WhatsApp connection found for tenant {tenant.tenant_id}")
                return False
            
            # Send via WhatsApp API
            result = self.wa_service.send_text_message(customer.phone_number, message_text)
            
            if result['success']:
                # Get or create conversation
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
                    direction='outbound',
                    status='sent',
                    text_body=message_text,
                    provider_msg_id=result.get('data', {}).get('id'),
                    sent_at=timezone.now()
                )
                
                logger.info(f"Sent PDPA message to {customer.phone_number}")
                return True
            else:
                logger.error(f"Failed to send message: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to customer: {str(e)}")
            return False
    
    # Template messages
    def _get_first_contact_template_bm(self, brand_name, customer_name):
        return f"""Hi {customer_name}! Anda dihubungi oleh {brand_name} berkaitan pembelian/promosi produk kami.
Dengan membalas YA, anda memberi kebenaran untuk kami menghantar mesej WhatsApp tentang resit, sokongan & promosi. Balas TIDAK untuk menolak.
Anda boleh berhenti pada bila-bila masa dengan taip STOP."""
    
    def _get_first_contact_template_en(self, brand_name, customer_name):
        return f"""Hi {customer_name}! This is {brand_name} about your purchase/promotions.
Reply YES to consent to receive WhatsApp messages for receipts, support & promos. Reply NO to decline.
You can opt out anytime by typing STOP."""
    
    def _get_consent_confirmed_template_bm(self):
        return """Terima kasih! Kebenaran anda telah direkodkan. Anda boleh taip STOP untuk berhenti pada bila-bila masa."""
    
    def _get_consent_confirmed_template_en(self):
        return """Thank you! Your consent has been recorded. You can type STOP anytime to opt out."""
    
    def _get_consent_declined_template_bm(self):
        return """Baik, kami tidak akan menghantar mesej promosi. Anda masih boleh hubungi kami untuk sokongan."""
    
    def _get_consent_declined_template_en(self):
        return """Understood. We won't send promotional messages. You can still contact us for support."""
    
    def _get_opt_out_template_bm(self):
        return """Notis diterima. Anda telah berhenti langganan. Taip START untuk melanggan semula."""
    
    def _get_opt_out_template_en(self):
        return """Noted. You've been unsubscribed. Type START to opt in again."""
    
    def should_send_marketing_message(self, tenant, customer):
        """Check if marketing messages should be sent to customer"""
        try:
            consent_status = self._get_consent_status(tenant, customer, 'whatsapp')
            return consent_status == 'granted'
        except Exception as e:
            logger.error(f"Error checking marketing consent: {str(e)}")
            return False
    
    # Contest Integration Methods
    def _handle_contest_integration(self, customer, message_text, tenant):
        """Handle contest integration after PDPA consent"""
        try:
            # Check if there's an active contest
            active_contest = Contest.objects.filter(
                tenant=tenant,
                is_active=True
            ).filter(
                starts_at__lte=timezone.now(),
                ends_at__gte=timezone.now()
            ).first()
            
            if not active_contest:
                return False
            
            # Check if customer already has an entry
            existing_entry = ContestEntry.objects.filter(
                contest=active_contest,
                customer=customer
            ).first()
            
            if existing_entry:
                # Handle existing entry based on status
                return self._handle_existing_contest_entry(customer, message_text, tenant, active_contest, existing_entry)
            else:
                # Create new contest entry and send post-PDPA message
                return self._create_contest_entry_and_send_message(customer, message_text, tenant, active_contest)
                
        except Exception as e:
            logger.error(f"Error in contest integration: {str(e)}")
            return False
    
    def _create_contest_entry_and_send_message(self, customer, message_text, tenant, contest):
        """Create contest entry and send post-PDPA message"""
        try:
            # Create contest entry
            entry = ContestEntry.objects.create(
                tenant=tenant,
                contest=contest,
                customer=customer,
                status='pending',
                contestant_name=customer.name,
                contestant_phone=customer.phone_number
            )
            
            # Send post-PDPA message
            self._send_contest_post_pdpa_message(customer, tenant, contest)
            
            logger.info(f"Created contest entry for {customer.name} in contest {contest.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating contest entry: {str(e)}")
            return False
    
    def _send_contest_post_pdpa_message(self, customer, tenant, contest):
        """Send post-PDPA message for contest"""
        try:
            # Send text message if available
            if contest.post_pdpa_text:
                self._send_message_to_customer(tenant, customer, contest.post_pdpa_text)
            
            # Send image if available
            if contest.post_pdpa_image_url:
                self._send_contest_image_message(customer, tenant, contest.post_pdpa_image_url)
            
            # Send GIF if available
            if contest.post_pdpa_gif_url:
                self._send_contest_gif_message(customer, tenant, contest.post_pdpa_gif_url)
            
            # Send contest instructions
            if contest.contest_instructions:
                instructions_msg = f"📋 Contest Instructions:\n\n{contest.contest_instructions}"
                self._send_message_to_customer(tenant, customer, instructions_msg)
            
        except Exception as e:
            logger.error(f"Error sending contest post-PDPA message: {str(e)}")
    
    def _send_contest_image_message(self, customer, tenant, image_url):
        """Send contest image message"""
        try:
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if not conn:
                return False
            
            result = self.wa_service.send_media_message(
                customer.phone_number,
                "Contest Information",
                image_url
            )
            
            if result['success']:
                # Create message record
                conversation, _ = Conversation.objects.get_or_create(
                    tenant=tenant,
                    customer=customer,
                    whatsapp_connection=conn,
                    defaults={}
                )
                
                CoreMessage.objects.create(
                    tenant=tenant,
                    conversation=conversation,
                    direction='outbound',
                    status='sent',
                    text_body='[Image: Contest Information]',
                    provider_msg_id=result.get('data', {}).get('id'),
                    sent_at=timezone.now()
                )
                
                return True
        except Exception as e:
            logger.error(f"Error sending contest image: {str(e)}")
            return False
    
    def _send_contest_gif_message(self, customer, tenant, gif_url):
        """Send contest GIF message"""
        try:
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            if not conn:
                return False
            
            result = self.wa_service.send_media_message(
                customer.phone_number,
                "Contest Animation",
                gif_url,
                filename="contest.gif"
            )
            
            if result['success']:
                # Create message record
                conversation, _ = Conversation.objects.get_or_create(
                    tenant=tenant,
                    customer=customer,
                    whatsapp_connection=conn,
                    defaults={}
                )
                
                CoreMessage.objects.create(
                    tenant=tenant,
                    conversation=conversation,
                    direction='outbound',
                    status='sent',
                    text_body='[GIF: Contest Animation]',
                    provider_msg_id=result.get('data', {}).get('id'),
                    sent_at=timezone.now()
                )
                
                return True
        except Exception as e:
            logger.error(f"Error sending contest GIF: {str(e)}")
            return False
