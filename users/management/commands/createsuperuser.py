"""
users/management/commands/create_superadmin.py

Creates the default super admin account if it doesn't exist.
Run automatically during build via build.sh
"""
from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Create default super admin account if it does not exist.'

    def handle(self, *args, **options):
        email = 'justice.okafor@kennediaconsulting.net'
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(f'Super admin already exists: {email}')
            return

        user = CustomUser(
            username='justice_okafor',
            email=email,
            first_name='Justice',
            last_name='Okafor',
            role='super_admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password('Kennedia1234!')
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Super admin created: {email}'))
