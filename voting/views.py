from django.http import HttpResponse
from django.shortcuts import render, redirect

from elections.models import Election
from voting.models import Ballot, Voter
from voting.utils import VoterData, VoteBallotData


# Create your views here.
def voting_intro(request, voter_id):
    try:
        voter = Voter.objects.get(id=voter_id)
        election = voter.election

        # Set voter data object
        voter_data = {
            'voter_id': str(voter_id),
            'election_id': str(election.id),
            'ballots': []
        }

        # Get ballots for the election
        ballots = election.ballots.all()
        for ballot in ballots:
            ballot_data = {
                'title': ballot.title,
                'description': ballot.description,
                'voting_type': ballot.voting_type,
                'candidates': [candidate.id for candidate in ballot.candidates.all()],
                'voteData': []
            }

            voter_data['ballots'].append(ballot_data)

        # Save the voter_data object to session as a dictionary
        request.session['voter_data'] = voter_data

    except Voter.DoesNotExist:
        return HttpResponse('Invalid vote ID.')

    return render(request, 'voting_intro.html', {
        'election': election,
        'ballots': election.ballots.all(),
        'voter': voter
    })


def voting_ballot(request, vote_id, ballot_index):
    # Get the voter data from the session
    voter_data = request.session.get('voter_data')

    if ballot_index is None:
        ballot_index = 0

    if not voter_data:
        return HttpResponse('Voting session expired.')

    # Retrieve the list of ballots from the stored voter data
    ballots = voter_data.get('ballots')

    # Check if ballot_index is valid
    if ballot_index < 0 or ballot_index >= len(ballots):
        return HttpResponse('Invalid ballot index.')

    # get the current ballot
    ballot_data = ballots[ballot_index]

    if request.method == 'POST':

        selected_candidates = request.POST.getlist('selected_candidates')

        ballot_data.voteData.append(selected_candidates)

        request.session['voter_data'] = voter_data

        # add 1 to ballot index
        next_ballot_index = ballot_index + 1

        # Check if there are more ballots to vote on
        if next_ballot_index < len(ballots):
            return redirect('voting:voting_ballot', vote_id=vote_id, ballot_index=next_ballot_index)
        else:
            # All ballots are done
            return redirect('voting:vote_summary', vote_id=vote_id)

    # Render the appropriate template for the voting type
    voting_type = ballot_data.get('voting_type')
    if voting_type == 'FFP':
        template_name = 'ballot_first_past_post.html'
    elif voting_type == 'RCV':
        template_name = 'ballot_ranked_choice.html'
    elif voting_type == 'YN':
        template_name = 'ballot_generic.html'
    else:
        return HttpResponse('Invalid Voting choice.')

    return render(request, template_name, {
        'ballot': ballot_data,
        'voter_data': voter_data,
        'ballot_index': ballot_index
    })

