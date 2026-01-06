import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ContestEntry
from .whatsapp_service import WhatsAppAPIService

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ContestEntry)
def _contest_entry_capture_old_status(sender, instance: ContestEntry, **kwargs):
    """
    Capture previous status so post_save can decide whether to notify the customer.
    """
    if not instance.pk:
        instance._old_status = None
        return
    try:
        old = ContestEntry.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._old_status = old
    except Exception:
        instance._old_status = None


@receiver(post_save, sender=ContestEntry)
def _contest_entry_notify_customer_on_review_completion(sender, instance: ContestEntry, created: bool, **kwargs):
    """
    If a receipt submission was flagged for manual review, notify the customer again after
    the team finishes review (e.g., under_review -> verified/rejected).
    """
    try:
        old_status = getattr(instance, "_old_status", None)
        new_status = instance.status

        # Only notify on meaningful transitions
        if old_status == new_status:
            return

        # We only care about manual-review completion transitions
        if old_status not in {"under_review", "submitted", "pending"}:
            return

        if new_status not in {"verified", "rejected", "winner"}:
            return

        # Prevent duplicate notification for the same status
        if instance.last_customer_notification_status == new_status:
            return

        if not instance.customer or not instance.customer.phone_number:
            return

        # SKIP for receipt-first auto-OCR flow (submitted -> verified in <10 seconds means auto-OCR)
        # The step-by-step service already sent receipt details + PDPA, so don't send approval here.
        if old_status == "submitted" and new_status == "verified":
            age = (timezone.now() - instance.submitted_at).total_seconds() if instance.submitted_at else 999
            if age < 10:  # Auto-OCR happens within seconds
                logger.info(f"Skipping signal notification for auto-OCR entry {instance.entry_id} (receipt-first flow)")
                return

        wa = WhatsAppAPIService()

        if new_status == "verified":
            msg = (
                "✅ Update: Your receipt submission has been **approved** after manual review.\n\n"
                "Thank you for joining! We’ll keep you posted if you win."
            )
        elif new_status == "rejected":
            reason = (instance.rejection_reason or "").strip()
            if reason:
                msg = (
                    "⚠️ Update: Your receipt submission has been **rejected** after manual review.\n\n"
                    f"Reason: {reason}\n\n"
                    "If you believe this is a mistake, please reply here and our team will assist."
                )
            else:
                msg = (
                    "⚠️ Update: Your receipt submission has been **rejected** after manual review.\n\n"
                    "If you believe this is a mistake, please reply here and our team will assist."
                )
        else:  # winner
            msg = (
                "🎉 Congratulations! Your entry has been marked as a **winner**.\n\n"
                "Our team will contact you with next steps."
            )

        result = wa.send_text_message(instance.customer.phone_number, msg)
        if result.get("success"):
            # Mark as notified (use update_fields to reduce churn)
            instance.last_customer_notification_status = new_status
            instance.last_customer_notification_at = timezone.now()
            instance.save(update_fields=["last_customer_notification_status", "last_customer_notification_at"])
            logger.info("Notified customer %s for ContestEntry %s status=%s", instance.customer.phone_number, instance.entry_id, new_status)
        else:
            logger.warning("Failed to notify customer %s for ContestEntry %s status=%s error=%s",
                           instance.customer.phone_number, instance.entry_id, new_status, result.get("error"))

    except Exception as e:
        logger.error("ContestEntry notification signal error: %s", str(e), exc_info=True)




