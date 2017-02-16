from random import choice
from time import localtime, sleep
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from sqlalchemy.orm.exc import NoResultFound
from config import *
from database import db_session
from database.models import Reminder

client = TwilioRestClient(account = TWILIO_SID,
                          token = TWILIO_SECRET,
                          request_account = TWILIO_ACCOUNT)
hour = localtime().tm_hour

try:
    reminders = db_session.query(Reminder).filter_by(time = hour)
except NoResultFound:
    exit(0)

for reminder in reminders:
    try:
        client.calls.create(to = reminder.number,
                            from_ = choice(TWILIO_NUMBERS),
                            url = "https://beta.xn--berwachungspaket-izb.at/act/gather-reminder-call/")
    except TwilioRestException:
        pass

    sleep(3)


db_session.remove()
