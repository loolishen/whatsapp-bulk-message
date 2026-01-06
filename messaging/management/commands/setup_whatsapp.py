import os
from django.core.management.base import BaseCommand
from messaging.whatsapp_service import WhatsAppAPIService

class Command(BaseCommand):
    help = 'Setup WABot webhook for the configured instance (no instance creation)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='Webhook URL for receiving WhatsApp events',
            default=''
        )
        parser.add_argument(
            '--disable',
            action='store_true',
            help='Disable webhook delivery instead of enabling it'
        )
    
    def handle(self, *args, **options):
        # Avoid slow model host connectivity checks in Cloud Shell environments.
        os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

        wa_service = WhatsAppAPIService()

        webhook_url = (options.get('webhook_url') or '').strip()
        enable = not bool(options.get('disable'))

        if not webhook_url:
            self.stdout.write(self.style.ERROR('Missing --webhook-url'))
            self.stdout.write('Example:')
            self.stdout.write('  python3 manage.py setup_whatsapp --webhook-url "https://YOUR_APP/webhook/whatsapp/"')
            return

        self.stdout.write(f"Setting webhook (enable={str(enable).lower()}): {webhook_url}")
        result = wa_service.set_webhook(webhook_url, enable=enable)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS('Webhook settings updated successfully'))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to set webhook: {result.get('error', 'Unknown error')}"))

        # Best-effort: show instance status
        try:
            status = wa_service.get_instance_status()
            self.stdout.write("Instance status:")
            self.stdout.write(str(status)[:2000])
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Could not fetch instance status: {e}"))
