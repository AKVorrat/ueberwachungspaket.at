#-*- coding: utf-8 -*-

from datetime import datetime, date
from json import load
from random import choice
from uuid import uuid4
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import url_for
from sqlalchemy import UniqueConstraint, Column, Boolean, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from config import DEBUG, MAIL_FROM, MAIL_DEBUG
from config.mail import *
from . import Base

def sendmail(addr_from, addr_to, subject, msg, attachment=None, attachment_name=None):
    if not attachment:
        mail = MIMEText(msg)
    else:
        mail = MIMEMultipart()
        mail.attach(MIMEText(msg))
        app = MIMEApplication(attachment)
        app['Content-Disposition'] = 'attachment; filename="%s"' % attachment_name
        mail.attach(app)

    mail["Subject"] = subject
    mail["From"] = addr_from
    if type(addr_to) == str:
        mail["To"] = addr_to
    else:
        mail["To"] = ', '.join(addr_to)

    with SMTP("localhost") as s:
        s.send_message(mail)

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

        addr_from = '"' + MAIL_FROM + '" <' + MAIL_FROM + '>'
        if DEBUG:
            addr_to = '"' + MAIL_DEBUG + '" <' + MAIL_DEBUG + '>'
        else:
            addr_to = str(rep) + " <" + rep.contact.mail + ">"
        subject = "Sicherheitspaket"
        msg = MAIL_DISCLAIMER.format(name_user=self.sender.name, mail_user=self.sender.email_address) + "\n" * 2
        msg = msg + MAIL_REPRESENTATIVE.format(name_rep=str(rep), name_user=self.sender.name, salutation=rep.salutation)
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
    newsletter = Column(Boolean(False), nullable=False)

    def __init__(self, name, email_address, newsletter=False):
        self.name = name
        self.email_address = email_address
        self.request_validation()
        self.newsletter = newsletter

    def validate(self):
        self.date_validated = datetime.now()

        addr_from = '"' + MAIL_FROM + '" <' + MAIL_FROM + '>'
        addr_to = self.name + " <" + self.email_address + ">"
        subject = "Vielen Dank für Ihre Teilnahme auf überwachungspaket.at"
        msg = MAIL_WELCOME.format(name_user=self.name)
        sendmail(addr_from, addr_to, subject, msg)

    def request_validation(self):
        self.hash = uuid4().hex
        self.date_requested = datetime.now()

        addr_from = '"' + MAIL_FROM + '" <' + MAIL_FROM + ">"
        addr_to = self.name + " <" + self.email_address + ">"
        subject = "Bestätigung für überwachungspaket.at"
        url = url_for("validate", hash=self.hash, _external=True)
        msg = MAIL_VALIDATE.format(name_user=self.name, url=url)
        sendmail(addr_from, addr_to, subject, msg)

class Representatives():
    def __init__(self):
        self.parties = load_parties()
        self.teams = load_teams()
        self.representatives = load_representatives("representatives.json", self.parties, self.teams)
        self.government = load_representatives("government.json", self.parties, self.teams, True)

    def get_representative_by_id(self, id):
        representatives = self.representatives + self.government
        if id == "00000":
            return choice([rep for rep in representatives if rep.important])

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
    def __init__(self, handle, name, shortname, prettyname, color, contact):
        self.handle = handle
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
    def __init__(self, id, name, contact, image, party, team, sex, important, salutation, state, is_government):
        self.id = id
        self.name = name
        self.contact = contact
        self.image = image
        self.party = party
        self.team = team
        self.sex = sex
        self.is_male = sex == 'male'
        self.is_female = sex == 'female'
        self.important = important
        self.salutation = salutation
        self.state = state
        self.is_government = is_government

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
        party = Party(prettyname, lparty["name"], lparty["shortname"], prettyname, lparty["color"], contact)
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

def load_representatives(filename, parties, teams, is_government=False):
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
        representative = Representative(lrep["id"], name, contact, image, party, team, lrep["sex"], lrep["important"], lrep["salutation"], lrep["state"], is_government)
        representatives.append(representative)

    return representatives

reps = Representatives()


def load_consultation_issues():
    with open("ueberwachungspaket/data/consultation_issues.json", "r") as f:
        consultation_issues = load(f)
    return consultation_issues

