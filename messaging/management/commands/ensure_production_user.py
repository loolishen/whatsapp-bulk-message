from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Tenant, TenantUser

class Command(BaseCommand):
    help = 'Ensure production user exists for login'

    def handle(self, *args, **options):
        self.stdout.write("Ensuring production user exists...")
        
        try:
            User = get_user_model()
            
            # Create or get tenant
            tenant, created_tenant = Tenant.objects.get_or_create(
                name='Demo Tenant',
                defaults={
                    'plan': 'pro',
                    'creation_date': timezone.now(),
                }
            )
            
            if created_tenant:
                self.stdout.write(f"Created tenant: {tenant.name} (plan: {tenant.plan})")
            else:
                self.stdout.write(f"Found existing tenant: {tenant.name} (plan: {tenant.plan})")
            
            # Create or update user
            user, created_user = User.objects.get_or_create(
                username='tenant',
                defaults={'email': 'tenant@example.com'}
            )
            
            # Always update password to ensure it's correct
            user.set_password('Tenant123!')
            user.is_active = True
            user.save()
            
            if created_user:
                self.stdout.write(f"Created user: {user.username}")
            else:
                self.stdout.write(f"Updated user: {user.username}")
            
            # Create tenant-user link
            tenant_user, created_link = TenantUser.objects.get_or_create(
                user=user,
                tenant=tenant,
                defaults={'role': 'owner'}
            )
            
            if created_link:
                self.stdout.write(f"Created tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
            else:
                self.stdout.write(f"Found existing tenant-user link: {user.username} @ {tenant.name} (role: {tenant_user.role})")
            
            # Test authentication
            from django.contrib.auth import authenticate
            auth_user = authenticate(username='tenant', password='Tenant123!')
            if auth_user:
                self.stdout.write(self.style.SUCCESS("Authentication test successful!"))
            else:
                self.stdout.write(self.style.ERROR("Authentication test failed!"))
                return
            
            self.stdout.write(self.style.SUCCESS("Production user setup completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to ensure production user: {e}"))
            import traceback
            traceback.print_exc()
