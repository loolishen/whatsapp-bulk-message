"""
Background tasks for WhatsApp Blasting
Can be integrated with Celery or run synchronously for now
"""
import time
import logging
from django.utils import timezone as dj_timezone
from .models import BlastCampaign, BlastRecipient, Conversation, CoreMessage
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)

def send_blast_campaign_task(campaign_id):
    """
    Background task to send blast campaign messages
    Can be called synchronously or via Celery
    """
    try:
        campaign = BlastCampaign.objects.get(blast_id=campaign_id)
        
        # Initialize WhatsApp service
        wa_service = WhatsAppAPIService()
        
        # Get recipients
        recipients = BlastRecipient.objects.filter(
            blast_campaign=campaign, 
            status='pending'
        ).select_related('customer')
        
        sent_count = 0
        failed_count = 0
        
        # Send messages to each recipient
        for recipient in recipients:
            try:
                # Update status to queued
                recipient.status = 'queued'
                recipient.save()
                
                # Send message via WABot
                if campaign.message_image_url:
                    # Send media message
                    result = wa_service.send_media_message(
                        number=recipient.customer.phone_number,
                        message=campaign.message_text,
                        media_url=campaign.message_image_url
                    )
                else:
                    # Send text message
                    result = wa_service.send_text_message(
                        number=recipient.customer.phone_number,
                        message=campaign.message_text
                    )
                
                if result.get('success'):
                    # Update recipient status to sent
                    recipient.status = 'sent'
                    recipient.sent_at = dj_timezone.now()
                    recipient.save()
                    sent_count += 1
                    
                    # Create conversation and message record
                    conn = campaign.whatsapp_connection
                    convo, _ = Conversation.objects.get_or_create(
                        tenant=campaign.tenant,
                        customer=recipient.customer,
                        whatsapp_connection=conn,
                        defaults={'channel': 'whatsapp'}
                    )
                    
                    # Update last message time
                    convo.last_message_at = dj_timezone.now()
                    convo.save()
                    
                    # Create message record
                    msg = CoreMessage.objects.create(
                        tenant=campaign.tenant,
                        conversation=convo,
                        direction='outbound',
                        status='sent',
                        text_body=campaign.message_text,
                        sent_at=dj_timezone.now()
                    )
                    
                    # Link message to recipient
                    recipient.message = msg
                    recipient.save()
                    
                    logger.info(f"Successfully sent blast message to {recipient.customer.phone_number}")
                else:
                    # Mark as failed
                    recipient.status = 'failed'
                    recipient.error_message = result.get('error', 'Unknown error')
                    recipient.save()
                    failed_count += 1
                    logger.error(f"Failed to send blast message to {recipient.customer.phone_number}: {result.get('error')}")
                
                # Update campaign statistics in real-time
                campaign.sent_count = sent_count
                campaign.failed_count = failed_count
                campaign.delivered_count = sent_count
                campaign.save()
                
                # Rate limiting: small delay between messages
                time.sleep(0.5)  # 0.5 second delay
                
            except Exception as e:
                # Mark as failed
                recipient.status = 'failed'
                recipient.error_message = str(e)
                recipient.save()
                failed_count += 1
                logger.error(f"Error sending blast message to {recipient.customer.phone_number}: {str(e)}")
        
        # Update final campaign statistics
        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.delivered_count = sent_count
        
        # Update campaign status
        if failed_count == 0:
            campaign.status = 'completed'
        elif sent_count == 0:
            campaign.status = 'failed'
        else:
            campaign.status = 'completed'  # Partial success
        
        campaign.completed_at = dj_timezone.now()
        campaign.save()
        
        logger.info(f"Blast campaign {campaign_id} completed: {sent_count} sent, {failed_count} failed")
        
        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in send_blast_campaign_task: {str(e)}")
        try:
            campaign = BlastCampaign.objects.get(blast_id=campaign_id)
            campaign.status = 'failed'
            campaign.save()
        except:
            pass
        return {
            'success': False,
            'error': str(e)
        }

