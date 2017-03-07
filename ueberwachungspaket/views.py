from flask import render_template, abort, request, url_for, flash, redirect
from random import choice
from datetime import datetime, date, timedelta
from twilio.twiml import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from config import *
from config.main import *
from database.models import Representatives, Reminder, Mail, Sender
from . import app, db_session
from .decorators import validate_twilio_request

reps = Representatives()

@app.route("/")
def root():
    important_reps = [reps.get_representative_by_id(id) for id in IMPORTANT_REPS]
    return render_template("index.html", reps=important_reps)

@app.route("/politiker/")
def representatives():
    return render_template("representatives.html", reps=reps.representatives + reps.government)

@app.route("/p/<prettyname>/")
def representative(prettyname):
    rep = reps.get_representative_by_name(prettyname)
    if rep:
        return render_template("representative.html", rep=rep, twilio_number=TWILIO_NUMBERS[0])
    else:
        abort(404)

@app.route("/weitersagen/")
def share():
    return render_template("share.html")

@app.route("/faq/")
def faq():
    return render_template("faq.html")

@app.route("/datenschutz/")
def privacy():
    return render_template("privacy.html")

@app.route("/act/mail/", methods=["POST"])
def mail():
    id = request.form.get("id")
    rep = reps.get_representative_by_id(id)
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    name_user = firstname + " " + lastname
    mail_user = request.form.get("email")
    newsletter = True if request.form.get("newsletter") == "yes" else False

    if not all([rep, firstname, lastname, mail_user]):
        abort(400) # bad request

    try:
        sender = db_session.query(Sender).filter_by(email_address = mail_user).one()
        mail = Mail(sender, id)

        try:
            db_session.add(mail)
            db_session.commit()

            if sender.date_validated:
                # sender is authorized to send mails
                flash("Vielen Dank für Ihre Teilnahme.")
                mail.send()
                db_session.commit()
            else:
                if datetime.now() - sender.date_requested > timedelta(5):
                    # validation request expired
                    flash("Ihre Bestätigungsanfrage ist abgelaufen. Um fortzufahren, bestätigen Sie bitte den Link, den wir an {mail_user} gesendet haben.".format(mail_user=sender.email_address))
                    sender.request_validation()
                    db_session.commit()
                else:
                    # validation request needs to be confirmed
                    flash("Danke für Ihr Engagement. Um fortzufahren, bestätigen Sie bitte den Link, den wir an {mail_user} gesendet haben.".format(mail_user=sender.email_address))

        except IntegrityError:
            flash("Sie haben {rep_name} bereits eine E-Mail geschrieben.".format(rep_name=str(rep)))
            db_session.rollback()

    except NoResultFound:
        # sender never sent mail before
        sender = Sender(name_user, mail_user)
        db_session.add(sender)
        mail = Mail(sender, id)
        db_session.add(mail)
        db_session.commit()
        flash("Danke für Ihr Engagement. Um fortzufahren, bestätigen Sie bitte den Link, den wir an {mail_user} gesendet haben.".format(mail_user=sender.email_address))

    return redirect(url_for("representative", prettyname=rep.name.prettyname, _anchor="email-senden"))

@app.route("/act/validate/<hash>", methods=["GET"])
def validate(hash):
    try:
        sender = db_session.query(Sender).filter_by(hash=hash).one()

        if sender.date_validated:
            flash("Sie haben Ihre E-Mail Adresse bereits erfolgreich verifiziert.")
        elif datetime.now() - sender.date_requested > timedelta(5):
            flash("Ihre Bestätigungsanfrage ist abgelaufen. Um fortzufahren, bestätigen Sie bitte den Link, den wir an {mail_user} gesendet haben.".format(mail_user=sender.email_address))
            sender.request_validation()
        else:
            flash("Vielen Dank, Sie haben Ihre E-Mail Adresse erfolgreich verifiziert.")
            sender.validate()
            for mail in sender.mails:
                mail.send()
            db_session.commit()

    except NoResultFound:
        flash("Dieser Bestätigungslink ist ungültig.")
        
    return render_template("validate.html")

