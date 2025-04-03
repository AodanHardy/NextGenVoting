from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from voting.models import Ballot, Candidate
from elections.models import Election


class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.dashboard_url = reverse("dashboard")

    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_dashboard_loads_for_logged_in_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard.html")

    def test_dashboard_shows_user_elections(self):
        self.client.login(username="testuser", password="testpass")

        # create elections for this user
        Election.objects.create(user=self.user, title="User Election", description="Test election")

        # create elections for another user
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        Election.objects.create(user=other_user, title="Other Election", description="Should not be visible")

        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "User Election")
        self.assertNotContains(response, "Other Election")


class ManageElectionViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(
            user=self.user, title="Test Election", description="A test election."
        )
        self.url = reverse("manage_election", args=[self.election.id])

    # TEST ACCESS CONTROL
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_404_if_election_does_not_belong_to_user(self):
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    # TEST PAGE LOAD
    def test_manage_election_page_loads(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_election.html")
        self.assertContains(response, "Test Election")

    # TEST POST ACTIONS
    @patch("elections.views.sendAllEmails_async.delay")
    def test_start_election(self, mock_send_emails):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "start"})
        self.election.refresh_from_db()
        self.assertEqual(self.election.status, "active")
        self.assertIsNotNone(self.election.start_time)
        mock_send_emails.assert_called_once_with(self.election.id)
        self.assertRedirects(response, self.url)

    def test_end_election(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "end"})
        self.election.refresh_from_db()
        self.assertEqual(self.election.status, "completed")
        self.assertIsNotNone(self.election.end_time)
        self.assertRedirects(response, self.url)

    def test_restart_election_creates_new_election(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "restart"})
        new_election = Election.objects.exclude(id=self.election.id).first()
        self.assertIsNotNone(new_election)
        self.assertEqual(new_election.title, self.election.title)
        self.assertRedirects(response, reverse("manage_election", args=[new_election.id]))

    def test_delete_election(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "delete"})
        with self.assertRaises(Election.DoesNotExist):
            Election.objects.get(id=self.election.id)
        self.assertRedirects(response, reverse("dashboard"))



class ViewResultsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(user=self.user, title="Test Election")

        # FPP Ballot
        self.fpp_ballot = Ballot.objects.create(
            election=self.election, title="FPP Ballot", voting_type="FPP", results_data={"1": 10, "2": 5}
        )
        Candidate.objects.create(ballot=self.fpp_ballot, title="Alice")
        Candidate.objects.create(ballot=self.fpp_ballot, title="Bob")

        # YN Ballot
        self.yn_ballot = Ballot.objects.create(
            election=self.election, title="YN Ballot", voting_type="YN", results_data={"yes": 20, "no": 10}
        )

        # RCV Ballot
        self.rcv_ballot = Ballot.objects.create(
            election=self.election, title="RCV Ballot", voting_type="RCV", results_data={
                "quota": 12,
                "winners": ["Alice"],
                "rounds": [{"round_number": 1, "initial_votes": {"1": 5, "2": 3}}],
            }
        )
        Candidate.objects.create(ballot=self.rcv_ballot, title="Alice")
        Candidate.objects.create(ballot=self.rcv_ballot, title="Bob")

    # TEST ACCESS CONTROL
    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("view_results", args=[self.fpp_ballot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_404_if_ballot_does_not_belong_to_user(self):
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(reverse("view_results", args=[self.fpp_ballot.id]))
        self.assertEqual(response.status_code, 404)






