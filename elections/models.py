from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Election(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elections')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    use_blockchain = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False)
    votes_cast = models.IntegerField(default=0)

    def __str__(self):
        return self.title

'''
class ElectionResults(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='results')
    ballot = models.ForeignKey('voting.Ballot', on_delete=models.CASCADE, related_name='results')
    results_data = models.JSONField()

    def __str__(self):
        return f"Results for {self.election.title}"
'''