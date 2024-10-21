from django.http import HttpResponse
from django.shortcuts import render

from elections.models import Election
from voting.models import Ballot, Voter


# Create your views here.
def voting_intro(request, vote_id):
    try:
        voter = Voter.objects.get(id=vote_id)
        election = voter.election

    except Voter.DoesNotExist:
        return HttpResponse('Invalid vote ID.')

    return render(request, 'voting_intro.html', {
        'election': election,
        'ballots': election.ballots.all(),
        'voter': voter
    })


def voting_ballot(request):
    return None