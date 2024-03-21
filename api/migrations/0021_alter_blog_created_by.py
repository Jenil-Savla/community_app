# Generated by Django 4.1.6 on 2024-03-21 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0020_blog_created_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                default="admin@gmail.com",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
