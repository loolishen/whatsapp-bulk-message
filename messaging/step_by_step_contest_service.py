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
from .models import Contest, ContestEntry, Customer, Tenant, Conversation, WhatsAppConnection, ContestFlowState
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)

class StepByStepContestService:
    """
    Service to handle step-by-step contest flow with dynamic prompts from contest form
    """
    
    def __init__(self):
        self.wa_service = WhatsAppAPIService()
    
    def process_message_for_contests(self, customer, message_text, tenant, conversation=None):
        """
        Process incoming message and handle step-by-step contest flow
        
        Args:
            customer: Customer object who sent the message
            message_text: The message content
            tenant: Tenant object
            conversation: Conversation object (optional)
        
        Returns:
            dict: Results of contest processing
        """
        try:
            results = {
                'contests_checked': 0,
                'flows_processed': 0,
                'flows_created': 0,
                'flows_advanced': 0,
                'errors': []
            }
            
            # Get all active contests for this tenant
            active_contests = self._get_active_contests(tenant)
            results['contests_checked'] = len(active_contests)
            
            if not active_contests:
                logger.info(f"No active contests found for tenant {tenant.name}")
                return results
            
            # Process each active contest
            for contest in active_contests:
                try:
                    result = self._process_contest_flow(
                        customer, message_text, tenant, contest, conversation
                    )
                    
                    if result['action'] == 'created':
                        results['flows_created'] += 1
                    elif result['action'] == 'advanced':
                        results['flows_advanced'] += 1
                    
                    results['flows_processed'] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing contest {contest.name}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f"Step-by-step contest processing completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in step-by-step contest processing: {str(e)}")
            return {
                'contests_checked': 0,
                'flows_processed': 0,
                'flows_created': 0,
                'flows_advanced': 0,
                'errors': [str(e)]
            }
    
    def _get_active_contests(self, tenant):
        """Get all currently active contests for a tenant"""
        now = timezone.now()
        
        return Contest.objects.filter(
            tenant=tenant,
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        ).order_by('-created_at')
    
    def _process_contest_flow(self, customer, message_text, tenant, contest, conversation=None):
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
                return {'action': 'created', 'flow_id': str(flow_state.flow_id)}
            
            # Process based on current step
            return self._handle_flow_step(flow_state, customer, message_text, tenant, contest, conversation)
                
        except Exception as e:
            logger.error(f"Error processing contest flow: {str(e)}")
            raise
    
    def _handle_flow_step(self, flow_state, customer, message_text, tenant, contest, conversation):
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
            
            # Step 1: Initial contact - look for greeting
            if flow_state.current_step == 'initial':
                if self._is_greeting_message(message_lower):
                    return self._handle_initial_greeting(flow_state, customer, tenant, contest, conversation)
                else:
                    # Not a greeting, don't process
                    return {'action': 'ignored', 'reason': 'not_greeting'}
            
            # Step 2: PDPA response handling
            elif flow_state.current_step == 'pdpa_response':
                return self._handle_pdpa_response(flow_state, customer, message_text, tenant, contest, conversation)
            
            # Step 3: Awaiting submission
            elif flow_state.current_step == 'awaiting_submission':
                return self._handle_submission(flow_state, customer, message_text, tenant, contest, conversation)
            
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
    
    def _handle_initial_greeting(self, flow_state, customer, tenant, contest, conversation):
        """Handle initial greeting - send PDPA message"""
        try:
            # Send PDPA message using contest form fields
            self._send_pdpa_message(customer, tenant, contest)
            
            # Advance to PDPA response step
            flow_state.advance_step('pdpa_response')
            flow_state.add_message_sent('pdpa', 'PDPA consent message sent')
            
            logger.info(f"Sent PDPA message to {customer.name} for contest {contest.name}")
            
            return {
                'action': 'advanced',
                'step': 'pdpa_sent',
                'flow_id': str(flow_state.flow_id)
            }
            
        except Exception as e:
            logger.error(f"Error handling initial greeting: {str(e)}")
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
                
                # Send acceptance response
                self._send_pdpa_acceptance_response(customer, tenant, contest)
                
                # Send contest instructions
                self._send_contest_instructions(customer, tenant, contest)
                
                # Advance to awaiting submission
                flow_state.advance_step('awaiting_submission')
                flow_state.add_message_sent('pdpa_acceptance', 'PDPA acceptance response sent')
                flow_state.add_message_sent('instructions', 'Contest instructions sent')
                
                logger.info(f"PDPA accepted by {customer.name} for contest {contest.name}")
                
                return {
                    'action': 'advanced',
                    'step': 'pdpa_accepted',
                    'flow_id': str(flow_state.flow_id)
                }
            
            elif self._is_consent_no(message_lower) or self._is_opt_out_message(message_lower):
                flow_state.pdpa_response = 'no' if self._is_consent_no(message_lower) else 'stop'
                flow_state.pdpa_responded_at = timezone.now()
                flow_state.save()
                
                # Send rejection response
                self._send_pdpa_rejection_response(customer, tenant, contest)
                
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
                self._send_pdpa_clarification(customer, tenant, contest)
                
                return {
                    'action': 'clarification',
                    'step': 'pdpa_clarification',
                    'flow_id': str(flow_state.flow_id)
                }
                
        except Exception as e:
            logger.error(f"Error handling PDPA response: {str(e)}")
            raise
    
    def _handle_submission(self, flow_state, customer, message_text, tenant, contest, conversation):
        """Handle contest submission (images, documents, etc.)"""
        try:
            # For now, just acknowledge submission
            # In a full implementation, you'd process the submission here
            
            self._send_submission_acknowledgment(customer, tenant, contest)
            
            # Create contest entry
            entry = ContestEntry.objects.create(
                tenant=tenant,
                contest=contest,
                customer=customer,
                conversation=conversation,
                status='submitted',
                contestant_name=customer.name,
                contestant_phone=customer.phone_number,
                submitted_at=timezone.now()
            )
            
            # Advance to completed
            flow_state.advance_step('completed')
            flow_state.add_message_sent('submission_ack', 'Submission acknowledgment sent')
            
            logger.info(f"Contest submission processed for {customer.name} in contest {contest.name}")
            
            return {
                'action': 'advanced',
                'step': 'submitted',
                'entry_id': str(entry.entry_id),
                'flow_id': str(flow_state.flow_id)
            }
            
        except Exception as e:
            logger.error(f"Error handling submission: {str(e)}")
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
    
    def _send_message_to_customer(self, tenant, customer, message_text):
        """Send text message to customer"""
        try:
            result = self.wa_service.send_text_message(customer.phone_number, message_text)
            
            if result['success']:
                # Create message record
                self._create_message_record(tenant, customer, message_text, 'outbound', 'sent')
                logger.info(f"Sent message to {customer.name}")
            else:
                logger.error(f"Failed to send message to {customer.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending message to customer: {str(e)}")
    
    def _send_media_message(self, customer, tenant, media_url, caption=""):
        """Send media message to customer"""
        try:
            result = self.wa_service.send_media_message(customer.phone_number, caption, media_url)
            
            if result['success']:
                # Create message record
                self._create_message_record(tenant, customer, f"{caption} [Media]", 'outbound', 'sent')
                logger.info(f"Sent media message to {customer.name}")
            else:
                logger.error(f"Failed to send media to {customer.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending media message: {str(e)}")
    
    def _create_message_record(self, tenant, customer, message_text, direction, status):
        """Create message record in database"""
        try:
            # Get or create conversation
            conn = WhatsAppConnection.objects.filter(tenant=tenant).first()
            conversation = None
            
            if conn:
                conversation, _ = Conversation.objects.get_or_create(
                    tenant=tenant,
                    customer=customer,
                    whatsapp_connection=conn,
                    defaults={}
                )
            
            # Create message record
            from .models import CoreMessage
            CoreMessage.objects.create(
                tenant=tenant,
                conversation=conversation,
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
