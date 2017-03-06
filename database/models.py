#-*- coding: utf-8 -*-

from datetime import datetime, date
from json import load
from random import choice
from uuid import uuid4
from smtplib import SMTP
from email.mime.text import MIMEText
from flask import url_for
from sqlalchemy import UniqueConstraint, Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import MAIL_FROM, MAIL_DEBUG
from config.main import DEBUG
from config.mail import *
from . import Base

def sendmail(addr_from, addr_to, subject, msg):
    mail = MIMEText(msg)
    mail["Subject"] = subject
    mail["From"] = addr_from
    mail["To"] = addr_to

    with SMTP("localhost") as s:
        s.sendmail(mail)

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

        addr_from = MAIL_FROM + " <" + MAIL_FROM + ">"
        if DEBUG:
            addr_to = MAIL_DEBUG + " <" + MAIL_DEBUG + ">"
        else:
            addr_to = str(rep) + " <" + rep.contact.mail + ">"
        subject = "Sicherheitspaket"
        salutation = "Sehr geehrter Herr" if rep.sex == "male" else "Sehr geehrte Frau"
        msg = MAIL_DISCLAIMER.format(name_user=self.sender.name, mail_user=self.sender.email_address) + "\n" * 2
        msg = msg + MAIL_REPRESENTATIVE.format(name_rep=str(rep), name_user=self.sender.name, salutation=salutation)
        sendmail(addr_from, addr_to, subject, msg)

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

        addr_from = MAIL_FROM + " <" + MAIL_FROM + ">"
        addr_to = self.name + " <" + self.email_address + ">"
        subject = "Vielen Dank für Ihre Teilnahme auf überwachungspaket.at"
        msg = MAIL_WELCOME.format(name_user=self.name)
        sendmail(addr_from, addr_to, subject, msg)

    def request_validation(self):
        self.hash = uuid4().hex
        self.date_requested = datetime.now()

        addr_from = MAIL_FROM + " <" + MAIL_FROM + ">"
        addr_to = self.name + " <" + self.email_address + ">"
        subject = "Bestätigung für überwachungspaket.at"
        url = url_for("validate", hash=self.hash, _external=True)
        msg = MAIL_VALIDATE.format(name_user=self.name, url=url)
        sendmail(addr_from, addr_to, msg)

class Representatives():
    def __init__(self):
        self.parties = load_parties()
        self.teams = load_teams()
        self.representatives = load_representatives("representatives.json", self.parties, self.teams)
        self.government = load_representatives("government.json", self.parties, self.teams)

    def get_representative_by_id(self, id):
        representatives = self.representatives + self.government
        if id == "00000":
            return choice([rep for rep in representatives if rep.team.prettyname == "spy"])

        try:
            rep = [rep for rep in representatives if rep.id == id][0]
        except IndexError:
            rep = None
        return rep

    def get_representative_by_name(self, prettyname):
        representatives = self.representatives + self.government
        try:
            rep = [rep for rep in representatives if rep.name.prettyname == prettyname][0]
        except IndexError:
            rep = None
        return rep

    def get_party(self, shortname):
        return self.parties[shortname]

class Contact():
    def __init__(self, mail, phone, facebook, twitter):
        self.mail = mail
        self.phone = phone
        self.facebook = facebook
        self.twitter = twitter

class Party():
    def __init__(self, name, shortname, prettyname, color, contact):
        self.name = name
        self.shortname = shortname
        self.prettyname = prettyname
        self.color = color
        self.contact = contact

class Name():
    def __init__(self, firstname, lastname, prettyname, prefix, suffix):
        self.firstname = firstname
        self.lastname = lastname
        self.prettyname = prettyname
        self.prefix = prefix
        self.suffix = suffix

class Image():
    def __init__(self, url, copyright):
        self.url = url
        self.copyright = copyright

class Team():
    def __init__(self, name, prettyname):
        self.name = name
        self.prettyname = prettyname

    def __repr__(self):
        return self.name

class Representative():
    def __init__(self, id, name, contact, image, party, team, sex, state):
        self.id = id
        self.name = name
        self.contact = contact
        self.image = image
        self.party = party
        self.team = team
        self.sex = sex
        self.state = state

        if not self.contact.mail:
            self.contact.mail = party.contact.mail
        if not self.contact.phone:
            self.contact.phone = party.contact.phone
        if not self.contact.facebook:
            self.contact.facebook = party.contact.facebook
        if not self.contact.twitter:
            self.contact.twitter = party.contact.twitter

    def __repr__(self):
        return self.name.firstname + " " + self.name.lastname

    def fullname(self):
        return (self.name.prefix + " " if self.name.prefix else "") + self.name.firstname + " " + self.name.lastname + (" " + self.name.suffix if self.name.suffix else "")

def load_parties():
    parties = {}

    with open("ueberwachungspaket/data/parties.json", "r") as f:
        lparties = load(f)

    for prettyname in lparties:
        lparty = lparties[prettyname]
        lcontact = lparty["contact"]
        contact = Contact(lcontact["mail"], lcontact["phone"], lcontact["facebook"], lcontact["twitter"])
        party = Party(lparty["name"], lparty["shortname"], prettyname, lparty["color"], contact)
        parties[prettyname] = party

    return parties

def load_teams():
    teams = {}

    with open("ueberwachungspaket/data/teams.json", "r") as f:
        lteams = load(f)

    for prettyname in lteams:
        lteam = lteams[prettyname]
        team = Team(lteam["name"], prettyname)
        teams[prettyname] = team

    return teams

def load_representatives(filename, parties, teams):
    representatives = []

    with open("ueberwachungspaket/data/" + filename, "r") as f:
        lrepresentatives = load(f)

    for lrep in lrepresentatives:
        lname = lrep["name"]
        name = Name(lname["firstname"], lname["lastname"], lname["prettyname"], lname["prefix"], lname["suffix"])
        lcontact = lrep["contact"]
        contact = Contact(lcontact["mail"], lcontact["phone"], lcontact["facebook"], lcontact["twitter"])
        image = Image(lrep["image"]["url"], lrep["image"]["copyright"])
        party = parties[lrep["party"]]
        team = teams[lrep["team"]]
        representative = Representative(lrep["id"], name, contact, image, party, team, lrep["sex"], lrep["state"])
        representatives.append(representative)

    return representatives

reps = Representatives()