@app.route("/act/call/", methods=["POST"])
@validate_twilio_request
def call():
    resp = Response()

    resp.play(url_for("static", filename="audio/intro.wav"))
    resp.redirect(url_for("gather_menu"))

    return str(resp)

@app.route("/act/gather-menu/", methods=["POST"])
@validate_twilio_request
def gather_menu():
    number = request.values.get("From")
    resp = Response()
    
    try:
        reminder = Reminder(number)
        db_session.add(reminder)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()

    with resp.gather(numDigits=1, action=url_for("handle_menu")) as g:
        g.play(url_for("static", filename="audio/gather_menu.wav"), loop = 4)

    return str(resp)

@app.route("/act/handle-menu/", methods=["POST"])
@validate_twilio_request
def handle_menu():
    digits_pressed = request.values.get("Digits", 0, type=int)
    resp = Response()

    if digits_pressed == 1:
        resp.redirect(url_for("gather_reminder_time"))
    elif digits_pressed == 2:
        resp.redirect(url_for("gather_representative"))
    elif digits_pressed == 3:
        resp.redirect(url_for("info_tape"))
    elif digits_pressed == 4:
        resp.redirect(url_for("handle_reminder_unsubscribe"))
    elif digits_pressed == 5:
        resp.dial(FEEDBACK_NUMBER)
    else:
        resp.play(url_for("static", filename="audio/invalid.wav"))
        resp.redirect(url_for("gather_menu"))

    return str(resp)

@app.route("/act/gather-reminder-time/", methods=["POST"])
@validate_twilio_request
def gather_reminder_time():
    resp = Response()
    
    with resp.gather(numDigits=2, action=url_for("handle_reminder_time")) as g:
        g.play(url_for("static", filename="audio/gather_reminder_time.wav"), loop = 4)

    return str(resp)

@app.route("/act/handle-reminder-time/", methods=["POST"])
@validate_twilio_request
def handle_reminder_time():
    digits_pressed = request.values.get("Digits", 0, type=int)
    number = request.values.get("From")
    resp = Response()

    if not number or number in ["+7378742833", "+2562533", "+8656696", "+266696687", "+86282452253"]:
        resp.play(url_for("static", filename="audio/handle_reminder_time_error.wav"))
    if 9 <= digits_pressed <= 16:
        reminder = db_session.query(Reminder).filter_by(phone_number = number).one()
        if reminder.time is None:
            resp.play(url_for("static", filename="audio/handle_reminder_time_set.wav"))
        else:
            if digits_pressed > datetime.now().hour and reminder.last_called.date() == datetime.today().date():
                reminder.last_called = None

            resp.play(url_for("static", filename="audio/handle_reminder_time_reset.wav"))

        reminder.time = digits_pressed
        db_session.commit()
    else:
        resp.play(url_for("static", filename="audio/handle_reminder_time_invalid.wav"))
        resp.redirect(url_for("gather_reminder_time"))

    return str(resp)

@app.route("/act/gather-representative/", methods=["POST"])
@validate_twilio_request
def gather_representative():
    resp = Response()

    with resp.gather(numDigits=5, action=url_for("handle_representative")) as g:
        g.play(url_for("static", filename="audio/gather_representative.wav"), loop = 4)

    return str(resp)

@app.route("/act/handle-representative/", methods=["POST"])
@validate_twilio_request
def handle_representative():
    digits_pressed = request.values.get("Digits", "00000", type=str)
    rep = reps.get_representative_by_id(digits_pressed)
    resp = Response()
    
    if rep is not None and rep.contact.phone:
        resp.play(url_for("static", filename="audio/handle_representative_a.wav"))
        resp.play(url_for("static", filename="audio/representative/" + rep.name.prettyname + ".wav"))
        resp.play(url_for("static", filename="audio/handle_representative_c.wav"))

        if app.debug:
            resp.dial(FEEDBACK_NUMBER, timelimit=60, callerid=choice(TWILIO_NUMBERS))
        else:
            resp.dial(rep.contact.phone, timelimit=900, callerid=choice(TWILIO_NUMBERS))

        resp.play(url_for("static", filename="audio/adieu.wav"))

    else:
        resp.play(url_for("static", filename="audio/handle_representative_invalid.wav"))
        resp.redirect(url_for("gather_representative"))

    return str(resp)

