from django.test import TestCase
from django.contrib.auth.models import User
from elections.models import Election


class ElectionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(
            user=self.user,
            title="Test Election",
            description="This is a test election.",
        )

    def test_election_creation(self):
        self.assertEqual(self.election.title, "test election")
        self.assertEqual(self.election.description, "test election.")
        self.assertEqual(self.election.status, "pending")
        self.assertEqual(self.election.use_blockchain, False)
        self.assertEqual(self.election.votes_cast, 0)

    def test_election_defaults(self):
        self.assertIsNone(self.election.start_time)
        self.assertIsNone(self.election.end_time)
        self.assertFalse(self.election.results_published)

    def test_election_status_choices(self):
        self.election.status = "active"
        self.election.save()
        self.assertEqual(self.election.status, "active")

        self.election.status = "completed"
        self.election.save()
        self.assertEqual(self.election.status, "completed")

    def test_foreign_key_relationship(self):
        self.assertEqual(self.election.user.username, "testuser")

    def test_auto_now_fields(self):
        self.assertIsNotNone(self.election.created_at)
        self.assertIsNotNone(self.election.updated_at)

    def test_use_blockchain_enabled(self):
        self.election.use_blockchain = True
        self.election.save()
        self.assertTrue(self.election.use_blockchain)

    def test_publish_results(self):
        self.election.results_published = True
        self.election.save()
        self.assertTrue(self.election.results_published)
