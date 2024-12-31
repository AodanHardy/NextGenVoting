from django.http import HttpResponse
from django.shortcuts import render, redirect

from elections.models import Election
from voting.models import Ballot, Voter, Candidate, Vote
from voting.utils import get_ranked_order


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
                'id': ballot.id,
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

    # Getting candidates from candidate ids
    candidate_ids = ballot_data.get('candidates', [])
    candidates = Candidate.objects.filter(id__in=candidate_ids)

    # Once a vote has been submitted
    if request.method == 'POST':

        # check if ranked choice
        if ballot_data.get('voting_type') == 'RCV':
            rankedChoiceDict = {}
            for candidate_id in candidate_ids:
                rc_vote = request.POST.get(str(candidate_id))

                if rc_vote != "":
                    rankedChoiceDict[candidate_id] = rc_vote

            ballot_data.get('voteData').append(get_ranked_order(rankedChoiceDict))


        else:
            # non-RCV ballots
            selected_candidates = request.POST.getlist('selected_candidate')

            ballot_data.get('voteData').append(selected_candidates)

        request.session['voter_data'] = voter_data

        # add 1 to ballot index
        next_ballot_index = ballot_index + 1

        # Check if there are more ballots to vote on
        if next_ballot_index < len(ballots):
            return redirect('voting:voting_ballot', vote_id=vote_id, ballot_index=next_ballot_index)
        else:
            # All ballots are done
            return redirect('voting:vote_summary', vote_id=vote_id)

    # open different html file depending on voting type
    voting_type = ballot_data.get('voting_type')
    if voting_type == 'FPP':
        template_name = 'ballot_first_past_post.html'
    elif voting_type == 'RCV':
        template_name = 'ballot_ranked_choice.html'
    elif voting_type == 'YN':
        template_name = 'ballot_yes_no.html'
    else:
        return HttpResponse('Invalid Voting choice.')

    return render(request, template_name, {
        'ballot': ballot_data,
        'voter_data': voter_data,
        'ballot_index': ballot_index,
        'candidates': candidates,
    })


def vote_summary(request, vote_id):
    # gather data from session
    voter_data = request.session.get('voter_data')
    ballots = voter_data.get('ballots')
    if request.method == 'POST':
        for ballot in ballots:

            # getting data in correct json format
            ballotVoteDict = ""

            # FPP format : {"id": 1}
            if ballot.get('voting_type') == 'FPP':
                voteData = ballot.get('voteData')
                voteData = voteData[0][0]
                ballotVoteDict = {"id": int(voteData)}

            # RCV format: {"rankings": [3, 2, 1]}
            elif ballot.get('voting_type') == 'RCV':
                voteData = ballot.get('voteData')
                voteData = voteData[0]
                ballotVoteDict = {"rankings": voteData}

            # YN format : {"vote": "yes"}
            elif ballot.get('voting_type') == 'YN':
                voteData = ballot.get('voteData')
                voteData = voteData[0][0]
                ballotVoteDict = {"vote": voteData}

            # get ballot
            ballotId = ballot.get('id')
            ballotobj = Ballot.objects.get(id=ballotId)

            '''
             At this point, the the ballot data is set and we need to save the vote data to the database
             
             take ballot id, create a new vote object with ballot id and vote data
            '''
            # creating votes
            Vote.objects.create(
                ballot=ballotobj,
                vote_data=ballotVoteDict
            )

        '''
        after all ballots have been uploaded, i need to update the voted column of the voter table
        '''
        voterObj = Voter.objects.get(id=vote_id)
        voterObj.voted = True
        voterObj.save()





    return render(request, 'vote_summary.html',
                  {'ballots': ballots})
