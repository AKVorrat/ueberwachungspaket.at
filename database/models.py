import datetime
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Date, DateTime
from . import Base

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False)
    time = Column(Integer)
    date_added = Column(Date, nullable=False)
    last_called = Column(DateTime)
    times_called = Column(Integer, nullable=False)
    times_forwarded = Column(Integer, nullable=False)
    time_connected = Column(Integer, nullable=False)

    def __init__(self, phone_number, time=None):
        self.phone_number = phone_number
        self.time = time
        self.date_added = datetime.date.today()
        self.last_called = None
        self.times_called = 0
        self.times_forwarded = 0
        self.time_connected = 0

    def __repr__(self):
        return "<Reminder for {}>".format(self.phone_number)

class Mail(Base):
    __tablename__ = "mails"
    id = Column(Integer, primary_key=True)
    mail_from = Column(String(254))
    name_from = Column(String(256))
    mail_to = Column(String(254))
    hash = Column(String(64))
    date_requested = Column(DateTime)
    date_sent = Column(DateTime)

    def __init__(self, mail_from, name_from, mail_to):
        self.mail_from = mail_from
        self.name_from = name_from
        self.mail_to = mail_to
        self.hash = uuid4.hex
        self.date_requested = datetime.today()
        self.date_sent = None
