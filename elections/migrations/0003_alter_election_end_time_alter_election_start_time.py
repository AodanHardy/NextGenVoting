# Generated by Django 5.1.2 on 2024-10-17 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='election',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]