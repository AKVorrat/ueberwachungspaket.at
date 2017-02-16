from flask import render_template, abort, request, url_for, jsonify
from random import choice
from twilio.twiml import Response
from sqlalchemy.exc import IntegrityError
from config import *
from database.models import Reminder
from . import app, reps, db_session
from .decorators import validate_twilio_request

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/abgeordnete/")
def representatives():
    return render_template("representatives.html", reps=reps.representatives)

@app.route("/a/<prettyname>/")
def representative(prettyname):
    rep = reps.get_representative_by_name(prettyname)
    if rep:
        return render_template("representative.html", rep=rep, twilio_number=choice(TWILIO_NUMBERS))
    else:
        abort(404)

@app.route("/weitersagen/")
def share():
    return render_template("share.html")

@app.route("/themen/")
def topics():
    return render_template("topics.html")

@app.route("/faq/")
def faq():
    return render_template("faq.html")

@app.route("/datenschutz/")
def privacy():
    return render_template("privacy.html")

def sendmail(id, firstname, lastname, email):
    return False
    
@app.route("/act/mail/", methods=["POST"])
def mail():
    id = request.form.get("id")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    newsletter = True if request.form.get("newsletter") == "yes" else False

    if not all([id, firstname, lastname, email]):
        app.logger.info("Sendmail: passed invalid arguments.")
        abort(400) # bad request

    success = sendmail(id, firstname, lastname, email, newsletter)

    rep = reps.get_representative_by_id(id)
    return render_template("representative.html", rep=rep, success=success)

@app.route("/act/call/", methods=["POST"])
@validate_twilio_request
def call():
    resp = Response()

    resp.say("Willkommen zu 'Kontaktiere Deine Abgeordneten'!", voice="alice", language="de-DE")
    resp.redirect(url_for("gather_menu"), method="POST")

    return str(resp)

@app.route("/act/gather-menu/", methods=["POST"])
@validate_twilio_request
def gather_menu():
    resp = Response()

    with resp.gather(numDigits=1, action=url_for("handle_menu"), method="POST") as g:
        g.say("Um mit einem Abgeordneten zu sprechen, wählen Sie Eins.", voice="alice", language="de-DE")
        g.say("Um sich für eine wiederholende Anruferinnerung anzumelden, wählen Sie Zwei.", voice="alice", language="de-DE")
        g.say("Um sich von der wiederholenden Anruferinnerung abzumendel, wählen Sie Drei.", voice="alice", language="de-DE")

    resp.redirect(url_for("gather_menu"), method="POST")

    return str(resp)

@app.route("/act/handle-menu/", methods=["POST"])
@validate_twilio_request
def handle_menu():
    digits_pressed = request.form.get("Digits", None)
    resp = Response()

    if digits_pressed == "1":
        resp.redirect(url_for("gather_representative"), method="POST")
    elif digits_pressed == "2":
        resp.redirect(url_for("gather_reminder_time"), method="POST")
    elif digits_pressed == "3":
        resp.redirect(url_for("handle_reminder_unsubscribe"), method="POST")
    else:
        resp.say("Sie haben keine gültige Option gewählt.", voice="alice", language="de-DE")
        resp.redirect(url_for("gather_menu"), method="POST")

    return str(resp)

@app.route("/act/gather-representative/", methods=["POST"])
@validate_twilio_request
def gather_representative():
    resp = Response()

    with resp.gather(numDigits=5, action=url_for("handle_representative"), method="POST") as g:
        g.say("Bitte geben Sie den Code ein, der Sie zu ihrem Abgeorneten weiterleitet.", voice="alice", language="de-DE")
        g.say("Der Code befindet sich am Ende der Seite ihres Abgeordneten und ist fünf Stellen lang.", voice="alice", language="de-DE")

    resp.redirect(url_for("gather_representative"), method="POST")

    return str(resp)

@app.route("/act/handle-representative/", methods=["POST"])
@validate_twilio_request
def handle_representative():
    digits_pressed = request.values.get("Digits", None)
    rep = reps.get_representative_by_id(digits_pressed)
    resp = Response()
    
    if rep is not None:
        resp.say("Sie werden jetzt zu " + str(rep) + " weitergeleitet.", voice="alice", language="de-DE")
        # resp.dial()
    else:
        resp.say("Sie haben keinen gültigen Code gewählt.", voice="alice", language="de-DE")
        resp.redirect(url_for("gather_representative"), method="POST")

    return str(resp)

