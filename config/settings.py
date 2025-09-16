import os
from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SITE_URL = os.getenv("SITE_URL")
# Credentials
USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")


# Screenshot + HTML dump toggle
SAVE_DEBUG = os.getenv("SAVE_DEBUG", "true").lower() in ("true", "1", "yes")

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

