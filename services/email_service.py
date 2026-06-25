import smtplib
from email.mime.text import MIMEText
from core.config import settings


def send_otp_email(email: str, otp: str):

    subject = "OTP Verification"

    body = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.

Thank you.
"""

    message = MIMEText(body)

    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = email


    with smtplib.SMTP(
        settings.SMTP_SERVER,
        settings.SMTP_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.EMAIL_USERNAME,
            settings.EMAIL_PASSWORD
        )

        server.send_message(message)