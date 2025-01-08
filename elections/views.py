from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from algorithms.firstPastThePost import FPTPVoteProcessor
from algorithms.rankedChoiceVote import RankedChoiceVoteProcessor
from .emailManager import EmailManager, sendAllEmails_async
from .forms import ElectionDetailsForm, BallotForm, CandidatesForm
from .models import Election, ElectionResults
from voting.models import Ballot, Candidate, Voter, Vote
from django.contrib.auth.decorators import login_required

import csv
from .forms import VoterUploadForm
from .utils import VoterData, getWinningVote
from .utils import ElectionData, BallotData

# Create your views here.

@login_required
def dashboard(request):
    user_elections = Election.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'elections': user_elections})


# page for viewing individual election
@login_required
def manage_election(request, election_id):
    election = get_object_or_404(Election, id=election_id, user=request.user)
    voterCount = len(election.voters.all())


    if request.method == 'POST':
        # check if user started or ended election
        action = request.POST.get('action')

        if action == 'start':
            election.start_time = timezone.now()
            election.status = 'active'
            election.save()

            # trigger to send out emails here
            sendAllEmails_async.delay(election_id)

        # if they ended election, update db and trigger counting process
        elif action == 'end':
            election.end_time = timezone.now()
            election.status = 'completed'
            election.save()

            # trigger to start counting process

            # get all ballots form this election
            ballots = Ballot.objects.filter(election=election_id)

            # for loop for each ballot in election
            for ballot in ballots:

                # fetch votes
                votes = Vote.objects.filter(ballot=ballot)

                # prep data
                vote_list = []
                for vote in votes:
                    vote_list.append(vote.vote_data)

                candidates_list = Candidate.objects.filter(ballot=ballot)
                candidates_dict = {}
                for candidate in candidates_list:
                    candidates_dict[candidate.id] = candidate.title

                '''
                    at this point i have all the votes and candidtes
                    
                    i now need to update the algorithms to take this data and return results
                    
                    then check each voting type and pass it too the algorithms 
                '''

                # call counting algorithm

                result = ElectionResults()
                result.election = election
                result.ballot = ballot

                # call FPP algorithm for FPP or YN votes
                if ballot.voting_type == "FPP" or ballot.voting_type == "YN":
                    processor = FPTPVoteProcessor(candidates_dict, vote_list)
                    result.results_data = processor.result

                # ranked choice
                elif ballot.voting_type == "RCV":
                    processor = RankedChoiceVoteProcessor(vote_list, candidates_dict, ballot.number_of_winners)
                    result.results_data = processor.finalize_results()

                # save results
                result.save()
                election.results_published = True
                election.save()

        return redirect('manage_election', election_id=election.id)

    # get winners if finished
    ballot_results = []

    # Prepare results
    for ballot in election.ballots.all():

        results = ballot.results.all()
        ballot_winners = []
        for result in results:

            if ballot.voting_type == "RCV":
                winners = result.results_data.get('winners', [])

            elif ballot.voting_type == "FPP" or ballot.voting_type == "YN":
                winnersIds = getWinningVote(result.results_data)
                winners = []
                for id in winnersIds:
                    winners.append(Candidate.objects.get(id=id))


            ballot_winners.extend(winners)

        ballot_results.append({'ballot': ballot,
                               'winners': ballot_winners,
                               'no_of_winners': ballot.number_of_winners})

    return render(request, 'manage_election.html', {'election': election,
                                                    'voters_count': voterCount,
                                                    'ballot_results': ballot_results})

@login_required
def view_fpp_results(request, ballot_id):  # view results function
    ballot = get_object_or_404(Ballot, id=ballot_id, election__user=request.user)
    results = ballot.results.first()
    results_data = results.results_data
    candidates = {str(c.id): c.title for c in ballot.candidates.all()}

    # if its FPP, send to FPP html template
    if ballot.voting_type == "FPP" or ballot.voting_type == "YN":
        labels = [candidates[candidate_id] for candidate_id in results_data.keys()]
        values = list(results_data.values())

        context = {
            'ballot_title': ballot.title,
            'labels': labels,
            'values': values,
        }
        return render(request, 'view_results_FPP.html', context)

    # if its RCV, send to RCV html template but breakdown data first
    elif ballot.voting_type == "RCV":
        rounds = results_data.get("rounds", [])
        candidates = results_data.get("candidates", {})
        quota = results_data.get("quota")
        winners = results_data.get("winners", [])
        processed_rounds = []

        for round_data in rounds:
            processed_round = {
                "round_number": round_data["round_number"],
                "elected": round_data.get("elected", []),
                "surplus": round_data.get("surplus", 0),
                "eliminated": round_data.get("eliminated", []),
                "initial_votes": {
                    candidates[cid]["name"]: votes
                    for cid, votes in round_data["initial_votes"].items()
                },
                "final_votes": {
                    candidates[cid]["name"]: votes
                    for cid, votes in round_data["final_votes"].items()
                },

                "transfers": {
                    candidates[cid]["name"]: votes
                    for cid, votes in round_data["transfers"].items()
                },
            }
            processed_rounds.append(processed_round)

        context = {
            "ballot_title": ballot.title,
            "quota": quota,
            "rounds": processed_rounds,
            "winners": winners,
        }
        return render(request, "view_results_RCV.html", context)


