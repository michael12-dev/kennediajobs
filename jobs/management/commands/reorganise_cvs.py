"""
Kennedia Jobs — jobs/management/commands/reorganise_cvs.py

Moves existing CVs from the flat applications/cvs/ folder into
organised per-job folders: applications/cvs/job_{id}_{slug}/

Usage:
    python manage.py reorganise_cvs           # preview (dry run)
    python manage.py reorganise_cvs --apply   # actually move files
"""
import os
import re
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from jobs.models import JobApplication


def make_slug(title: str) -> str:
    title = re.sub(r'[^\w\s-]', '', title.lower())
    return re.sub(r'[\s_]+', '-', title).strip('-')[:50]


class Command(BaseCommand):
    help = 'Reorganise existing CV uploads into per-job folders.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually move files (default is dry-run preview).',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        mode = 'LIVE' if apply else 'DRY RUN'
        self.stdout.write(f'\n=== CV Reorganiser — {mode} ===\n')

        apps = JobApplication.objects.select_related('job').exclude(cv_file='')
        total = apps.count()
        moved = 0
        skipped = 0
        errors = 0

        for app in apps:
            if not app.cv_file:
                continue

            old_relative = app.cv_file.name          # e.g. applications/cvs/amaka.pdf
            old_absolute = os.path.join(settings.MEDIA_ROOT, old_relative)

            # Build new path
            slug = make_slug(app.job.title)
            folder = f'applications/cvs/job_{app.job.id}_{slug}'
            filename = os.path.basename(old_relative)
            new_relative = f'{folder}/{filename}'
            new_absolute = os.path.join(settings.MEDIA_ROOT, new_relative)

            # Already in correct folder — skip
            if old_relative == new_relative:
                self.stdout.write(f'  [SKIP] {filename} — already organised')
                skipped += 1
                continue

            # Source file doesn't exist on disk
            if not os.path.exists(old_absolute):
                self.stdout.write(
                    self.style.WARNING(f'  [MISSING] {old_relative} — file not found on disk')
                )
                errors += 1
                continue

            self.stdout.write(f'  [MOVE] {old_relative}')
            self.stdout.write(f'      → {new_relative}')

            if apply:
                try:
                    os.makedirs(os.path.dirname(new_absolute), exist_ok=True)
                    shutil.move(old_absolute, new_absolute)
                    # Update DB record
                    app.cv_file.name = new_relative
                    app.save(update_fields=['cv_file'])
                    moved += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'      ERROR: {e}'))
                    errors += 1
            else:
                moved += 1  # count as would-be moves in dry run

        self.stdout.write('\n--- Summary ---')
        self.stdout.write(f'  Total applications with CVs : {total}')
        self.stdout.write(f'  {"Would move" if not apply else "Moved"}    : {moved}')
        self.stdout.write(f'  Already organised           : {skipped}')
        self.stdout.write(f'  Errors / missing files      : {errors}')

        if not apply:
            self.stdout.write(
                self.style.WARNING(
                    '\nThis was a DRY RUN. Run with --apply to actually move files.\n'
                    'Command: python manage.py reorganise_cvs --apply'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('\nDone! All CVs reorganised.\n'))
