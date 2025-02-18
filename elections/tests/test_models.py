from django.test import TestCase
from django.contrib.auth.models import User
from elections.models import Election


class ElectionModelTest(TestCase):

    def setUp(self):
        """Set up a test user and a test election."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(
            user=self.user,
            title="Test Election",
            description="This is a test election.",
        )

    def test_election_creation(self):
        """Test if an election can be created successfully."""
        self.assertEqual(self.election.title, "Test Election")
        self.assertEqual(self.election.description, "This is a test election.")
        self.assertEqual(self.election.status, "pending")  # Default status
        self.assertEqual(self.election.use_blockchain, False)  # Default value
        self.assertEqual(self.election.votes_cast, 0)  # Default value

    def test_election_str(self):
        """Test the string representation of the Election model."""
        self.assertEqual(str(self.election), "Test Election")

    def test_election_status_choices(self):
        """Test that status choices are valid."""
        self.election.status = "active"
        self.election.save()
        self.assertEqual(self.election.status, "active")

        self.election.status = "completed"
        self.election.save()
        self.assertEqual(self.election.status, "completed")

    def test_foreign_key_relationship(self):
        """Test that the election is linked to a user."""
        self.assertEqual(self.election.user.username, "testuser")

    def test_auto_now_fields(self):
        """Ensure auto_now_add and auto_now work correctly."""
        self.assertIsNotNone(self.election.created_at)
        self.assertIsNotNone(self.election.updated_at)
