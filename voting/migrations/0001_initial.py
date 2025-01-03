# Generated by Django 5.1.2 on 2024-10-14 16:09

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('voting_type', models.CharField(choices=[('FPP', 'First Past The Post'), ('RCV', 'Ranked Choice Voting'), ('YN', 'YES or No Vote')], max_length=3)),
                ('results_published', models.BooleanField(default=False)),
                ('votes_cast', models.IntegerField(default=0)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ballots', to='elections.election')),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('ballot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='voting.ballot')),
            ],
        ),
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voters', to='elections.election')),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('vote_data', models.JSONField()),
                ('blockchain_transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('verified', models.BooleanField(default=False)),
                ('ballot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='voting.ballot')),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='voting.voter')),
            ],
        ),
    ]