class ConsultationSender(Base):
    __tablename__ = "consultation_senders"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(256), nullable=False)
    last_name = Column(String(256), nullable=False)
    email_address = Column(String(254), unique=True, nullable=False)
    bmi_text = Column(Text)
    bmj_text = Column(Text)
    confidential_submission = Column(Boolean(True), nullable=False)
    hash = Column(String(64), unique=True, nullable=False)
    date_validated = Column(DateTime)
    date_requested = Column(DateTime, nullable=False)
    newsletter = Column(Boolean(False), nullable=False)

    def __init__(self, first_name, last_name, email_address, bmi_text, bmj_text, confidential_submission, newsletter=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.bmi_text = bmi_text
        self.bmj_text = bmj_text
        self.confidential_submission = confidential_submission
        self.request_validation()
        self.newsletter = newsletter

    def validate(self):
        self.date_validated = datetime.now()

    def request_validation(self):
        self.hash = uuid4().hex
        self.date_requested = datetime.now()

        addr_from = '"' + MAIL_FROM + '" <' + MAIL_FROM + '>'
        addr_to = '"' + self.first_name + ' ' + self.last_name + '" <' + self.email_address + '>'
        subject = "Bestätigung für überwachungspaket.at"
        url = url_for("consultation_complete", hash=self.hash, _external=True)
        msg = CONSULTATION_MAIL_VALIDATE.format(first_name=self.first_name, last_name=self.last_name, url=url)
        sendmail(addr_from, addr_to, subject, msg)

class Opinion(Base):
    __tablename__ = "opinions"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    logo_filename = Column(String(256))
    date = Column(Date, nullable=False)
    link_bmi_parliament = Column(String(256))
    link_bmi_pdf = Column(String(256))
    originality_bmi = Column(Integer, nullable=False)
    link_bmj_parliament = Column(String(256))
    link_bmj_pdf = Column(String(256))
    originality_bmj = Column(Integer, nullable=False)
    addresses_bundestrojaner = Column(Boolean, nullable=False)
    addresses_netzsperren = Column(Boolean, nullable=False)
    addresses_vds_video = Column(Boolean, nullable=False)
    addresses_ueberwachung_strassen = Column(Boolean, nullable=False)
    addresses_vds_quickfreeze = Column(Boolean, nullable=False)
    addresses_anonyme_simkarten = Column(Boolean, nullable=False)
    addresses_imsi_catcher = Column(Boolean, nullable=False)
    addresses_lauschangriff_auto = Column(Boolean, nullable=False)
    comment = Column(Text)

    def __init__(self,
                 name,
                 logo_filename,
                 date,
                 link_bmi_parliament,
                 link_bmi_pdf,
                 originality_bmi,
                 link_bmj_parliament,
                 link_bmj_pdf,
                 originality_bmj,
                 addresses_bundestrojaner,
                 addresses_netzsperren,
                 addresses_vds_video,
                 addresses_ueberwachung_strassen,
                 addresses_vds_quickfreeze,
                 addresses_anonyme_simkarten,
                 addresses_imsi_catcher,
                 addresses_lauschangriff_auto,
                 comment):
        self.name = name
        self.logo_filename = logo_filename
        self.date = date
        self.link_bmi_parliament = link_bmi_parliament
        self.link_bmi_pdf = link_bmi_pdf
        self.originality_bmi = originality_bmi
        self.link_bmj_parliament = link_bmj_parliament
        self.link_bmj_pdf = link_bmj_pdf
        self.originality_bmj = originality_bmj
        self.addresses_bundestrojaner = addresses_bundestrojaner
        self.addresses_netzsperren = addresses_netzsperren
        self.addresses_vds_video = addresses_vds_video
        self.addresses_ueberwachung_strassen = addresses_ueberwachung_strassen
        self.addresses_vds_quickfreeze = addresses_vds_quickfreeze
        self.addresses_anonyme_simkarten = addresses_anonyme_simkarten
        self.addresses_imsi_catcher = addresses_imsi_catcher
        self.addresses_lauschangriff_auto = addresses_lauschangriff_auto
        self.comment = comment

    @hybrid_property
    def originality(self):
        return (self.originality_bmi + self.originality_bmj) / 2

    def date_pretty(self):
        return "{}.{}.{}".format(self.date.day, self.date.month, self.date.year)

    def originality_pretty(self):
        return int(self.originality)

    def serialize(self):
        return {
            "logoFilename": self.logo_filename,
            "name": self.name,
            "date": self.date_pretty(),
            "linkBmiParliament": self.link_bmi_parliament,
            "linkBmiPdf": self.link_bmi_pdf,
            "linkBmjParliament": self.link_bmj_parliament,
            "linkBmjPdf": self.link_bmj_pdf,
            "addresses": "",
            "originality": self.originality,
            "comment": self.comment
        }
