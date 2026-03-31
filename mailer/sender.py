"""
email/sender.py — Gmail SMTP sender.

Requires Gmail 2FA enabled and an App Password generated at:
https://myaccount.google.com/apppasswords
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date


def send_email(
    html_content: str,
    gmail_user: str,
    gmail_app_password: str,
    recipient: str,
) -> None:
    """
    Send the HTML newsletter via Gmail SMTP over SSL (port 465).
    Raises smtplib.SMTPException on delivery failure.
    """
    today = date.today().strftime("%B %d, %Y")
    subject = f"Morning Brief — {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html_content, "html"))

    print(f"Sending email to {recipient}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, recipient, msg.as_string())
    print("Email sent.")
