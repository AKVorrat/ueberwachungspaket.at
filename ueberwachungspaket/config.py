import os

DEBUG = False

PROJECT_NAME = "Kontaktiere Deine Abgeordneten"

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
TWIML_APPLICATION_SID = os.environ.get("TWIML_APPLICATION_SID")
