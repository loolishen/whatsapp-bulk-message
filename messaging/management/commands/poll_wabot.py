"""
Management command to poll WABOT for new messages
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.wabot_poller import WABOTPoller
import time

class Command(BaseCommand):
    help = 'Poll WABOT for new messages'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='Polling interval in seconds (default: 30)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit'
        )
    
    def handle(self, *args, **options):
        poller = WABOTPoller()
        interval = options['interval']
        run_once = options['once']
        
        self.stdout.write(f'Starting WABOT poller with {interval}s interval...')
        
        if run_once:
            self.stdout.write('Running once...')
            success = poller.poll_messages()
            if success:
                self.stdout.write(self.style.SUCCESS('Polling completed successfully'))
            else:
                self.stdout.write(self.style.ERROR('Polling failed'))
        else:
            self.stdout.write('Running continuously (Ctrl+C to stop)...')
            try:
                while True:
                    success = poller.poll_messages()
                    if success:
                        self.stdout.write(f'{timezone.now()}: Polled successfully')
                    else:
                        self.stdout.write(self.style.WARNING(f'{timezone.now()}: Polling failed'))
                    
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Polling stopped'))
