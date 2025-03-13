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
    voting_type = models.CharField(max_length=3, choices=VOTING_TYPE_CHOICES)
    number_of_winners = models.IntegerField(default=1)
    results_data = models.JSONField(default=dict)

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
    email = models.EmailField(unique=False)
    voted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ballot = models.ForeignKey('Ballot', on_delete=models.CASCADE, related_name='votes')
    vote_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class Blockchain_Vote(models.Model):
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    STATUS_CHOICES = [(COMPLETE, "COMPLETE"),(IN_PROGRESS, "IN_PROGRESS"), (FAILED, "FAILED")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='blockchain_vote')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=IN_PROGRESS, max_length=20)

    # if vote fails to be uploaded to blockchain, save it here
    vote_data = models.JSONField(default=dict, blank=True, null=True)
