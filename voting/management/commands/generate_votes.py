import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from elections.models import Election
from voting.management.commands.rcv_vote_generator import generateRcvVotes
from voting.models import Ballot, Candidate, Vote


class Command(BaseCommand):
    help = "Generate a large number of votes for testing"

    def add_arguments(self, parser):
        parser.add_argument('num_votes', type=int, help="Number of votes to generate")
        parser.add_argument('num_candidates', type=int, help="Number of Candidates max 15")
        parser.add_argument('num_winners', type=int, help="Number of winners")

    def handle(self, *args, **options):
        num_votes = options['num_votes']
        num_candidates = options['num_candidates']
        if options['num_winners']:
            num_winners = options['num_winners']
        else:
            num_winners = 1

        superuser = User.objects.get(id=1)

        # Create an election
        election = Election.objects.create(title="Generated Election",
                                           use_blockchain=False,
                                           description="Generated Test Election",
                                           user=superuser,
                                           )

        # Create a ballot
        ballot = Ballot.objects.create(election=election,
                                       title="test ballot",
                                       voting_type="RCV",
                                       number_of_winners=num_winners,
                                       )

        # Create candidates
        candidateNames = ["Michael", "Jim", "Dwight", "Andy", "Oscar", "Creed", "Angela", "Pam",
                          "Toby", "Stanley", "Kevin", "Meredith", "Phyllis", "Ryan", "Jan"]

        newNumber = num_candidates

        userCandidates = random.sample(candidateNames, newNumber)

        candidates = [
            Candidate.objects.create(ballot=ballot, title=userCandidates[i]) for i in range(len(userCandidates))
        ]

        candidatesDict = {}

        for candidate in candidates:
            candidatesDict[candidate.id] = candidate.title



        # Simulate votes
        votes = generateRcvVotes(candidatesDict, num_votes)


        # Bulk insert votes

        for i in range(len(votes)):
            Vote.objects.create(ballot_id=ballot.id, vote_data=votes[i])

        election.status = "active"
        election.save()


        self.stdout.write(self.style.SUCCESS(f"Successfully generated {num_votes} votes!"))
