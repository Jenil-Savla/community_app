# Generated by Django 4.1.6 on 2023-02-17 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_village_no_of_families'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('about', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('venue', models.CharField(default='N/A', max_length=1000)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('photos', models.URLField(blank=True, null=True)),
                ('pdf', models.URLField(blank=True, null=True)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='events/')),
            ],
        ),
        migrations.AddField(
            model_name='village',
            name='shakha',
            field=models.CharField(default='None', max_length=50),
        ),
    ]
