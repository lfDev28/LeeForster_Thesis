import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Notification:
    def __init__(self):
        self.sender_email = os.getenv("EMAIL_ADDRESS")
        self.app_password = os.getenv("EMAIL_APP_PASSWORD")


    def send_email(self, recipient, subject, body):
        # Set up the email content
        if not recipient or recipient == "":
            raise Exception("No recipient email provided")
        
        if not subject or subject == "":
            raise Exception("No subject provided")
        
        if not body or body == "":
            raise Exception("No body provided")
            

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = recipient

        # Connect to the Gmail SMTP server and send the email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.sender_email, self.app_password)
                smtp.send_message(msg)
            print(f"Email sent to {recipient}!")
        except Exception as e:
            print(f"Failed to send email: {e}")
