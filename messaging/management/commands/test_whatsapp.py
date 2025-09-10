from django.core.management.base import BaseCommand
from messaging.whatsapp_service import WhatsAppAPIService
from messaging.models import Contact

class Command(BaseCommand):
    help = 'Test sending a message to the default test number'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--instance-id',
            type=str,
            help='WhatsApp instance ID',
            default='68A0A11A89A8D'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Message to send',
            default='Hello! This is a test message from your WhatsApp Bulk Message app.'
        )
        parser.add_argument(
            '--number',
            type=str,
            help='Phone number to send to',
            default='+60172419029'
        )
    
    def handle(self, *args, **options):
        wa_service = WhatsAppAPIService()
        wa_service.set_instance_id(options['instance_id'])
        
        phone_number = options['number']
        message = options['message']
        
        self.stdout.write(f"Sending test message to {phone_number}...")
        self.stdout.write(f"Message: {message}")
        
        result = wa_service.send_text_message(phone_number, message)
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS('Message sent successfully!')
            )
            self.stdout.write(f"API Response: {result['data']}")
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to send message: {result.get("error", "Unknown error")}')
            )
            
        # Also check if contact exists in database
        try:
            contact = Contact.objects.get(phone_number=phone_number)
            self.stdout.write(f"Contact found in database: {contact.name} - {contact.phone_number}")
        except Contact.DoesNotExist:
            self.stdout.write(f"Contact {phone_number} not found in database. Consider adding it.")