@app.route("/act/gather-reminder-time/", methods=["POST"])
@validate_twilio_request
def gather_reminder_time():
    resp = Response()
    
    with resp.gather(numDigits=2, action=url_for("handle_reminder_time"), method="POST") as g:
        g.say("Um welche Uhrzeit möchten sie täglich mit einem zufälligen Abgeordneten verbunden werden?", voice="alice", language="de-DE")
        g.say("Bitte verwenden Sie das Vierundzwanzig-Stunden-Format.", voice="alice", language="de-DE")

    resp.redirect(url_for("gather_reminder_time"), method="POST")

    return str(resp)

@app.route("/act/handle-reminder-time/", methods=["POST"])
@validate_twilio_request
def handle_reminder_time():
    digits_pressed = request.values.get("Digits", None)
    from_number = request.values.get("From", None)
    resp = Response()

    if not all([digits_pressed, from_number]):
        resp.say("Es ist ein Fehler aufgetreten.", voice="alice", language="de-DE")
        resp.say("Bitte kontaktieren Sie uns, um den Service wieder zum Laufen zu bringen.", voice="alice", language="de-DE")
    if len(digits_pressed) == 2 and int(digits_pressed) >= 9 and int(digits_pressed) <= 16:
        reminder = Reminder(from_number, int(digits_pressed))

        try:
            db_session.add(reminder)
            db_session.commit()
            resp.say("Sie wurden in unsere Liste aufgenommen.", voice="alice", language="de-DE")
            resp.say("Um sich wieder abzumelden, rufen Sie erneut an und wählen die entsprechende Option im Menü.", voice="alice", language="de-DE")
        except IntegrityError as e:
            db_session.rollback()
            db_session.query(Reminder).filter_by(number = from_number).delete()
            db_session.add(reminder)
            db_session.commit()
            resp.say("Ihre Erinnerungszeit wurde aktualisiert.")
    else:
        resp.say("Die Zeit, die Sie eingegeben haben, ist ungültig.", voice="alice", language="de-DE")
        resp.say("Bitte beachten Sie, dass die Büros der Abgeordneten nur von neun bis sechzehn Uhr besetzt sind.", voice="alice", language="de-DE")
        resp.redirect(url_for("gather_reminder_time"), method="POST")

    return str(resp)

@app.route("/act/handle-reminder-unsubscribe/", methods=["POST"])
@validate_twilio_request
def handle_reminder_unsubscribe():
    from_number = request.values.get("From", None)
    resp = Response()
    
    db_session.query(Reminder).filter_by(number = from_number).delete()
    db_session.commit()
    resp.say("Sie werden ab jetzt nicht mehr regelmäßig mit Abgeordneten verbunden.", voice="alice", language="de-DE")

    return str(resp)

@app.route("/act/gather-reminder-call/", methods=["POST"])
@validate_twilio_request
def gather_reminder_call():
    resp = Response()

    with resp.gather(numDigits=1, action=url_for("handle_reminder_call"), method="POST") as g:
        g.say("Hallo, ich wollte Sie daran erinnern, einen Abgeordneten zu kontaktieren.", voice="alice", language="de-DE")
        g.say("Um jetzt mit einem Abgeordneten zu sprechen, wählen Sie Eins.", voice="alice", language="de-DE")
        g.say("Um in Zukunft nicht mehr erinnert zu werden, wählen Sie Zwei.", voice="alice", language="de-DE")

    resp.redirect(url_for("gather_reminder_call"), method="POST")

    return str(resp)

@app.route("/act/handle-reminder-call/", methods=["POST"])
@validate_twilio_request
def handle_reminder_call():
    digits_pressed = request.values.get("Digits", None)
    resp = Response()

    if digits_pressed == "1":
        rep = choice([rep for rep in resp.representatives if rep.team.prettyname == "spy"])
        resp.say("Sie werden jetzt mit " + rep + " verbunden.", voice="alice", language="de-DE")
        # resp.dial()
    elif digits_pressed == "2":
        resp.redirect(url_for("handle_reminder_unsubscribe"), method="POST")
    else:
        resp.say("Sie haben keine gültige Option gewählt.", voice="alice", language="de-DE")
        resp.redirect(url_for("handle_reminder_call"), method="POST")

    return str(resp)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
