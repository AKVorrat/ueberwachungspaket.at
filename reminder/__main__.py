from random import choice
from time import sleep
from datetime import datetime, date
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_, cast, Date
from config import *
from database import db_session
from database.models import Reminder

try:
    client = TwilioRestClient(TWILIO_ACCOUNT, TWILIO_SECRET)
except TwilioRestException:
    exit(0)

hour = datetime.now().hour
today = date.today()

try:
    reminders = db_session.query(Reminder).filter(Reminder.time == hour, or_(Reminder.last_called == None, cast(Reminder.last_called, Date) != today)).all()
except NoResultFound:
    exit(0)

for reminder in reminders:
    try:
        client.calls.create(to = reminder.phone_number,
                            from_ = choice(TWILIO_NUMBERS),
                            url = CALLBACK_BASE_URL + "/act/gather-reminder-call/",
                            if_machine = "Hangup")
        reminder.last_called = datetime.now()
        reminder.times_called = reminder.times_called + 1
    except TwilioRestException:
        pass

    sleep(2)

db_session.commit()
db_session.remove()
