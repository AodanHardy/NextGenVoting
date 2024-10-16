from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ElectionDetailsForm, BallotForm, CandidatesForm, VotersListForm
from .models import Election
from voting.models import Ballot, Candidate, Voter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .utils import ElectionData, BallotData


# Create your views here.

@login_required
def dashboard(request):

    user_elections = Election.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'elections': user_elections})


def election_details(request):
    if request.method == 'POST':
        # Process the form data
        form = ElectionDetailsForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            num_of_ballots = form.cleaned_data['number_of_ballots']
            use_blockchain = form.cleaned_data['use_blockchain']

            # Create an Election object and save it in the session
            election = ElectionData(
                title,
                description,
                start_time,
                end_time,
                num_of_ballots,
                use_blockchain

            )

            electionData = election.__dict__

            electionData['start_time'] = election.start_time.isoformat()
            electionData['end_time'] = election.end_time.isoformat()

            request.session['election'] = electionData

            # Redirect to the next form
            return redirect('add_ballots')
    else:
        form = ElectionDetailsForm()

    return render(request, 'election_details.html', {'form': form})



@login_required
def add_ballots(request):
    # Retrieve the election object from the session
    election_data = request.session.get('election')
    if not election_data:
        return redirect('elections:election_details')

    current_ballot = request.session.get('current_ballot', 1)
    num_of_ballots = election_data['num_of_ballots']

    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            # Create the BallotData object
            ballot = BallotData(
                title=form.cleaned_data['ballot_title'],
                voting_type=form.cleaned_data['voting_type']
            )

            # Save this ballot to the session as currentBallot
            request.session['currentBallot'] = ballot.__dict__

            # Redirect to the add candidates form to complete this ballot
            return redirect('elections:add_candidates')

    else:
        form = BallotForm()

    return render(request, 'add_ballots.html', {
        'form': form,
        'current_ballot': current_ballot,
        'num_of_ballots': num_of_ballots
    })



@login_required
def add_candidates(request):
    pass


@login_required
def add_voters(request):
    pass


@login_required
def save_election(request):
    pass
