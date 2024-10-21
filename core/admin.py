from django.contrib import admin

from elections.models import Election
from voting.models import Ballot, Candidate, Voter


# Register your models here.

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    readonly_fields = ('start_time', 'end_time')  # Prevent editing after election has started/completed

@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('title', 'voting_type', 'election')
    list_filter = ('voting_type', 'election')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('title', 'ballot')

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'election')
    search_fields = ('name', 'email')
