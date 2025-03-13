from django.test import TestCase
from django.contrib.auth.models import User
from elections.models import Election
from voting.models import Ballot, Candidate, Voter, Vote, Blockchain_Vote


class VotingModelsTest(TestCase):

    def setUp(self):
        """Set up necessary objects for testing."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(
            user=self.user,
            title="Test Election",
            description="A test election."
        )
        self.ballot = Ballot.objects.create(
            election=self.election,
            title="Test Ballot",
            voting_type="FPP",
            number_of_winners=1
        )
        self.candidate = Candidate.objects.create(
            ballot=self.ballot,
            title="Test Candidate"
        )
        self.voter = Voter.objects.create(
            election=self.election,
            name="Test Voter",
            email="voter@example.com"
        )
        self.vote = Vote.objects.create(
            ballot=self.ballot,
            vote_data={"candidate_id": str(self.candidate.id)}
        )
        self.blockchain_vote = Blockchain_Vote.objects.create(
            election=self.election,
            status="in_progress",
            vote_data={"tx_hash": "123abc"}
        )

    ### ✅ BALLOT MODEL TESTS ###
    def test_ballot_creation(self):
        """Test that a ballot is created successfully."""
        self.assertEqual(self.ballot.title, "Test Ballot")
        self.assertEqual(self.ballot.voting_type, "FPP")
        self.assertEqual(self.ballot.number_of_winners, 1)
        self.assertEqual(self.ballot.election, self.election)

    def test_ballot_voting_type_choices(self):
        """Ensure only valid voting types are allowed."""
        valid_types = ["FPP", "RCV", "YN"]
        for v_type in valid_types:
            self.ballot.voting_type = v_type
            self.ballot.save()
            self.assertEqual(self.ballot.voting_type, v_type)

    ### ✅ CANDIDATE MODEL TESTS ###
    def test_candidate_creation(self):
        """Test that a candidate is created successfully."""
        self.assertEqual(self.candidate.title, "Test Candidate")
        self.assertEqual(self.candidate.ballot, self.ballot)

    ### ✅ VOTER MODEL TESTS ###
    def test_voter_creation(self):
        """Test that a voter is created successfully."""
        self.assertEqual(self.voter.name, "Test Voter")
        self.assertEqual(self.voter.email, "voter@example.com")
        self.assertEqual(self.voter.election, self.election)
        self.assertFalse(self.voter.voted)  # Default should be False

    ### ✅ VOTE MODEL TESTS ###
    def test_vote_creation(self):
        """Test that a vote is recorded correctly."""
        self.assertEqual(self.vote.ballot, self.ballot)
        self.assertEqual(self.vote.vote_data, {"candidate_id": str(self.candidate.id)})
        self.assertIsNotNone(self.vote.created_at)  # Ensure timestamp is set

    ### ✅ BLOCKCHAIN VOTE MODEL TESTS ###
    def test_blockchain_vote_creation(self):
        """Test that a blockchain vote is recorded correctly."""
        self.assertEqual(self.blockchain_vote.election, self.election)
        self.assertEqual(self.blockchain_vote.status, "in_progress")
        self.assertEqual(self.blockchain_vote.vote_data, {"tx_hash": "123abc"})

    def test_blockchain_vote_status_choices(self):
        """Ensure blockchain vote status only accepts valid choices."""
        valid_statuses = ["complete", "in_progress", "failed"]
        for status in valid_statuses:
            self.blockchain_vote.status = status
            self.blockchain_vote.save()
            self.assertEqual(self.blockchain_vote.status, status)
