from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from messaging.models import Tenant, TenantUser


class Command(BaseCommand):
    help = 'Seed a tenant and a user linked via TenantUser for login tests.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='khinddemo')
        parser.add_argument('--password', type=str, default='d3mo.123')
        parser.add_argument('--email', type=str, default='khinddemo@example.com')
        parser.add_argument('--tenant', type=str, default='Demo Tenant')
        parser.add_argument('--plan', type=str, default='pro')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']
        tenant_name = options['tenant']
        plan = options['plan']

        tenant, _ = Tenant.objects.get_or_create(name=tenant_name, defaults={
            'plan': plan,
            'creation_date': timezone.now(),
        })

        user, created_user = User.objects.get_or_create(username=username, defaults={'email': email})
        if created_user:
            user.set_password(password)
            user.save()

        TenantUser.objects.get_or_create(user=user, tenant=tenant, defaults={'role': 'owner'})

        self.stdout.write(self.style.SUCCESS(
            f"Seeded tenant '{tenant.name}' (plan={tenant.plan}) and user '{user.username}'"
        ))


