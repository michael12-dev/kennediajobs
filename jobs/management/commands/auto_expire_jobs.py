"""
jobs/management/commands/auto_expire_jobs.py

Marks jobs as 'expired' when their deadline has passed.
Run manually or via a cron job / scheduled task.

Usage:
    python manage.py auto_expire_jobs
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from jobs.models import Job


class Command(BaseCommand):
    help = 'Mark jobs as expired when their deadline has passed.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        expired = Job.objects.filter(
            status='active',
            deadline__lt=today,
        )
        count = expired.count()
        if count:
            expired.update(status='expired')
            self.stdout.write(
                self.style.SUCCESS(f'Marked {count} job(s) as expired.')
            )
        else:
            self.stdout.write('No jobs to expire.')