'''' The rest of the views are for the forms for creating an election '''


# Fist form asks for election:
# Title
# Description
# number of ballots
# if it uses blockchain
@login_required
def election_details(request):
    # need to Clear data from previous session

    if request.method == 'POST':
        # Process the form data
        form = ElectionDetailsForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            num_of_ballots = form.cleaned_data['number_of_ballots']
            use_blockchain = form.cleaned_data['use_blockchain']

            # Create an ElectionData object and save it in the session
            election = ElectionData(
                title,
                description,
                num_of_ballots,
                use_blockchain
            )
            # Need to put it in dictionary ro save it
            electionData = election.__dict__


            request.session['election'] = electionData

            return redirect('add_ballots')
    else:
        form = ElectionDetailsForm()

    return render(request, 'election_details.html', {'form': form})



@login_required
def add_ballots(request):
    # get the election object from the session
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
    # Retrieve the current ballot and voting type from the session
    current_ballot = request.session.get('currentBallot')
    election_data = request.session.get('election')

    if not current_ballot or not election_data:
        # Redirect back if there's no ballot data
        return redirect('elections:add_ballots')

    if request.method == 'POST':
        form = CandidatesForm(request.POST)
        if form.is_valid():
            # Get the candidates from the form
            candidates_str = form.cleaned_data['candidates']
            candidate_list = [candidate.strip() for candidate in candidates_str.split(',') if candidate.strip()]

            # Get number of winners
            num_of_winners = form.cleaned_data['number_of_winners']
            if num_of_winners is None:
                num_of_winners = 1
            current_ballot['number_of_winners'] = num_of_winners

            # Add candidates to current ballot
            current_ballot['candidates'].extend(candidate_list)

            # Update the session with current ballot
            request.session['currentBallot'] = current_ballot

            # Logic to move to next ballot
            election_data['ballots'].append(current_ballot)
            request.session['election'] = election_data

            # Clear currentBallot for the next ballot
            del request.session['currentBallot']

            # Check if there are more ballots to add
            current_ballot_num = request.session.get('current_ballot', 1)
            num_of_ballots = election_data['num_of_ballots']

            if current_ballot_num < num_of_ballots:
                request.session['current_ballot'] = current_ballot_num + 1
                return redirect('elections:add_ballots')
            else:
                # All ballots are added, move to voter upload
                # Reset current ballot
                request.session['current_ballot'] = 1
                return redirect('elections:add_voters')

    else:
        form = CandidatesForm()

    return render(request, 'add_candidates.html', {
        'form': form,
        'ballot_title': current_ballot['title'],
        'voting_type': current_ballot['voting_type'],
        'candidates': current_ballot.get('candidates', [])
    })



@login_required
def add_voters(request):
    if request.method == 'POST':
        form = VoterUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['voter_file']

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                voters = []
                for row in reader:
                    name = row.get('name')
                    email = row.get('email')
                    if name and email:
                        voter = VoterData(name, email)  # VoterData from utils.py
                        voters.append(voter.__dict__)

                # Store voters in session
                election_data = request.session.get('election', {})
                if 'voters' not in election_data:
                    election_data['voters'] = []
                election_data['voters'].extend(voters)

                request.session['election'] = election_data

                return redirect('elections:review_election')

            except Exception as e:
                form.add_error('voter_file', f"Error processing file: {str(e)}")

    else:
        form = VoterUploadForm()

    return render(request, 'add_voters.html', {'form': form})



@login_required
def review_election(request):
    election_data = request.session.get('election', None)

    if not election_data:
        # If there's no election data, go back to start
        return redirect('add_election')

    if request.method == 'POST':
        # Save the Election object
        election = Election.objects.create(
            user=request.user,
            title=election_data['title'],
            description=election_data['description'],
            use_blockchain=election_data['useBlockchain'],
        )

        # Mapping form voting types to model choice values
        VOTING_TYPE_MAPPING = {
            'first_past_the_post': 'FPP',
            'ranked_choice': 'RCV',
            'yes_no': 'YN'
        }

        # Save Ballots and Candidates
        ballots_data = election_data.get('ballots', [])
        for ballot_data in ballots_data:
            # Get the voting type as per the model's expected format
            voting_type = VOTING_TYPE_MAPPING.get(ballot_data['voting_type'])

            ballot = Ballot.objects.create(
                election=election,
                title=ballot_data['title'],
                voting_type=voting_type,
                number_of_winners=ballot_data['number_of_winners']
            )

            # Save Candidates for each ballot
            candidates_data = ballot_data.get('candidates', [])
            for candidate_name in candidates_data:
                Candidate.objects.create(
                    ballot=ballot,
                    title=candidate_name
                )

        # Save Voters
        voters_data = election_data.get('voters', [])
        for voter_data in voters_data:
            Voter.objects.create(
                election=election,
                name=voter_data['name'],
                email=voter_data['email']
            )

        # Clear the session after saving
        request.session.pop('election')
        return redirect('dashboard')  # Redirect after saving

    return render(request, 'review_election.html', {'election_data': election_data})



