from django.core.management.base import BaseCommand
from messaging.whatsapp_service import WhatsAppAPIService

class Command(BaseCommand):
    help = 'Setup WhatsApp API instance and webhook'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='Webhook URL for receiving WhatsApp events',
            default='https://webhook.site/your-unique-id-here'
        )
    
    def handle(self, *args, **options):
        wa_service = WhatsAppAPIService()
        
        self.stdout.write("Creating WhatsApp instance...")
        
        # Create instance
        result = wa_service.create_instance()
        if result['success']:
            instance_id = result['instance_id']
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created instance: {instance_id}')
            )
            
            # Set webhook if URL provided
            webhook_url = options['webhook_url']
            if webhook_url and webhook_url != 'https://webhook.site/your-unique-id-here':
                self.stdout.write(f"Setting webhook: {webhook_url}")
                webhook_result = wa_service.set_webhook(webhook_url)
                
                if webhook_result['success']:
                    self.stdout.write(
                        self.style.SUCCESS('Webhook set successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to set webhook: {webhook_result.get("error", "Unknown error")}')
                    )
            
            # Print instructions
            self.stdout.write("\n" + "="*50)
            self.stdout.write("IMPORTANT: Update your views.py with the instance ID:")
            self.stdout.write(f'wa_service.set_instance_id("{instance_id}")')
            self.stdout.write("\nConnect your WhatsApp:")
            self.stdout.write("1. Scan the QR code that appears in your WhatsApp Web")
            self.stdout.write("2. Your instance will be ready to send messages")
            self.stdout.write("="*50)
            
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to create instance: {result.get("error", "Unknown error")}')
            )
