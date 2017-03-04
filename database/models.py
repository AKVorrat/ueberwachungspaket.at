from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import UniqueConstraint, Column, Integer, String, Date, DateTime
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
        self.date_added = date.today()
        self.last_called = None
        self.times_called = 0
        self.times_forwarded = 0
        self.time_connected = 0

    def __repr__(self):
        return "<Reminder for {}>".format(self.phone_number)

class Mail(Base):
    __tablename__ = "mails"

    id = Column(Integer, primary_key=True)
    name_user = Column(String(256), nullable=False)
    mail_user = Column(String(254), nullable=False)
    rep_id = Column(String(5), nullable=False)
    hash = Column(String(64), nullable=False)
    date_requested = Column(DateTime, nullable=False)
    date_sent = Column(DateTime)

    __table_args__ = tuple(
            UniqueConstraint(mail_user, rep_id)
            )

    def __init__(self, name_user, mail_user, rep_id):
        self.name_user = name_user
        self.mail_user = mail_user
        self.rep_id = rep_id
        self.hash = uuid4().hex
        self.date_requested = datetime.today()
        self.date_sent = None
