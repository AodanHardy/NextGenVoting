# Generated by Django 5.1.2 on 2024-10-17 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voter',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
