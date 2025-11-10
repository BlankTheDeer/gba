# ?? Async Email Sender for BlankTB Portal
import smtplib
from email.message import EmailMessage
from app.core.config import settings

async def send_email(to_email: str, subject: str, html_content: str):
    msg = EmailMessage()
    msg["From"] = settings.MAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("This email requires HTML support.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.MAIL_USER, settings.MAIL_PASS)
            smtp.send_message(msg)
        print(f"Sent email to {to_email}")
    except Exception as e:
        print(f"Email error: {e}")
