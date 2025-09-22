import os
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SITE_URL = os.getenv("SITE_URL")
# Credentials
EMAIL = os.getenv("EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")
# Email Settings
SMTP_SERVER = os.getenv("SMTP_SERVER", "")
# SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
# Max login tries -> if fails
MAX_LOGIN_ATTEMPTS = os.getenv("MAX_LOGIN_ATTEMPTS")

# Screenshot + HTML dump toggle
SAVE_SCREENSHOTS = os.getenv("SAVE_SCREENSHOTS", "true").lower() in ("true", "1", "yes")

# Browser options
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
PROXY = os.getenv("PROXY", None)

# Login form selectors (configurable!)
LOGIN_EMAIL_SELECTORS = [
    {"by": "id", "value": "name"},
    {"by": "name", "value": "name"},
    {"by": "name", "value": "email"},
    {"by": "name", "value": "username"},
    {"by": "id", "value": "email"},
    {"by": "id", "value": "username"},
    {"by": "css", "value": "input[type='email']"},
    {"by": "css", "value": "input[name*='user']"},
]

LOGIN_PASSWORD_SELECTORS = [
    {"by": "name", "value": "password"},
    {"by": "id", "value": "password"},
    {"by": "css", "value": "input[type='password']"},
]

