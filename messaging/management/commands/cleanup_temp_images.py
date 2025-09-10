"""
Django management command to clean up expired temporary images
Run this periodically via cron job or Django-crontab
"""

from django.core.management.base import BaseCommand
from messaging.temp_image_storage import TemporaryImageStorage

class Command(BaseCommand):
    help = 'Clean up expired temporary WhatsApp images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually deleting files',
        )

    def handle(self, *args, **options):
        temp_storage = TemporaryImageStorage()
        
        if options['dry_run']:
            self.stdout.write("🧹 DRY RUN: Checking for expired files...")
        else:
            self.stdout.write("🧹 Cleaning up expired temporary images...")
        
        if not options['dry_run']:
            result = temp_storage.cleanup_expired_files()
            
            if result['success']:
                count = result['cleaned_count']
                if count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Cleaned up {count} expired image(s)')
                    )
                else:
                    self.stdout.write('ℹ️  No expired images found')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error during cleanup: {result["error"]}')
                )
        else:
            # For dry run, we'd implement a check without deletion
            self.stdout.write('🔍 Dry run completed')
