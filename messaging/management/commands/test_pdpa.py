"""
Management command to test PDPA consent functionality
"""
from django.core.management.base import BaseCommand
from messaging.models import Customer, Tenant, Consent
from messaging.pdpa_service import PDPAConsentService
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test PDPA consent functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--customer-phone',
            type=str,
            help='Phone number of customer to test with',
            default='60123456789'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Test message to send',
            default='hello'
        )
        parser.add_argument(
            '--action',
            type=str,
            choices=['test', 'clear-consent', 'show-consent'],
            default='test',
            help='Action to perform'
        )

    def handle(self, *args, **options):
        customer_phone = options['customer_phone']
        message = options['message']
        action = options['action']
        
        # Get or create tenant
        tenant = Tenant.objects.first()
        if not tenant:
            self.stdout.write(
                self.style.ERROR('No tenant found. Please create a tenant first.')
            )
            return
        
        # Get or create customer
        customer, created = Customer.objects.get_or_create(
            phone_number=customer_phone,
            defaults={
                'name': f'Test Customer {customer_phone[-4:]}',
                'tenant': tenant
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created customer: {customer.name} ({customer.phone_number})')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Found customer: {customer.name} ({customer.phone_number})')
            )
        
        if action == 'test':
            self.test_pdpa_flow(customer, message, tenant)
        elif action == 'clear-consent':
            self.clear_consent(customer, tenant)
        elif action == 'show-consent':
            self.show_consent(customer, tenant)
    
    def test_pdpa_flow(self, customer, message, tenant):
        """Test PDPA flow with given message"""
        self.stdout.write(f'\nTesting PDPA flow with message: "{message}"')
        
        # Initialize PDPA service
        pdpa_service = PDPAConsentService()
        
        # Show current consent status
        consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
        self.stdout.write(f'Current consent status: {consent_status}')
        
        # Process message
        result = pdpa_service.handle_incoming_message(customer, message, tenant)
        
        if result:
            self.stdout.write(
                self.style.SUCCESS('PDPA service handled the message successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('PDPA service did not handle the message')
            )
        
        # Show updated consent status
        new_consent_status = pdpa_service._get_consent_status(tenant, customer, 'whatsapp')
        self.stdout.write(f'Updated consent status: {new_consent_status}')
    
    def clear_consent(self, customer, tenant):
        """Clear all consent records for customer"""
        deleted_count = Consent.objects.filter(
            tenant=tenant,
            customer=customer,
            type='whatsapp'
        ).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {deleted_count} consent records for {customer.name}')
        )
    
    def show_consent(self, customer, tenant):
        """Show consent history for customer"""
        consents = Consent.objects.filter(
            tenant=tenant,
            customer=customer,
            type='whatsapp'
        ).order_by('-occurred_at')
        
        if not consents:
            self.stdout.write('No consent records found')
            return
        
        self.stdout.write(f'\nConsent history for {customer.name}:')
        for consent in consents:
            self.stdout.write(
                f'  {consent.occurred_at.strftime("%Y-%m-%d %H:%M:%S")} - '
                f'{consent.status.upper()}'
            )
