from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand


class Command(BaseCommand):
    """
    Extends the built-in createsuperuser to also set role='super_admin'
    so the Kennedia admin dashboard works correctly on first login.
    """
    def handle(self, *args, **options):
        super().handle(*args, **options)
        # After the user is created, set the role
        from django.contrib.auth import get_user_model
        User = get_user_model()
        email = options.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                if user.role != 'super_admin':
                    user.role = 'super_admin'
                    user.save(update_fields=['role'])
                    self.stdout.write('Role set to super_admin.')
            except User.DoesNotExist:
                pass
