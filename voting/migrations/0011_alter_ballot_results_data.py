# Generated by Django 5.1.4 on 2025-01-24 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("voting", "0010_ballot_results_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ballot",
            name="results_data",
            field=models.JSONField(default=dict),
        ),
    ]
