import os
import sendgrid
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "neharika.nln@ppreciate.com"  # use a verified sender in SendGrid

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)


def send_otp_email(receiver, otp):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=receiver,
        subject="Password Reset OTP",
        plain_text_content=f"Your OTP is {otp}. It is valid for 10 minutes."
    )
    try:
        response = sg.send(message)
        print("Email sent:", response.status_code)
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False
