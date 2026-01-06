"""
Step-by-Step Contest Flow Service

This service implements the complete step-by-step contest flow:
1. Contestant sends hi/hello message
2. System sends PDPA message (from contest form)
3. Contestant accepts/rejects
4. System sends acceptance/rejection response
5. System sends contest instructions (from contest form)
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
import re
from .models import Contest, ContestEntry, Customer, Tenant, Conversation, WhatsAppConnection, ContestFlowState
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)

class StepByStepContestService:
    """
    Service to handle step-by-step contest flow with dynamic prompts from contest form
    """
    
    def __init__(self):
        self.wa_service = WhatsAppAPIService()
    
    def process_message_for_contests(self, customer, message_text, tenant, conversation=None, media_url=None, media_type=None, media_meta=None):
        """
        Process incoming message and handle step-by-step contest flow
        
        Args:
            customer: Customer object who sent the message
            message_text: The message content
            tenant: Tenant object
            conversation: Conversation object (optional)
            media_url: URL of attached media (image/video/document)
            media_type: Type of media ('image', 'video', 'document')
        
        Returns:
            dict: Results of contest processing
        """
        """
        Receipt-first rules:
        - Resume ONLY the most recent in-progress flow (if any)
        - Otherwise start the contest when the user sends a receipt image (preferred)
        - If the user types text/keyword first, ask them to send a receipt photo
        """
        try:
            results = {
                'contests_checked': 0,
                'flows_processed': 0,
                'flows_created': 0,
                'flows_advanced': 0,
                'errors': []
            }

            # 1) Resume existing in-progress flow (only one)
            in_progress = ContestFlowState.objects.filter(
                customer=customer,
                current_step__in=['initial', 'pdpa_response', 'awaiting_nric', 'awaiting_receipt']
            ).select_related('contest').order_by('-last_updated')

            if in_progress.exists():
                flow_state = in_progress.first()
                contest = flow_state.contest
                result = self._handle_flow_step(
                    flow_state,
                    customer,
                    message_text,
                    tenant,
                    contest,
                    conversation,
                    media_url=media_url,
                    media_type=media_type,
                    media_meta=media_meta,
                )
                results['contests_checked'] = 1
                results['flows_processed'] = 1
                if result.get('action') == 'created':
                    results['flows_created'] += 1
                elif result.get('action') == 'advanced':
                    results['flows_advanced'] += 1
                logger.info(f"Step-by-step contest processing (resume) completed: {results}")
                return results

            # 2) No in-progress flow -> start only the first matching contest
            active_contests = self._get_active_contests(tenant)
            results['contests_checked'] = len(active_contests)

            if not active_contests:
                logger.info(f"No active contests found for tenant {tenant.name}")
                return results

            # Receipt-first: if user sends an image first, start the contest without requiring keywords.
            has_receipt_image = bool(media_url) and (media_type == "image")

            # If we previously asked the user to choose a contest (multiple active) after a receipt,
            # we cache the receipt for a short period and reuse it once they reply with a keyword.
            pending_key = f"pending_receipt:{tenant.tenant_id}:{customer.customer_id}"
            pending = cache.get(pending_key)

            matched = None
            # If user has a cached receipt and now replied with a keyword, match contest and reuse the receipt.
            if (not has_receipt_image) and pending and (message_text or "").strip():
                for contest in active_contests:
                    if contest.matches_message(message_text):
                        matched = contest
                        # override media with cached receipt
                        media_url = pending.get("media_url") or media_url
                        media_type = "image"
                        media_meta = pending.get("media_meta") or media_meta
                        cache.delete(pending_key)
                        has_receipt_image = True
                        break

            # If no keyword match, receipt image can start the (single) active contest.
            if not matched and has_receipt_image:
                if len(active_contests) == 1:
                    matched = active_contests[0]
                else:
                    # Multiple active contests: ask user to pick a contest keyword, cache receipt temporarily.
                    try:
                        options = []
                        for c in active_contests[:5]:
                            kws = c.get_keywords_list()
                            kw = kws[0].upper() if kws else c.name
                            options.append(f"- {c.name}: reply `{kw}`")
                        msg = (
                            "🧾 Receipt received.\n\n"
                            "Multiple contests are currently active.\n"
                            "Please reply with the contest keyword to choose:\n"
                            + "\n".join(options)
                        )
                        self._send_message_to_customer(tenant, customer, msg, contest=None, conversation=conversation)
                        cache.set(
                            pending_key,
                            {"media_url": media_url, "media_meta": media_meta or {}},
                            timeout=15 * 60,
                        )
                    except Exception:
                        pass
                    logger.info("Receipt image received but multiple contests active; asked user to choose contest keyword.")
                    return results

            # Fallback: match by keyword if user typed it (non-receipt first).
            if not matched:
                for contest in active_contests:
                    if contest.matches_message(message_text):
                        matched = contest
                        break

            if not matched:
                logger.info("No matching contest for message from %s: %s", customer.phone_number, (message_text or "")[:80])
                return results

            result = self._process_contest_flow(
                customer,
                message_text,
                tenant,
                matched,
                conversation,
                media_url=media_url,
                media_type=media_type,
                media_meta=media_meta,
            )
            results['flows_processed'] = 1
            if result.get('action') == 'created':
                results['flows_created'] += 1
            elif result.get('action') == 'advanced':
                results['flows_advanced'] += 1

            logger.info(f"Step-by-step contest processing (new match) completed: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in step-by-step contest processing: {str(e)}", exc_info=True)
            return {'contests_checked': 0, 'flows_processed': 0, 'flows_created': 0, 'flows_advanced': 0, 'errors': [str(e)]}
    
    def _get_active_contests(self, tenant):
        """Get all currently active contests for a tenant"""
        now = timezone.now()
        
        return Contest.objects.filter(
            tenant=tenant,
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        ).order_by('-auto_reply_priority', '-created_at')
    
    def _process_contest_flow(self, customer, message_text, tenant, contest, conversation=None, media_url=None, media_type=None, media_meta=None):
        """
        Process the step-by-step flow for a single contest
        
        Args:
            customer: Customer object
            message_text: Message content
            tenant: Tenant object
            contest: Contest object
            conversation: Conversation object (optional)
        
        Returns:
            dict: Processing result
        """
        try:
            # Get or create flow state
            flow_state, created = ContestFlowState.objects.get_or_create(
                customer=customer,
                contest=contest,
                defaults={'current_step': 'initial'}
            )
            
            if created:
                logger.info(f"Created new flow state for {customer.name} in contest {contest.name}")
                # Receipt-first: if the first message is a receipt image OR keyword/text, handle it immediately.
                if (media_type == "image" and media_url) or contest.matches_message(message_text) or (message_text or "").strip():
                    # NOTE: use locals().get(...) so this code is resilient even if an older
                    # deployed signature does not define media_url/media_type (prevents NameError).
                    return self._handle_flow_step(
                        flow_state,
                        customer,
                        message_text,
                        tenant,
                        contest,
                        conversation,
                        media_url=locals().get("media_url"),
                        media_type=locals().get("media_type"),
                        media_meta=media_meta,
                    )
                return {'action': 'created', 'flow_id': str(flow_state.flow_id)}
            
            # Process based on current step
            # NOTE: use locals().get(...) so this code is resilient even if an older
            # deployed signature does not define media_url/media_type (prevents NameError).
            return self._handle_flow_step(
                flow_state,
                customer,
                message_text,
                tenant,
                contest,
                conversation,
                media_url=locals().get("media_url"),
                media_type=locals().get("media_type"),
                media_meta=media_meta,
            )
                
        except Exception as e:
            logger.error(f"Error processing contest flow: {str(e)}")
            raise
    
    def _handle_flow_step(self, flow_state, customer, message_text, tenant, contest, conversation, media_url=None, media_type=None, media_meta=None):
        """
        Handle the current step in the flow
        
        Args:
            flow_state: ContestFlowState object
            customer: Customer object
            message_text: Message content
            tenant: Tenant object
            contest: Contest object
            conversation: Conversation object (optional)
        
        Returns:
            dict: Processing result
        """
        try:
            message_lower = message_text.lower().strip()
            
            # Step 1: Receipt-first entry point
            if flow_state.current_step == 'initial':
                # If they sent a receipt image first, process it immediately.
                if media_type == "image" and media_url:
                    flow_state.advance_step('awaiting_receipt')
                    return self._handle_receipt_submission(
                        flow_state,
                        customer,
                        message_text,
                        tenant,
                        contest,
                        conversation,
                        media_url=media_url,
                        media_type=media_type,
                        media_meta=media_meta,
                    )

                # If they sent text first (keyword/hi/etc), ask for the receipt photo.
                if (message_text or "").strip():
                    ask_receipt = (
                        f"Hi! To join **{contest.name}**, please send a clear photo of your purchase receipt.\n\n"
                        "Once we read the receipt, we’ll ask for your consent (privacy policy) and then collect your details."
                    )
                    self._send_message_to_customer(tenant, customer, ask_receipt, contest=contest, conversation=conversation)
                    flow_state.advance_step('awaiting_receipt')
                    flow_state.add_message_sent('ask_receipt', 'Asked for receipt photo (receipt-first)')
                    return {'action': 'advanced', 'step': 'awaiting_receipt', 'flow_id': str(flow_state.flow_id)}

                return {'action': 'ignored', 'reason': 'empty_message'}
            
            # Step 2: PDPA response handling
            elif flow_state.current_step == 'pdpa_response':
                return self._handle_pdpa_response(flow_state, customer, message_text, tenant, contest, conversation)
            
            # Step 3: Awaiting NRIC/details submission
            elif flow_state.current_step == 'awaiting_nric':
                return self._handle_nric_submission(flow_state, customer, message_text, tenant, contest, conversation)
            
            # Step 4: Awaiting receipt submission
            elif flow_state.current_step == 'awaiting_receipt':
                return self._handle_receipt_submission(
                    flow_state,
                    customer,
                    message_text,
                    tenant,
                    contest,
                    conversation,
                    media_url=media_url,
                    media_type=media_type,
                    media_meta=media_meta,
                )
            
            # Step 5: Awaiting confirmation (deprecated - now handled directly in _handle_nric_submission)
            elif flow_state.current_step == 'awaiting_submission':
                # This step is no longer used - details are confirmed automatically
                return {'action': 'ignored', 'reason': 'deprecated_step'}
            
            # Other steps - no processing needed
            else:
                return {'action': 'ignored', 'reason': 'step_completed'}
                
        except Exception as e:
            logger.error(f"Error handling flow step: {str(e)}")
            raise
    
    def _is_greeting_message(self, message_lower):
        """Check if message is a greeting"""
        greetings = [
            'hi', 'hello', 'hai', 'salam', 'hey', 'good morning', 'good afternoon', 
            'good evening', 'selamat pagi', 'selamat petang', 'selamat malam',
            'contest', 'join', 'participate', 'enter'
        ]
        
        return any(greeting in message_lower for greeting in greetings)
    
    def _handle_initial_contact(self, flow_state, customer, tenant, contest, conversation):
        """Handle initial contact - send introduction message then PDPA"""
        try:
            # Step 1: Send introduction message (if exists)
            if hasattr(contest, 'introduction_message') and contest.introduction_message:
                self._send_message_to_customer(tenant, customer, contest.introduction_message, contest=contest, conversation=conversation)
                flow_state.add_message_sent('introduction', 'Introduction message sent')
                logger.info(f"Sent introduction message to {customer.name} for contest {contest.name}")
            
            # Step 2: Send PDPA consent message using contest form fields
            if contest.pdpa_message:
                self._send_message_to_customer(tenant, customer, contest.pdpa_message, contest=contest, conversation=conversation)
            else:
                # Default PDPA message
                default_pdpa = f"Before we continue, we need your consent to collect and process your personal data.\n\n"
                default_pdpa += "Do you agree to participate and allow us to process your information?\n\n"
                default_pdpa += "Reply 'I agree' to continue or 'No' to opt out."
                self._send_message_to_customer(tenant, customer, default_pdpa, contest=contest, conversation=conversation)
            
            # Advance to PDPA response step
            flow_state.advance_step('pdpa_response')
            flow_state.add_message_sent('pdpa', 'PDPA consent message sent')
            
            logger.info(f"Sent introduction and PDPA message to {customer.name} for contest {contest.name}")
            
            return {
                'action': 'advanced',
                'step': 'pdpa_sent',
                'flow_id': str(flow_state.flow_id)
            }
            
        except Exception as e:
            logger.error(f"Error handling initial contact: {str(e)}")
            raise
    
    def _handle_pdpa_response(self, flow_state, customer, message_text, tenant, contest, conversation):
        """Handle PDPA response (yes/no/stop)"""
        try:
            message_lower = message_text.lower().strip()
            
            # Check for consent responses
            if self._is_consent_yes(message_lower):
                flow_state.pdpa_response = 'yes'
                flow_state.pdpa_responded_at = timezone.now()
                flow_state.save()
                
                # Step 1: Send agreement response message
                if contest.participant_agreement:
                    self._send_message_to_customer(tenant, customer, contest.participant_agreement, contest=contest, conversation=conversation)
                else:
                    self._send_message_to_customer(
                        tenant,
                        customer,
                        "✅ Thank you for your consent!",
                        contest=contest,
                        conversation=conversation,
                    )
                
                flow_state.add_message_sent('pdpa_acceptance', 'PDPA acceptance response sent')
                
                # Step 2: Wait 3 seconds, then send "one final step" message
                import threading
                def send_info_request():
                    import time
                    time.sleep(3)  # Wait 3 seconds
                    
                    # Send the "one final step" message asking for name/email/nric
                    # Use post_pdpa_text from contest form if available
                    if contest.post_pdpa_text:
                        info_request_msg = contest.post_pdpa_text
                    else:
                        info_request_msg = (
                            "One final step before we continue and enter you into the contest.\n\n"
                            "We need your:\n"
                            "• Full name\n"
                            "• Email address\n"
                        )
                        if contest.requires_nric:
                            info_request_msg += "• IC/NRIC number\n"
                        info_request_msg += "\nPlease reply with your **full name** to start."
                    
                    self._send_message_to_customer(tenant, customer, info_request_msg, contest=contest, conversation=conversation)
                    
                    # Start required info collection (name/email, then NRIC if required)
                    flow_state.metadata = flow_state.metadata or {}
                    flow_state.metadata['details_step'] = 'name'
                    flow_state.save()
                    
                    # Reuse awaiting_nric step as the "awaiting_details" state
                    flow_state.advance_step('awaiting_nric')
                    flow_state.add_message_sent('info_request', 'Info request sent after 3 second delay')
                
                # Start the delayed message in a background thread
                thread = threading.Thread(target=send_info_request)
                thread.daemon = True
                thread.start()
                
                logger.info(f"PDPA accepted by {customer.name} for contest {contest.name}, info request scheduled")
                
                return {
                    'action': 'advanced',
                    'step': 'pdpa_accepted',
                    'flow_id': str(flow_state.flow_id)
                }
            
            elif self._is_consent_no(message_lower) or self._is_opt_out_message(message_lower):
                flow_state.pdpa_response = 'no' if self._is_consent_no(message_lower) else 'stop'
                flow_state.pdpa_responded_at = timezone.now()
                flow_state.save()
                
                # Send participant rejection message from contest form
                if contest.participant_rejection:
                    self._send_message_to_customer(tenant, customer, contest.participant_rejection, contest=contest, conversation=conversation)
                else:
                    self._send_message_to_customer(tenant, customer, "We respect your choice, you won't receive contest messages.", contest=contest, conversation=conversation)
                
                # Mark flow as completed (rejected)
                flow_state.advance_step('completed')
                flow_state.add_message_sent('pdpa_rejection', 'PDPA rejection response sent')
                
                logger.info(f"PDPA rejected by {customer.name} for contest {contest.name}")
                
                return {
                    'action': 'advanced',
                    'step': 'pdpa_rejected',
                    'flow_id': str(flow_state.flow_id)
                }
            
            else:
                # Unclear response, ask for clarification
                clarification = "🤔 We didn't understand your response.\n\n"
                clarification += "Please reply with:\n"
                clarification += "✅ 'I agree' - to agree and participate\n"
                clarification += "❌ 'No' - to decline"
                self._send_message_to_customer(tenant, customer, clarification, contest=contest, conversation=conversation)
                
                return {
                    'action': 'clarification',
                    'step': 'pdpa_clarification',
                    'flow_id': str(flow_state.flow_id)
                }
                
        except Exception as e:
            logger.error(f"Error handling PDPA response: {str(e)}")
            raise
    
    def _handle_nric_submission(self, flow_state, customer, message_text, tenant, contest, conversation):
        """
        Handle required details in sequence:
        - name
        - email
        - nric (if contest.requires_nric)
        Then finish the entry (receipt was submitted earlier in receipt-first flow).
        """
        try:
            # Ensure entry exists (we store collected details on ContestEntry)
            entry, _ = ContestEntry.objects.get_or_create(
                tenant=tenant,
                contest=contest,
                customer=customer,
                defaults={
                    'conversation': conversation,
                    'status': 'pending',
                    'contestant_phone': customer.phone_number,
                }
            )

            flow_state.metadata = flow_state.metadata or {}
            details_step = flow_state.metadata.get('details_step') or 'name'

            text = (message_text or "").strip()

            # Step: name
            if details_step == 'name':
                if len(text) < 2:
                    self._send_message_to_customer(tenant, customer, "Please reply with your **full name** (at least 2 characters).")
                    return {'action': 'waiting', 'step': 'awaiting_name', 'flow_id': str(flow_state.flow_id)}

                entry.contestant_name = text
                entry.save(update_fields=['contestant_name'])

                # Also update customer display name (so all future messages look nice)
                try:
                    customer.name = text
                    customer.save(update_fields=['name'])
                except Exception:
                    pass

                flow_state.metadata['details_step'] = 'email'
                flow_state.save()

                self._send_message_to_customer(tenant, customer, f"Thanks, {text}! Now please reply with your **email address**.", contest=contest, conversation=conversation)
                return {'action': 'advanced', 'step': 'awaiting_email', 'flow_id': str(flow_state.flow_id)}

            # Step: email
            if details_step == 'email':
                email = text.lower()
                # simple email validation
                if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                    self._send_message_to_customer(tenant, customer, "That doesn’t look like a valid email. Please reply with a valid email (e.g., name@example.com).", contest=contest, conversation=conversation)
                    return {'action': 'waiting', 'step': 'awaiting_email', 'flow_id': str(flow_state.flow_id)}

                entry.contestant_email = email
                entry.save(update_fields=['contestant_email'])

                if contest.requires_nric:
                    flow_state.metadata['details_step'] = 'nric'
                    flow_state.save()
                    self._send_message_to_customer(tenant, customer, "Great. Finally, please reply with your **IC/NRIC** (e.g., 901231-01-1234).", contest=contest, conversation=conversation)
                    return {'action': 'advanced', 'step': 'awaiting_nric', 'flow_id': str(flow_state.flow_id)}

                # If NRIC not required, go straight to receipt
                flow_state.metadata['details_step'] = 'done'
                flow_state.save()

            # Step: nric
            if (details_step == 'nric') or (details_step == 'done' and contest.requires_nric):
                digits = re.sub(r"\D", "", text)
                if len(digits) != 12:
                    self._send_message_to_customer(tenant, customer, "❌ Sorry, I couldn't process your IC/NRIC. Please send 12 digits (e.g., 901231011234) or with dashes (e.g., 901231-01-1234).")
                    return {'action': 'waiting', 'step': 'awaiting_nric', 'flow_id': str(flow_state.flow_id)}

                nric = f"{digits[:6]}-{digits[6:8]}-{digits[8:]}"
                entry.contestant_nric = nric
                entry.save(update_fields=['contestant_nric'])

                flow_state.metadata['details_step'] = 'done'
                flow_state.save()

            # All details collected - show receipt result AND confirm entry
            # Get receipt details from metadata
            ocr_result = (flow_state.metadata or {}).get('ocr_result', {})
            receipt_status = (flow_state.metadata or {}).get('receipt_status', 'unknown')
            receipt_msg = ocr_result.get('formatted_message', '')
            
            # Build final acknowledgment message
            final_msg = ""
            
            # Show receipt details or flagged message based on status
            if receipt_status == 'valid' and receipt_msg:
                # Valid receipt - show details
                final_msg += f"{receipt_msg}\n\n"
            elif receipt_status in ['invalid', 'failed']:
                # Invalid receipt - show flagged message
                final_msg += "⚠️ Your receipt has been flagged for manual review.\n\n"
                final_msg += "Our team will review your submission and get back to you if any additional information is needed.\n\n"
            else:
                # Fallback receipt acknowledgment
                final_msg += "✅ Your receipt has been processed successfully.\n\n"
            
            # Show collected details
            final_msg += "📋 Your Entry Details:\n"
            final_msg += f"👤 Name: {entry.contestant_name or 'N/A'}\n"
            final_msg += f"📧 Email: {entry.contestant_email or 'N/A'}\n"
            if entry.contestant_nric:
                final_msg += f"🆔 IC/NRIC: {entry.contestant_nric}\n"
            
            # Add entry confirmation
            entry_number = str(entry.entry_id)[:8].upper()
            final_msg += f"\n🎉 Congratulations! You have been entered into the contest!\n\n"
            final_msg += f"🎫 Entry Number: {entry_number}\n\n"
            final_msg += "Your contest entry has been successfully registered. "
            final_msg += "We'll contact you on WhatsApp if you're selected as a winner.\n\n"
            final_msg += "Good luck! 🍀"
            
            self._send_message_to_customer(tenant, customer, final_msg, contest=contest, conversation=conversation)
            
            # Mark flow as completed
            flow_state.advance_step('completed')
            flow_state.completed_at = timezone.now()
            flow_state.save()
            flow_state.add_message_sent('final_entry_confirmed', 'Final entry confirmation with receipt details sent')
            
            # Mark entry as submitted
            entry.status = 'submitted'
            entry.submitted_at = timezone.now()
            entry.save(update_fields=['status', 'submitted_at'])

            logger.info(f"Entry completed for {customer.name} in contest {contest.name}")
            return {'action': 'completed', 'step': 'entry_confirmed', 'flow_id': str(flow_state.flow_id), 'entry_id': str(entry.entry_id)}
            
        except Exception as e:
            logger.error(f"Error handling NRIC submission: {str(e)}")
            raise
    
    def _handle_details_confirmation(self, flow_state, customer, message_text, tenant, contest, conversation):
        """This method is no longer used - details are confirmed automatically after collection"""
        # This step is now handled directly in _handle_nric_submission
        return {'action': 'ignored', 'reason': 'deprecated_method'}
    
    def _handle_receipt_submission(self, flow_state, customer, message_text, tenant, contest, conversation, media_url=None, media_type=None, media_meta=None):
        """Handle receipt submission with OCR processing"""
        try:
            # Import OCR service
            from .receipt_ocr_service import ReceiptOCRService
            from .models import ContestEntry
            
            # Get receipt image URL - prefer media_url from webhook, fallback to conversation history
            receipt_image_url = media_url if media_type == 'image' else None
            
            if not receipt_image_url:
                # Try getting from conversation (legacy fallback)
                receipt_image_url = self._get_latest_image_from_conversation(conversation)
            
            if not receipt_image_url:
                # No image found, send reminder
                reminder = "⚠️ Please upload your receipt image.\n\n"
                reminder += "Make sure to send the image as a photo (not document)."
                self._send_message_to_customer(tenant, customer, reminder, contest=contest, conversation=conversation)
                return {
                    'action': 'waiting',
                    'step': 'awaiting_receipt',
                    'flow_id': str(flow_state.flow_id)
                }

            # Processing happens silently - no notification message sent
            
            # Process receipt with OCR
            ocr_service = ReceiptOCRService()
            ocr_result = ocr_service.process_receipt_image(
                image_url=receipt_image_url,
                media_meta=media_meta or {},
                fallback_city=customer.city if hasattr(customer, 'city') else None,
                fallback_state=customer.state if hasattr(customer, 'state') else None
            )

            ocr_success = bool(ocr_result.get('success'))
            validity = (ocr_result.get('validity') or '').upper()
            is_valid = (validity == 'VALID')

            # If OCR fully failed, log internally but proceed with PDPA (mark as under_review for manual check)
            if not ocr_success:
                logger.warning(f"OCR failed for {customer.phone_number}: {ocr_result.get('error')}")
                # Create entry marked as under_review (admin will check it manually)
                entry, _ = ContestEntry.objects.update_or_create(
                    tenant=tenant,
                    contest=contest,
                    customer=customer,
                    defaults={
                        'conversation': conversation,
                        'status': 'under_review',
                        'contestant_name': customer.name,
                        'contestant_phone': customer.phone_number,
                        'receipt_image_url': receipt_image_url,
                        'rejection_reason': f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}"[:500],
                        'submitted_at': timezone.now(),
                    }
                )
                # Don't send error to user — will show "flagged for manual review" at the end
            elif not is_valid:
                reason = (
                    ocr_result.get('reason')
                    or ocr_result.get('error')
                    or 'Receipt could not be fully verified automatically'
                )

                # Create or update entry (unique_together on contest+customer)
                entry, _ = ContestEntry.objects.update_or_create(
                    tenant=tenant,
                    contest=contest,
                    customer=customer,
                    defaults={
                        'conversation': conversation,
                        'status': 'under_review',
                        'is_verified': False,
                        'contestant_name': customer.name,
                        'contestant_phone': customer.phone_number,
                        'receipt_image_url': receipt_image_url,
                        # store what we know (if any)
                        'store_name': ocr_result.get('store_name'),
                        'store_location': ocr_result.get('store_location'),
                        'rejection_reason': str(reason)[:500],
                        'submitted_at': timezone.now(),
                    }
                )
                # Don't send error message immediately - will show "flagged for manual review" at the end

            # Otherwise, OCR is VALID: proceed as normal submission
            elif is_valid:
                entry, _ = ContestEntry.objects.update_or_create(
                    tenant=tenant,
                    contest=contest,
                    customer=customer,
                    defaults={
                        'conversation': conversation,
                        'status': 'submitted',
                        'contestant_name': customer.name,
                        'contestant_phone': customer.phone_number,
                        'receipt_image_url': receipt_image_url,
                        'submitted_at': timezone.now(),
                    }
                )

                # Save OCR data to entry (includes setting rejected/verified based on validity)
                ocr_service.save_to_contest_entry(entry, ocr_result)

                # Don't send OCR result message immediately - will show in final message

            # Store OCR result in metadata for later display (after PDPA acceptance)
            try:
                flow_state.metadata = flow_state.metadata or {}
                flow_state.metadata["receipt_done"] = True
                flow_state.metadata["receipt_status"] = 'valid' if is_valid else ('failed' if not ocr_success else 'invalid')
                flow_state.metadata["ocr_result"] = {
                    'store_name': ocr_result.get('store_name', 'N/A'),
                    'store_location': ocr_result.get('store_location', 'N/A'),
                    'receipt_amount': str(ocr_result.get('receipt_amount', 'N/A')),
                    'products_purchased': ocr_result.get('products_purchased', []),
                    'formatted_message': ocr_result.get('formatted_message', ''),
                    'validity': validity,
                    'is_valid': is_valid,
                    'ocr_success': ocr_success,
                }
                flow_state.save(update_fields=["metadata"])
            except Exception:
                pass

            # Send PDPA message first (receipt details will be shown after they agree)
            pdpa_msg = contest.pdpa_message or (
                "Before we continue, we need your consent to collect and process your personal data.\n\n"
                "Please read our privacy policy here:\n"
                "https://khind.com.my/pages/privacy-policy\n\n"
                "Reply **I agree** to continue, or **No** to opt out."
            )
            if contest.pdpa_message:
                pdpa_msg = (
                    "Before we continue, please review our privacy policy and consent below.\n\n"
                    + contest.pdpa_message
                )
            self._send_message_to_customer(tenant, customer, pdpa_msg, contest=contest, conversation=conversation)
            flow_state.advance_step('pdpa_response')
            flow_state.add_message_sent('pdpa_after_receipt', 'PDPA message sent after receipt')

            return {'action': 'advanced', 'step': 'pdpa_sent', 'flow_id': str(flow_state.flow_id), 'ocr_result': ocr_result}
            
        except Exception as e:
            logger.error(f"Error handling receipt submission: {str(e)}", exc_info=True)
            raise
    
    def _is_consent_yes(self, message_lower):
        """Check if message indicates consent"""
        yes_responses = [
            'yes', 'ya', 'ok', 'okay', 'agree', 'accept', 'consent', 'terima',
            'setuju', 'baik', 'yes i agree', 'i agree', 'i accept'
        ]
        return any(response in message_lower for response in yes_responses)
    
    def _is_consent_no(self, message_lower):
        """Check if message indicates no consent"""
        no_responses = [
            'no', 'tidak', 'reject', 'decline', 'not agree', 'don\'t agree',
            'tidak setuju', 'tidak terima'
        ]
        return any(response in message_lower for response in no_responses)
    
    def _is_opt_out_message(self, message_lower):
        """Check if message is opt-out"""
        opt_out_responses = [
            'stop', 'unsubscribe', 'opt out', 'berhenti', 'stop sending',
            'don\'t send', 'tidak mahu'
        ]
        return any(response in message_lower for response in opt_out_responses)
    
    def _send_pdpa_message(self, customer, tenant, contest):
        """Send PDPA consent message using contest form fields"""
        try:
            # Use post_pdpa_text from contest form, or default message
            if contest.post_pdpa_text:
                message = contest.post_pdpa_text
            else:
                message = f"🎉 Welcome to {contest.name}!\n\n"
                message += "To participate in this contest, we need your consent to process your personal data.\n\n"
                message += "Please reply with:\n"
                message += "✅ YES - to agree and participate\n"
                message += "❌ NO - to decline\n"
                message += "🛑 STOP - to opt out of future messages\n\n"
                message += "Thank you!"
            
            self._send_message_to_customer(tenant, customer, message)
            
            # Send additional content if available
            if contest.post_pdpa_image_url:
                self._send_media_message(customer, tenant, contest.post_pdpa_image_url, "Contest Information")
            
            if contest.post_pdpa_gif_url:
                self._send_media_message(customer, tenant, contest.post_pdpa_gif_url, "Contest Animation")
                
        except Exception as e:
            logger.error(f"Error sending PDPA message: {str(e)}")
    
    def _send_pdpa_acceptance_response(self, customer, tenant, contest):
        """Send response for PDPA acceptance"""
        try:
            message = "✅ Thank you for your consent!\n\n"
            message += "You have successfully agreed to participate in our contest.\n"
            message += "We will now send you the contest instructions."
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending PDPA acceptance response: {str(e)}")
    
    def _send_pdpa_rejection_response(self, customer, tenant, contest):
        """Send response for PDPA rejection"""
        try:
            message = "❌ We understand your decision.\n\n"
            message += "You have chosen not to participate in this contest.\n"
            message += "If you change your mind, feel free to contact us again.\n\n"
            message += "Thank you for your time!"
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending PDPA rejection response: {str(e)}")
    
    def _send_pdpa_clarification(self, customer, tenant, contest):
        """Send clarification message for unclear PDPA response"""
        try:
            message = "🤔 We didn't understand your response.\n\n"
            message += "Please reply with:\n"
            message += "✅ YES - to agree and participate\n"
            message += "❌ NO - to decline\n"
            message += "🛑 STOP - to opt out of future messages"
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending PDPA clarification: {str(e)}")
    
    def _send_contest_instructions(self, customer, tenant, contest):
        """Send contest instructions using contest form fields"""
        try:
            # Use contest_instructions from contest form
            if contest.contest_instructions:
                message = f"📋 Contest Instructions for {contest.name}\n\n"
                message += contest.contest_instructions
            else:
                message = f"📋 How to participate in {contest.name}:\n\n"
                message += "1. Follow the contest requirements\n"
                message += "2. Submit your entry as instructed\n"
                message += "3. Wait for verification\n\n"
                message += "Good luck! 🍀"
            
            # Add eligibility message if available
            if contest.eligibility_message:
                message += f"\n\n✅ {contest.eligibility_message}"
            
            # Add requirements if any
            requirements = []
            if contest.requires_nric:
                requirements.append("📄 NRIC submission required")
            if contest.requires_receipt:
                requirements.append("🧾 Receipt submission required")
            if contest.min_purchase_amount:
                requirements.append(f"💰 Minimum purchase: RM{contest.min_purchase_amount}")
            
            if requirements:
                message += f"\n\n📋 Requirements:\n" + "\n".join(requirements)
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending contest instructions: {str(e)}")
    
    def _send_submission_acknowledgment(self, customer, tenant, contest):
        """Send acknowledgment for contest submission"""
        try:
            message = f"✅ Thank you for your submission!\n\n"
            message += f"Your entry for '{contest.name}' has been received.\n"
            message += "We will review your submission and notify you of the results.\n\n"
            message += "Good luck! 🍀"
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending submission acknowledgment: {str(e)}")
    
    def _get_latest_image_from_conversation(self, conversation):
        """Get the most recent image URL from conversation messages"""
        try:
            if not conversation:
                return None
            
            # Get recent messages with attachments
            from .models import CoreMessage, MessageAttachment
            
            recent_messages = CoreMessage.objects.filter(
                conversation=conversation,
                direction='inbound'
            ).order_by('-created_at')[:10]
            
            # Look for image attachments
            for msg in recent_messages:
                # Model uses `kind` and `storage_path`
                attachments = MessageAttachment.objects.filter(message=msg, kind='image')
                if attachments.exists():
                    attachment = attachments.first()
                    if getattr(attachment, 'storage_path', None):
                        return str(attachment.storage_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest image: {e}")
            return None
    
    def _send_message_to_customer(self, tenant, customer, message_text, contest=None, conversation=None):
        """Send text message to customer"""
        try:
            result = self.wa_service.send_text_message(customer.phone_number, message_text)
            
            if result['success']:
                # Create message record
                self._create_message_record(tenant, customer, message_text, 'outbound', 'sent', contest=contest, conversation=conversation)
                logger.info(f"Sent message to {customer.name}")
            else:
                logger.error(f"Failed to send message to {customer.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending message to customer: {str(e)}")
    
    def _send_media_message(self, customer, tenant, media_url, caption="", contest=None, conversation=None):
        """Send media message to customer"""
        try:
            result = self.wa_service.send_media_message(customer.phone_number, caption, media_url)
            
            if result['success']:
                # Create message record
                self._create_message_record(tenant, customer, f"{caption} [Media]", 'outbound', 'sent', contest=contest, conversation=conversation)
                logger.info(f"Sent media message to {customer.name}")
            else:
                logger.error(f"Failed to send media to {customer.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending media message: {str(e)}")
    
    def _create_message_record(self, tenant, customer, message_text, direction, status, contest=None, conversation=None):
        """Create message record in database"""
        try:
            # Prefer provided conversation
            conv = conversation

            # Otherwise, get or create conversation
            if conv is None:
                conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
                if conn:
                    conv, _ = Conversation.objects.get_or_create(
                        tenant=tenant,
                        customer=customer,
                        whatsapp_connection=conn,
                        defaults={'contest': contest} if contest else {}
                    )

            # Ensure conversation is linked to contest (Participants Manager chat history uses conversation.contest)
            if contest and conv and getattr(conv, 'contest_id', None) is None:
                try:
                    conv.contest = contest
                    conv.save(update_fields=['contest'])
                except Exception:
                    pass
            
            # Create message record
            from .models import CoreMessage
            CoreMessage.objects.create(
                tenant=tenant,
                conversation=conv,
                direction=direction,
                status=status,
                text_body=message_text,
                created_at=timezone.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating message record: {str(e)}")
    
    def get_flow_stats(self, tenant):
        """Get statistics about contest flows"""
        try:
            now = timezone.now()
            
            # Get active contests
            active_contests = Contest.objects.filter(
                tenant=tenant,
                is_active=True,
                starts_at__lte=now,
                ends_at__gte=now
            )
            
            # Get flow statistics
            total_flows = ContestFlowState.objects.filter(contest__in=active_contests).count()
            
            # Get flows by step
            step_stats = {}
            for step, _ in ContestFlowState.FLOW_STEPS:
                count = ContestFlowState.objects.filter(
                    contest__in=active_contests,
                    current_step=step
                ).count()
                step_stats[step] = count
            
            # Get PDPA response stats
            pdpa_stats = {
                'accepted': ContestFlowState.objects.filter(
                    contest__in=active_contests,
                    pdpa_response='yes'
                ).count(),
                'rejected': ContestFlowState.objects.filter(
                    contest__in=active_contests,
                    pdpa_response='no'
                ).count(),
                'stopped': ContestFlowState.objects.filter(
                    contest__in=active_contests,
                    pdpa_response='stop'
                ).count(),
            }
            
            return {
                'active_contests': active_contests.count(),
                'total_flows': total_flows,
                'step_breakdown': step_stats,
                'pdpa_responses': pdpa_stats,
                'contests': [
                    {
                        'name': contest.name,
                        'flows': ContestFlowState.objects.filter(contest=contest).count(),
                        'completed': ContestFlowState.objects.filter(contest=contest, current_step='completed').count(),
                        'starts_at': contest.starts_at,
                        'ends_at': contest.ends_at
                    }
                    for contest in active_contests
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting flow stats: {str(e)}")
            return {
                'active_contests': 0,
                'total_flows': 0,
                'step_breakdown': {},
                'pdpa_responses': {},
                'contests': []
            }
