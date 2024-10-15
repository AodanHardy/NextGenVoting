from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ElectionDetailsForm, BallotForm, CandidatesForm, VotersListForm
from .models import Election
from voting.models import Ballot, Candidate, Voter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


# Create your views here.

@login_required
def dashboard(request):

    user_elections = Election.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'elections': user_elections})


def election_details(request):
    pass



@login_required
def add_ballots(request):
    pass


@login_required
def add_candidates(request):
    pass


@login_required
def add_voters(request):
    pass


@login_required
def save_election(request):
    pass
