import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.template.loader import render_to_string

from celery import shared_task

from elections.models import Election
from nextgenvoting.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST, EMAIL_PORT
from voting.models import Voter




@shared_task
def sendAllEmails_async(electionId):
    emailManager = EmailManager(electionId)
    emailManager.send_emails_to_all_voters()


class EmailManager:
    """
    sends emails to all voters of an election.
    """

    def __init__(self, election_id):
        self.election = Election.objects.get(id=election_id)
        self.email_user = EMAIL_HOST_USER
        self.email_password = EMAIL_HOST_PASSWORD
        self.EMAIL_HOST = EMAIL_HOST
        self.EMAIL_PORT = EMAIL_PORT

    def get_voters(self):
        try:
            return Voter.objects.filter(election_id=self.election.id)
        except Exception as e:
            print(f"Error retrieving voters: {e}")
            return []

    def send_email(self, voter):

        # make the link here
        unique_link = f"http://localhost:8000/vote/{voter.id}/"

        subject = f"Vote now in {self.election.title}"

        context = {'name': voter.name, 'election_name': self.election.title, 'link': unique_link}
        body = render_to_string('email_template.html', context=context)

        msg = MIMEMultipart()
        msg['From'] = self.email_user
        msg['To'] = voter.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            # Connect to the server
            server = smtplib.SMTP(self.EMAIL_HOST, self.EMAIL_PORT)
            server.starttls()
            server.login(self.email_user, self.email_password)

            # Send the email
            server.sendmail(self.email_user, voter.email, msg.as_string())
            return True
        except Exception as e:
            print(f"Failed to send email to {voter.email}: {e}")
            return False
        finally:
            server.quit()

    def send_emails_to_all_voters(self):
        voters = self.get_voters()
        if not voters:
            print("No voters found")
            return

        for voter in voters:
            success = self.send_email(voter)
            if success:
                print(f"Email sent to {voter.name} ({voter.email})")
            else:
                print(f"Failed to send email to {voter.name} ({voter.email})")
