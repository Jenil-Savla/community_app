# Generated by Django 4.1.6 on 2023-08-14 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0016_user_in_laws_shakha_user_shakha"),
    ]

    operations = [
        migrations.CreateModel(
            name="Blog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("details", models.TextField(default="NA")),
                (
                    "picture",
                    models.ImageField(blank=True, null=True, upload_to="blogs/"),
                ),
                ("phone", models.BigIntegerField(default=0)),
                ("is_advertisement", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]