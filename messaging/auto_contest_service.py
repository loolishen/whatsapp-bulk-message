"""
Automatic Contest Entry Service

This service automatically adds contestants to contests based on message timing.
When a customer sends a message during an active contest period, they are automatically
added as a contestant to that contest.
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import Contest, ContestEntry, Customer, Tenant, Conversation, WhatsAppConnection
from .contest_flow_models import ContestFlowState
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)

class AutoContestService:
    """
    Service to automatically add contestants to contests based on message timing
    """
    
    def __init__(self):
        self.wa_service = WhatsAppAPIService()
    
    def process_message_for_contests(self, customer, message_text, tenant, conversation=None):
        """
        Process incoming message and automatically add customer to active contests
        
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
                'contests_added': 0,
                'contests_updated': 0,
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
                    result = self._process_contest_for_customer(
                        customer, message_text, tenant, contest, conversation
                    )
                    
                    if result['action'] == 'created':
                        results['contests_added'] += 1
                    elif result['action'] == 'updated':
                        results['contests_updated'] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing contest {contest.name}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f"Auto contest processing completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in auto contest processing: {str(e)}")
            return {
                'contests_checked': 0,
                'contests_added': 0,
                'contests_updated': 0,
                'errors': [str(e)]
            }
    
    def _get_active_contests(self, tenant):
        """
        Get all currently active contests for a tenant
        
        Args:
            tenant: Tenant object
        
        Returns:
            QuerySet: Active contests
        """
        now = timezone.now()
        
        return Contest.objects.filter(
            tenant=tenant,
            is_active=True,
            starts_at__lte=now,
            ends_at__gte=now
        ).order_by('-created_at')
    
    def _process_contest_for_customer(self, customer, message_text, tenant, contest, conversation=None):
        """
        Process a single contest for a customer
        
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
            # Check if customer already has an entry for this contest
            existing_entry = ContestEntry.objects.filter(
                contest=contest,
                customer=customer
            ).first()
            
            if existing_entry:
                # Update existing entry
                return self._update_existing_entry(
                    existing_entry, customer, message_text, tenant, contest, conversation
                )
            else:
                # Create new entry
                return self._create_new_entry(
                    customer, message_text, tenant, contest, conversation
                )
                
        except Exception as e:
            logger.error(f"Error processing contest {contest.name} for customer {customer.name}: {str(e)}")
            raise
    
    def _create_new_entry(self, customer, message_text, tenant, contest, conversation=None):
        """
        Create a new contest entry for a customer
        
        Args:
            customer: Customer object
            message_text: Message content
            tenant: Tenant object
            contest: Contest object
            conversation: Conversation object (optional)
        
        Returns:
            dict: Creation result
        """
        try:
            with transaction.atomic():
                # Create contest entry
                entry = ContestEntry.objects.create(
                    tenant=tenant,
                    contest=contest,
                    customer=customer,
                    conversation=conversation,
                    status='pending',
                    contestant_name=customer.name,
                    contestant_phone=customer.phone_number,
                    submitted_at=timezone.now()
                )
                
                # Send contest notification message
                self._send_contest_notification(customer, tenant, contest, entry)
                
                logger.info(f"Created contest entry for {customer.name} in contest {contest.name}")
                
                return {
                    'action': 'created',
                    'entry_id': str(entry.entry_id),
                    'contest_name': contest.name,
                    'customer_name': customer.name
                }
                
        except Exception as e:
            logger.error(f"Error creating contest entry: {str(e)}")
            raise
    
    def _update_existing_entry(self, entry, customer, message_text, tenant, contest, conversation=None):
        """
        Update an existing contest entry
        
        Args:
            entry: Existing ContestEntry object
            customer: Customer object
            message_text: Message content
            tenant: Tenant object
            contest: Contest object
            conversation: Conversation object (optional)
        
        Returns:
            dict: Update result
        """
        try:
            # Update entry timestamp
            entry.submitted_at = timezone.now()
            entry.updated_at = timezone.now()
            
            # If entry was rejected, reset to pending
            if entry.status == 'rejected':
                entry.status = 'pending'
                entry.verification_notes = None
            
            entry.save()
            
            # Send update notification
            self._send_contest_update_notification(customer, tenant, contest, entry)
            
            logger.info(f"Updated contest entry for {customer.name} in contest {contest.name}")
            
            return {
                'action': 'updated',
                'entry_id': str(entry.entry_id),
                'contest_name': contest.name,
                'customer_name': customer.name,
                'status': entry.status
            }
            
        except Exception as e:
            logger.error(f"Error updating contest entry: {str(e)}")
            raise
    
    def _send_contest_notification(self, customer, tenant, contest, entry):
        """
        Send notification message to customer about contest entry
        
        Args:
            customer: Customer object
            tenant: Tenant object
            contest: Contest object
            entry: ContestEntry object
        """
        try:
            # Create welcome message
            message = f"🎉 Congratulations {customer.name}!\n\n"
            message += f"You have been automatically entered into our contest:\n"
            message += f"📋 {contest.name}\n\n"
            
            if contest.description:
                message += f"📝 {contest.description}\n\n"
            
            # Add contest instructions if available
            if contest.contest_instructions:
                message += f"📋 Instructions:\n{contest.contest_instructions}\n\n"
            
            # Add eligibility message
            if contest.eligibility_message:
                message += f"✅ {contest.eligibility_message}\n\n"
            
            # Add contest period info
            message += f"⏰ Contest Period:\n"
            message += f"Start: {contest.starts_at.strftime('%Y-%m-%d %H:%M')}\n"
            message += f"End: {contest.ends_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # Add requirements if any
            requirements = []
            if contest.requires_nric:
                requirements.append("📄 NRIC submission")
            if contest.requires_receipt:
                requirements.append("🧾 Receipt submission")
            if contest.min_purchase_amount:
                requirements.append(f"💰 Minimum purchase: RM{contest.min_purchase_amount}")
            
            if requirements:
                message += f"📋 Requirements:\n" + "\n".join(requirements) + "\n\n"
            
            message += "Good luck! 🍀"
            
            # Send message
            self._send_message_to_customer(tenant, customer, message)
            
            # Send custom post-PDPA content if available
            self._send_contest_custom_content(customer, tenant, contest)
            
        except Exception as e:
            logger.error(f"Error sending contest notification: {str(e)}")
    
    def _send_contest_update_notification(self, customer, tenant, contest, entry):
        """
        Send update notification for existing contest entry
        
        Args:
            customer: Customer object
            tenant: Tenant object
            contest: Contest object
            entry: ContestEntry object
        """
        try:
            message = f"🔄 Contest Update\n\n"
            message += f"Your entry in '{contest.name}' has been updated.\n\n"
            message += f"Status: {entry.get_status_display()}\n"
            message += f"Updated: {entry.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            if entry.status == 'pending':
                message += "Your entry is pending review. We'll notify you once it's processed.\n\n"
            elif entry.status == 'verified':
                message += "✅ Your entry has been verified! You're officially in the contest.\n\n"
            elif entry.status == 'rejected':
                message += "❌ Your entry was rejected. Please check the requirements and try again.\n\n"
            
            message += "Thank you for participating! 🎉"
            
            self._send_message_to_customer(tenant, customer, message)
            
        except Exception as e:
            logger.error(f"Error sending contest update notification: {str(e)}")
    
    def _send_contest_custom_content(self, customer, tenant, contest):
        """
        Send custom contest content (images, GIFs, etc.)
        
        Args:
            customer: Customer object
            tenant: Tenant object
            contest: Contest object
        """
        try:
            # Send custom text if available
            if contest.post_pdpa_text:
                self._send_message_to_customer(tenant, customer, contest.post_pdpa_text)
            
            # Send custom image if available
            if contest.post_pdpa_image_url:
                self._send_media_message(customer, tenant, contest.post_pdpa_image_url, "Contest Information")
            
            # Send custom GIF if available
            if contest.post_pdpa_gif_url:
                self._send_media_message(customer, tenant, contest.post_pdpa_gif_url, "Contest Animation")
                
        except Exception as e:
            logger.error(f"Error sending contest custom content: {str(e)}")
    
    def _send_message_to_customer(self, tenant, customer, message_text):
        """
        Send text message to customer
        
        Args:
            tenant: Tenant object
            customer: Customer object
            message_text: Message content
        """
        try:
            result = self.wa_service.send_text_message(customer.phone_number, message_text)
            
            if result['success']:
                # Create message record
                self._create_message_record(tenant, customer, message_text, 'outbound', 'sent')
                logger.info(f"Sent contest message to {customer.name}")
            else:
                logger.error(f"Failed to send message to {customer.name}: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error sending message to customer: {str(e)}")
    
    def _send_media_message(self, customer, tenant, media_url, caption=""):
        """
        Send media message to customer
        
        Args:
            customer: Customer object
            tenant: Tenant object
            media_url: Media URL
            caption: Media caption
        """
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
        """
        Create message record in database
        
        Args:
            tenant: Tenant object
            customer: Customer object
            message_text: Message content
            direction: 'inbound' or 'outbound'
            status: Message status
        """
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
    
    def get_contest_stats(self, tenant):
        """
        Get statistics about auto contest processing
        
        Args:
            tenant: Tenant object
        
        Returns:
            dict: Contest statistics
        """
        try:
            now = timezone.now()
            
            # Get active contests
            active_contests = Contest.objects.filter(
                tenant=tenant,
                is_active=True,
                starts_at__lte=now,
                ends_at__gte=now
            )
            
            # Get total entries from auto processing
            total_entries = ContestEntry.objects.filter(
                tenant=tenant,
                contest__in=active_contests
            ).count()
            
            # Get entries by status
            status_stats = {}
            for status, _ in ContestEntry.STATUS_CHOICES:
                count = ContestEntry.objects.filter(
                    tenant=tenant,
                    contest__in=active_contests,
                    status=status
                ).count()
                status_stats[status] = count
            
            return {
                'active_contests': active_contests.count(),
                'total_entries': total_entries,
                'status_breakdown': status_stats,
                'contests': [
                    {
                        'name': contest.name,
                        'entries': contest.total_entries,
                        'verified': contest.verified_entries,
                        'starts_at': contest.starts_at,
                        'ends_at': contest.ends_at
                    }
                    for contest in active_contests
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting contest stats: {str(e)}")
            return {
                'active_contests': 0,
                'total_entries': 0,
                'status_breakdown': {},
                'contests': []
            }
