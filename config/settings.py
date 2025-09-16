import os
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SITE_URL = os.getenv("SITE_URL")
# Credentials
EMAIL = os.getenv("EMAIL", "")
PASSWORD = os.getenv("PASSWORD", "")

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

