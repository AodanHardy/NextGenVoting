from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ElectionDetailsForm, BallotForm, CandidatesForm
from .models import Election
from voting.models import Ballot, Candidate, Voter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

import csv
from .forms import VoterUploadForm
from .utils import VoterData
from .utils import ElectionData, BallotData


# Create your views here.

@login_required
def dashboard(request):
    user_elections = Election.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'elections': user_elections})


def election_details(request):
    # need to Clear data from previous session

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
    # Retrieve the current ballot, and voting type from the session
    current_ballot = request.session.get('currentBallot')
    election_data = request.session.get('election')

    if not current_ballot or not election_data:
        return redirect('elections:add_ballots')  # Redirect back if there's no ballot data

    if request.method == 'POST':
        form = CandidatesForm(request.POST)
        if form.is_valid():
            # Get the candidates from the form, split by commas, and clean them up
            candidates_str = form.cleaned_data['candidates']
            candidate_list = [candidate.strip() for candidate in candidates_str.split(',') if candidate.strip()]

            # Get number of winners
            num_of_winners = form.cleaned_data['number_of_winners']
            if num_of_winners is None:
                num_of_winners = 1
            current_ballot['number_of_winners'] = num_of_winners

            # Add candidates to the current ballot
            current_ballot['candidates'].extend(candidate_list)

            # Update the session with the current ballot
            request.session['currentBallot'] = current_ballot

            # Logic to move to the next ballot
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
        return redirect('add_election')  # If no election data, go back to start

    if request.method == 'POST':
        # Save the Election object
        election = Election.objects.create(
            user=request.user,
            title=election_data['title'],
            description=election_data['description'],
            start_time=election_data['start_time'],
            end_time=election_data['end_time'],
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



@login_required
def save_election(request):
    pass