@app.route("/act/handle-reminder-unsubscribe/", methods=["POST"])
@validate_twilio_request
def handle_reminder_unsubscribe():
    resp = Response()
    
    direction = request.values.get("Direction")

    if direction == "inbound":
        number = request.values.get("From")
    else:
        number = request.values.get("To")
    
    reminder = db_session.query(Reminder).filter_by(phone_number = number).one()
    reminder.time = None
    db_session.commit()
    resp.play(url_for("static", filename="audio/handle_reminder_unsubscribe.wav"))

    return str(resp)

@app.route("/act/gather-reminder-call/", methods=["POST"])
@validate_twilio_request
def gather_reminder_call():
    resp = Response()

    resp.play(url_for("static", filename="audio/gather_reminder_call.wav"))
    resp.redirect(url_for("gather_reminder_menu"))

    return str(resp)

@app.route("/act/gather-reminder-menu/", methods=["POST"])
@validate_twilio_request
def gather_reminder_menu():
    resp = Response()

    with resp.gather(numDigits=1, action=url_for("handle_reminder_menu")) as g:
        g.play(url_for("static", filename="audio/gather_reminder_menu.wav"), loop = 4)

    return str(resp)

@app.route("/act/handle-reminder-menu/", methods=["POST"])
@validate_twilio_request
def handle_reminder_menu():
    digits_pressed = request.values.get("Digits", 0, type=int)
    number = request.values.get("To")
    resp = Response()

    if digits_pressed == 1:
        reminder = db_session.query(Reminder).filter_by(phone_number = number).one()
        reminder.times_forwarded = reminder.times_forwarded + 1
        db_session.commit()

        rep = reps.get_representative_by_id("00000")
        resp.play(url_for("static", filename="audio/handle_representative_a.wav"))
        resp.play(url_for("static", filename="audio/representative/" + rep.name.prettyname + ".wav"))
        resp.play(url_for("static", filename="audio/handle_representative_c.wav"))

        if app.debug:
            resp.dial(FEEDBACK_NUMBER, timelimit=60, callerid=choice(TWILIO_NUMBERS))
        else:
            resp.dial(rep.contact.phone, timelimit=900, callerid=choice(TWILIO_NUMBERS))

        resp.play(url_for("static", filename="audio/adieu.wav"))

    elif digits_pressed == 2:
        pass # hang up
    elif digits_pressed == 3:
        resp.redirect(url_for("reminder_info_tape"))
    elif digits_pressed == 4:
        resp.redirect(url_for("handle_reminder_unsubscribe"))
    elif digits_pressed == 5:
        resp.dial(FEEDBACK_NUMBER)
    else:
        resp.play(url_for("static", filename="audio/invalid.wav"))
        resp.redirect(url_for("gather_reminder_menu"))

    return str(resp)

@app.route("/act/info_tape/", methods=["POST"])
@validate_twilio_request
def info_tape():
    resp = Response()

    with resp.gather(numDigits=1, action=url_for("gather_menu")) as g:
        g.play(url_for("static", filename="audio/info_tape.wav"))

    resp.redirect(url_for("gather_menu"))

    return str(resp)

@app.route("/act/reminder_info_tape/", methods=["POST"])
@validate_twilio_request
def reminder_info_tape():
    resp = Response()

    with resp.gather(numDigits=1, action=url_for("gather_reminder_menu")) as g:
        g.play(url_for("static", filename="audio/info_tape.wav"))

    resp.redirect(url_for("gather_reminder_menu"))

    return str(resp)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
