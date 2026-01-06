"""
Conversation Flow Service
Handles multi-step conversation logic for contests
"""
import logging
from typing import Optional, Dict, Any
from .models import (
    Contest, ContestConversationStep, UserConversationProgress,
    Customer, Tenant, Conversation
)
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)


class ConversationFlowService:
    """
    Service to manage multi-step conversation flows for contests.
    """
    
    def __init__(self):
        pass
    
    def process_message(
        self, 
        customer: Customer, 
        message_text: str, 
        tenant: Tenant,
        conversation: Optional[Conversation] = None
    ) -> Dict[str, Any]:
        """
        Process a message and advance the conversation flow if applicable.
        
        Returns:
            {
                'matched': bool,  # Whether any conversation step matched
                'contest': Contest or None,  # The contest that matched
                'step': ContestConversationStep or None,  # The step that matched
                'reply_message': str or None,  # The reply to send
                'advanced': bool,  # Whether the user was advanced to next step
                'completed': bool  # Whether the conversation is completed
            }
        """
        result = {
            'matched': False,
            'contest': None,
            'step': None,
            'reply_message': None,
            'advanced': False,
            'completed': False
        }
        
        if not message_text:
            return result
        
        # Get all active contests for this tenant with conversation steps
        active_contests = Contest.objects.filter(
            tenant=tenant,
            is_active=True
        ).prefetch_related('conversation_steps').order_by('-auto_reply_priority')
        
        for contest in active_contests:
            # Skip contests without conversation steps
            if not contest.conversation_steps.exists():
                continue
            
            # Get or create user progress for this contest
            user_progress, created = UserConversationProgress.objects.get_or_create(
                customer=customer,
                contest=contest,
                defaults={
                    'started_at': dj_timezone.now(),
                    'completed': False
                }
            )
            
            # If conversation is completed, skip
            if user_progress.completed:
                continue
            
            # If user hasn't started, check if message matches step 1
            if not user_progress.current_step:
                first_step = contest.conversation_steps.filter(step_order=1).first()
                if first_step and first_step.matches_message(message_text):
                    # User started the conversation!
                    result['matched'] = True
                    result['contest'] = contest
                    result['step'] = first_step
                    result['reply_message'] = first_step.auto_reply_message
                    
                    # Advance to step 2 (or mark as completed if only 1 step)
                    if first_step.auto_advance_to_next:
                        next_step = user_progress.advance_to_next_step()
                        result['advanced'] = True
                        result['completed'] = next_step is None
                    
                    logger.info(
                        f"Customer {customer.name} started conversation with contest "
                        f"{contest.name} at step 1"
                    )
                    return result
            
            # User is in middle of conversation - check current step
            elif user_progress.current_step:
                current_step = user_progress.current_step
                
                # Check if message matches current step's keywords
                if current_step.matches_message(message_text):
                    result['matched'] = True
                    result['contest'] = contest
                    result['step'] = current_step
                    result['reply_message'] = current_step.auto_reply_message
                    
                    # Advance to next step if configured
                    if current_step.auto_advance_to_next:
                        next_step = user_progress.advance_to_next_step()
                        result['advanced'] = True
                        result['completed'] = next_step is None
                        
                        if next_step:
                            logger.info(
                                f"Customer {customer.name} advanced to step "
                                f"{next_step.step_order} in contest {contest.name}"
                            )
                        else:
                            logger.info(
                                f"Customer {customer.name} completed conversation "
                                f"flow for contest {contest.name}"
                            )
                    
                    return result
        
        return result
    
    def reset_conversation(
        self,
        customer: Customer,
        contest: Contest
    ) -> bool:
        """
        Reset a user's conversation progress for a specific contest.
        
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            user_progress = UserConversationProgress.objects.get(
                customer=customer,
                contest=contest
            )
            user_progress.reset_progress()
            logger.info(
                f"Reset conversation progress for {customer.name} in contest {contest.name}"
            )
            return True
        except UserConversationProgress.DoesNotExist:
            logger.warning(
                f"No conversation progress found for {customer.name} in contest {contest.name}"
            )
            return False
    
    def get_conversation_status(
        self,
        customer: Customer,
        contest: Contest
    ) -> Dict[str, Any]:
        """
        Get the current status of a user's conversation in a contest.
        
        Returns:
            {
                'started': bool,
                'current_step': int or None,
                'current_step_name': str or None,
                'completed': bool,
                'total_steps': int,
                'progress_percentage': float
            }
        """
        try:
            user_progress = UserConversationProgress.objects.get(
                customer=customer,
                contest=contest
            )
            
            total_steps = contest.conversation_steps.count()
            current_step_order = user_progress.current_step.step_order if user_progress.current_step else 0
            
            return {
                'started': True,
                'current_step': current_step_order,
                'current_step_name': user_progress.current_step.step_name if user_progress.current_step else None,
                'completed': user_progress.completed,
                'total_steps': total_steps,
                'progress_percentage': (current_step_order / total_steps * 100) if total_steps > 0 else 0
            }
        except UserConversationProgress.DoesNotExist:
            return {
                'started': False,
                'current_step': None,
                'current_step_name': None,
                'completed': False,
                'total_steps': contest.conversation_steps.count(),
                'progress_percentage': 0
            }

