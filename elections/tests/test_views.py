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
        """Test that dashboard redirects if user is not logged in."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertTrue(response.url.startswith("/accounts/login/"))  # Check redirect URL

    def test_dashboard_loads_for_logged_in_user(self):
        """Test that the dashboard page loads for authenticated users."""
        self.client.login(username="testuser", password="testpass")  # Log in
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)  # Page loads successfully
        self.assertTemplateUsed(response, "dashboard.html")  # Correct template used

    def test_dashboard_shows_user_elections(self):
        """Test that only the logged-in user's elections are displayed."""
        self.client.login(username="testuser", password="testpass")

        # Create elections for this user
        Election.objects.create(user=self.user, title="User Election", description="Test election")

        # Create elections for another user
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        Election.objects.create(user=other_user, title="Other Election", description="Should not be visible")

        response = self.client.get(self.dashboard_url)
        self.assertContains(response, "User Election")  # User's election should be there
        self.assertNotContains(response, "Other Election")  # Other user's election should not appear


class ManageElectionViewTest(TestCase):

    def setUp(self):
        """Set up test client, user, and an election."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(
            user=self.user, title="Test Election", description="A test election."
        )
        self.url = reverse("manage_election", args=[self.election.id])  # Ensure the name matches urls.py

    ### ✅ TEST ACCESS CONTROL ###
    def test_redirect_if_not_logged_in(self):
        """Test that the view redirects if user is not logged in."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith("/accounts/login/"))  # Default Django login redirect

    def test_404_if_election_does_not_belong_to_user(self):
        """Test that another user cannot manage this election."""
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)  # Should return 404 since election belongs to a different user

    ### ✅ TEST PAGE LOAD ###
    def test_manage_election_page_loads(self):
        """Test that the page loads successfully for the election owner."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "manage_election.html")
        self.assertContains(response, "Test Election")  # Ensure election title appears

    ### ✅ TEST POST ACTIONS ###
    @patch("elections.views.sendAllEmails_async.delay")  # Mock the email sending task
    def test_start_election(self, mock_send_emails):
        """Test starting an election updates status and sends emails."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "start"})
        self.election.refresh_from_db()
        self.assertEqual(self.election.status, "active")
        self.assertIsNotNone(self.election.start_time)
        mock_send_emails.assert_called_once_with(self.election.id)  # Ensure email task is triggered
        self.assertRedirects(response, self.url)  # Redirects back to manage page

    def test_end_election(self):
        """Test ending an election updates status."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "end"})
        self.election.refresh_from_db()
        self.assertEqual(self.election.status, "completed")
        self.assertIsNotNone(self.election.end_time)
        self.assertRedirects(response, self.url)

    def test_restart_election_creates_new_election(self):
        """Test restarting an election creates a new one."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "restart"})
        new_election = Election.objects.exclude(id=self.election.id).first()
        self.assertIsNotNone(new_election)
        self.assertEqual(new_election.title, self.election.title)
        self.assertRedirects(response, reverse("manage_election", args=[new_election.id]))

    def test_delete_election(self):
        """Test deleting an election removes it from the database."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.url, {"action": "delete"})
        with self.assertRaises(Election.DoesNotExist):
            Election.objects.get(id=self.election.id)
        self.assertRedirects(response, reverse("dashboard"))  # Ensure redirect to dashboard after delete



class ViewResultsTest(TestCase):
    def setUp(self):
        """Set up test client, user, and ballots with different voting types."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.election = Election.objects.create(user=self.user, title="Test Election")

        # Create FPP Ballot
        self.fpp_ballot = Ballot.objects.create(
            election=self.election, title="FPP Ballot", voting_type="FPP", results_data={"1": 10, "2": 5}
        )
        Candidate.objects.create(ballot=self.fpp_ballot, title="Alice")
        Candidate.objects.create(ballot=self.fpp_ballot, title="Bob")

        # Create YN Ballot
        self.yn_ballot = Ballot.objects.create(
            election=self.election, title="YN Ballot", voting_type="YN", results_data={"yes": 20, "no": 10}
        )

        # Create RCV Ballot
        self.rcv_ballot = Ballot.objects.create(
            election=self.election, title="RCV Ballot", voting_type="RCV", results_data={
                "quota": 12,
                "winners": ["Alice"],
                "rounds": [{"round_number": 1, "initial_votes": {"1": 5, "2": 3}}],
            }
        )
        Candidate.objects.create(ballot=self.rcv_ballot, title="Alice")
        Candidate.objects.create(ballot=self.rcv_ballot, title="Bob")

    ### ✅ TEST ACCESS CONTROL ###
    def test_redirect_if_not_logged_in(self):
        """Test that the results page redirects if user is not logged in."""
        response = self.client.get(reverse("view_results", args=[self.fpp_ballot.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith("/accounts/login/"))  # Check redirect URL

    def test_404_if_ballot_does_not_belong_to_user(self):
        """Test that another user cannot view results for this ballot."""
        other_user = User.objects.create_user(username="otheruser", password="otherpass")
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(reverse("view_results", args=[self.fpp_ballot.id]))
        self.assertEqual(response.status_code, 404)  # Should return 404

    ### ✅ TEST VIEW RESULTS FUNCTIONALITY ###
    def test_view_results_fpp(self):
        """Test that FPP results load correctly and use the correct template."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("view_results", args=[self.fpp_ballot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "view_results_FPP.html")
        self.assertContains(response, "FPP Ballot")  # Ensure ballot title appears
        self.assertContains(response, "Alice")  # Ensure candidate appears
        self.assertContains(response, "Bob")




