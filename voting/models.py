import uuid

from django.db import models

from elections.models import Election


# Create your models here.

class Ballot(models.Model):
    VOTING_TYPE_CHOICES = [
        ('FPP', 'First Past The Post'),
        ('RCV', 'Ranked Choice Voting'),
        ('YN', 'YES or No Vote'),
    ]

    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='ballots')
    title = models.CharField(max_length=255)
    description = models.TextField()
    voting_type = models.CharField(max_length=3, choices=VOTING_TYPE_CHOICES)
    results_published = models.BooleanField(default=False)
    votes_cast = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    ballot = models.ForeignKey(Ballot, on_delete=models.CASCADE, related_name='candidates')
    title = models.CharField(max_length=255)


    def __str__(self):
        return self.title


class Voter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='voters')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ballot = models.ForeignKey('Ballot', on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='votes')
    vote_data = models.JSONField()
    blockchain_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Vote by {self.voter.name} for ballot {self.ballot.title}"
