# Generated by Django 4.1.6 on 2023-02-15 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_user_relation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.CharField(default='Male', max_length=10),
        ),
        migrations.AlterField(
            model_name='user',
            name='maritial_status',
            field=models.CharField(default='Single', max_length=10),
        ),
    ]