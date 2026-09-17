from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jobs', '0005_alter_job_options_alter_jobapplication_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='applications',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
