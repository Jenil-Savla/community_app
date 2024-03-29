# Generated by Django 4.1.6 on 2024-03-21 10:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0019_user_additional_phone_user_email_id_user_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="blog",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
