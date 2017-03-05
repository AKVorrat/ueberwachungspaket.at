from datetime import datetime, date
from uuid import uuid4
from flask import url_for
from sqlalchemy import UniqueConstraint, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ueberwachungspaket import app, reps
from config import *
from . import Base

def sendmail(addr_from, addr_to, msg):
    if app.debug:
        app.logger.info("Sending mail from " + addr_from + " to " + addr_to + ".")
        app.logger.info(msg)
    else:
        server = SMTP("localhost")
        server.sendmail(addr_from, addr_to, msg)
        server.quit()

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
    sender_id = Column(Integer, ForeignKey("senders.id"))
    recipient = Column(String(5), nullable=False)
    date_sent = Column(DateTime)

    __table_args__ = tuple(
            UniqueConstraint(sender_id, recipient)
            )

    def __init__(self, sender, recipient):
        self.sender = sender
        self.recipient = recipient

    def send(self):
        self.date_sent = datetime.now()

        rep = reps.get_representative_by_id(self.recipient)

        addr_from = MAIL_FROM
        addr_to = str(rep) + " <" + rep.contact.mail + ">"
        salutation = "Sehr geehrter Herr" if rep.sex == "male" else "Sehr geehrte Frau"
        msg = app.config["MAIL_DISCLAIMER"].format(name_user=self.sender.name, mail_user=self.sender.email_address) + "\n" * 2
        msg = msg + app.config["MAIL_REPRESENTATIVE"].format(name_rep=str(rep), name_user=self.sender.name, salutation=salutation)
        sendmail(addr_from, addr_to, msg)

class Sender(Base):
    __tablename__ = "senders"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    email_address = Column(String(254), unique=True, nullable=False)
    mails = relationship("Mail", order_by="Mail.id", backref="sender")
    hash = Column(String(64), unique=True, nullable=False)
    date_validated = Column(DateTime)
    date_requested = Column(DateTime, nullable=False)

    def __init__(self, name, email_address):
        self.name = name
        self.email_address = email_address
        self.request_validation()

    def validate(self):
        self.date_validated = datetime.now()

        addr_from = MAIL_FROM
        addr_to = self.name + " <" + self.email_address + ">"
        msg = app.config["MAIL_WELCOME"].format(name_user=self.name)
        sendmail(addr_from, addr_to, msg)

    def request_validation(self):
        self.hash = uuid4().hex
        self.date_requested = datetime.now()

        addr_from = MAIL_FROM
        addr_to = self.name + " <" + self.email_address + ">"
        url = url_for("validate", hash=self.hash, _external=True)
        msg = app.config["MAIL_VALIDATE"].format(name_user=self.name, url=url)
        sendmail(addr_from, addr_to, msg)
