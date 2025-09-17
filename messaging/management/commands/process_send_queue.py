from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.models import SendQueue, CampaignMessage

class Command(BaseCommand):
    help = 'Process queued campaign messages and mark them sent (stub send).'

    def handle(self, *args, **options):
        now = timezone.now()
        qs = SendQueue.objects.select_related('campaign_message', 'tenant').filter(status='queued', scheduled_at__lte=now)[:100]
        processed = 0
        for task in qs:
            cm = task.campaign_message
            try:
                # Simulate send success
                cm.status = 'sent'
                cm.sent_at = now
                cm.save(update_fields=['status', 'sent_at'])
                task.status = 'sent'
                task.processed_at = now
                task.save(update_fields=['status', 'processed_at'])
                processed += 1
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                task.processed_at = now
                task.save(update_fields=['status', 'error_message', 'processed_at'])
        self.stdout.write(self.style.SUCCESS(f'Processed {processed} queued messages.'))
