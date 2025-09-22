import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import SENDER_EMAIL, SMTP_SERVER, SENDER_PASSWORD, RECIPIENT_EMAIL

SMTP_PORT: int = 587

def send_email(subject: str, body: str):
    """Send email notification to one recipient."""
    try:
        msg = MIMEMultipart()
        if SENDER_EMAIL is None or RECIPIENT_EMAIL is None:
            raise ValueError("SENDER_EMAIL and RECIPIENT_EMAIL must not be None")
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        if SMTP_SERVER is None or SMTP_PORT is None:
            raise ValueError("SMTP_SERVER and SMTP_PORT must not be None")
        if SENDER_EMAIL is None or SENDER_PASSWORD is None:
            raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must not be None")
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"[📧] Email sent to {RECIPIENT_EMAIL}: {subject}")
    except Exception as e:
        print(f"[❌] Email sending failed: {e}")
