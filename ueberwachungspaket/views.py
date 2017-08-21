# -*- coding: utf-8 -*-
from random import choice, shuffle
from datetime import datetime, date, timedelta
from re import match
from flask import render_template, abort, request, url_for, flash, redirect, jsonify, send_from_directory
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from config import *
from config.main import *
from config.mail import *
from database.models import Representatives, Reminder, Mail, Sender, ConsultationSender, Opinion
from database.models import load_consultation_issues, sendmail
from . import app, db_session
from .decorators import twilio_request

from json import load
import math
import weasyprint
from markdown import markdown
import re

page_size = 35
reps = Representatives()
c_issues = load_consultation_issues()

@app.route("/")
def root():
    with open("ueberwachungspaket/data/quotes.json", "r") as json_file:
        quotes = load(json_file)
    shuffle(quotes)

    consultation_count = db_session.query(func.count(ConsultationSender.date_validated)).one()[0]
    if consultation_count < 100:
        consultation_max = 100
    else:
        consultation_max = math.ceil(consultation_count / 10000.0) * 10000
    return render_template(
        "index.html", 
        quotes=quotes,
        consultation_progress_max=consultation_max,
        consultation_progress_count=consultation_count,
        consultation_progress_count_percent=100.0*consultation_count/consultation_max,
        consultation_issues=c_issues
    )

@app.route("/politiker/")
def representatives():
    reps_random = reps.representatives + reps.government
    shuffle(reps_random)
    return render_template(
        "representatives.html",
        reps=reps_random
    )

@app.route("/p/<prettyname>/")
def representative(prettyname):
    rep = reps.get_representative_by_name(prettyname)
    if rep:
        return render_template(
            "representative.html",
            rep=rep,
            twilio_number=TWILIO_NUMBERS[0]
        )
    else:
        abort(404)

@app.route("/konsultation/")
def consultation():
    with open("ueberwachungspaket/data/quotes.json", "r") as json_file:
        quotes = load(json_file)
    shuffle(quotes)
    query = db_session.query(Opinion).order_by(Opinion.originality.desc(), Opinion.date.desc())
    opinions_count = query.count()
    opinions = query.limit(page_size).all()

    return render_template(
        "consultation.html",
        quotes=quotes,
        opinions=opinions,
        opinions_count=opinions_count
    )

@app.route("/konsultation/load")
def consultation_load():
    page_index = request.args.get("pageIndex", 0, type=int)
    sort_key = request.args.get("sortKey")
    filter_origin = request.args.get("filterOrigin")
    filter_topic = request.args.get("filterTopic")
    filter_name = request.args.get("filterName")

    query = db_session.query(Opinion)

    if sort_key:
        if sort_key == "name":
            query = query.order_by(Opinion.name, Opinion.originality.desc())
        elif sort_key == "date":
            query = query.order_by(Opinion.date, Opinion.originality.desc())
        else:
            query = query.order_by(Opinion.originality.desc(), Opinion.date.desc())

    if filter_topic:
        if filter_topic == "bundestrojaner":
            query = query.filter_by(addresses_bundestrojaner=True)
        elif filter_topic == "netzsperren":
            query = query.filter_by(addresses_netzsperren=True)
        elif filter_topic == "vds-video":
            query = query.filter_by(addresses_vds_video=True)
        elif filter_topic == "ueberwachung-strassen":
            query = query.filter_by(addresses_ueberwachung_strassen=True)
        elif filter_topic == "vds-quickfreeze":
            query = query.filter_by(addresses_vds_quickfreeze=True)
        elif filter_topic == "anonyme-simkarten":
            query = query.filter_by(addresses_anonyme_simkarten=True)
        elif filter_topic == "imsi-catcher":
            query = query.filter_by(addresses_imsi_catcher=True)
        elif filter_topic == "lauschangriff-auto":
            query = query.filter_by(addresses_lauschangriff_auto=True)

    if filter_origin:
        if filter_origin == "bmi":
            query = query.filter(and_(Opinion.link_bmi_pdf.isnot(None), Opinion.link_bmi_pdf != ""))
        elif filter_origin == "bmj":
            query = query.filter(and_(Opinion.link_bmj_pdf.isnot(None), Opinion.link_bmj_pdf != ""))

    if filter_name:
        query = query.filter(Opinion.name.ilike("%{}%".format(filter_name)))

    opinions_count = query.count()
    opinions = query.slice(page_index * page_size, (page_index + 1) * page_size).all()
    opinions = [opinion.serialize() for opinion in opinions]
    return jsonify(opinions=opinions, count=opinions_count)

@app.route("/konsultation/showpdf/bmi/<int:fid>")
def showpdf_bmi(fid):
    resp = send_from_directory(PDF_FOLDER, str(fid) + "_bmi.pdf")
    resp.headers["Content-Disposition"] = "inline; filename=" + str(fid) + "_bmi.pdf"
    return resp

@app.route("/konsultation/showpdf/bmj/<int:fid>")
def showpdf_bmj(fid):
    resp = send_from_directory(PDF_FOLDER, str(fid) + "_bmj.pdf")
    resp.headers["Content-Disposition"] = "inline; filename=" + str(fid) + "_bmj.pdf"
    return resp

@app.route("/weitersagen/")
def share():
    return render_template("share.html")

@app.route("/unterstützer/")
def supporters():
    return render_template("supporters.html")

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
    mail_user = request.form.get("email")
    newsletter = True if request.form.get("newsletter") == "yes" else False

    if not all([rep, firstname, lastname, mail_user]) or not rep.contact.mail or id == "00000" or not match(r"[^@]+@[^@]+\.[^@]+", mail_user):
        abort(400) # bad request

    name_user = firstname + " " + lastname

    try:
        sender = db_session.query(Sender).filter_by(email_address=mail_user).one()

        if newsletter:
            sender.newsletter = True
            db_session.commit()

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
        sender = Sender(name_user, mail_user, newsletter=newsletter)
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
@twilio_request
def call(resp):
    resp.play(url_for("static", filename="audio/intro.wav"))
    resp.redirect(url_for("gather_menu"))

@app.route("/act/callback/", methods=["POST"])
@twilio_request
def callback(resp):
    direction = request.values.get("Direction")
    duration = request.values.get("CallDuration", 0, type=int)

    if direction == "inbound":
        number = request.values.get("From")
    else:
        number = request.values.get("To")

    try:
        reminder = db_session.query(Reminder).filter_by(phone_number=number).one()
        reminder.time_connected = reminder.time_connected + duration
        db_session.commit()
    except IntegrityError:
        db_session.rollback()
    except NoResultFound:
        pass

@app.route("/act/gather-menu/", methods=["POST"])
@twilio_request
def gather_menu(resp):
    number = request.values.get("From")

    try:
        reminder = Reminder(number)
        db_session.add(reminder)
        db_session.commit()
    except IntegrityError:
        db_session.rollback()

    with resp.gather(numDigits=1, action=url_for("handle_menu")) as g:
        g.play(url_for("static", filename="audio/gather_menu.wav"), loop=4)

@app.route("/act/handle-menu/", methods=["POST"])
@twilio_request
def handle_menu(resp):
    digits_pressed = request.values.get("Digits", 0, type=int)

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

@app.route("/act/gather-reminder-time/", methods=["POST"])
@twilio_request
def gather_reminder_time(resp):
    with resp.gather(numDigits=2, action=url_for("handle_reminder_time")) as g:
        g.play(url_for("static", filename="audio/gather_reminder_time.wav"), loop=4)

@app.route("/act/handle-reminder-time/", methods=["POST"])
@twilio_request
def handle_reminder_time(resp):
    digits_pressed = request.values.get("Digits", 0, type=int)
    number = request.values.get("From")

    if not number or number in ["+7378742833", "+2562533", "+8656696", "+266696687", "+86282452253"]:
        resp.play(url_for("static", filename="audio/handle_reminder_time_error.wav"))
    if 9 <= digits_pressed <= 16:
        reminder = db_session.query(Reminder).filter_by(phone_number=number).one()
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

@app.route("/act/gather-representative/", methods=["POST"])
@twilio_request
def gather_representative(resp):
    with resp.gather(numDigits=5, action=url_for("handle_representative")) as g:
        g.play(url_for("static", filename="audio/gather_representative.wav"), loop=4)

@app.route("/act/handle-representative/", methods=["POST"])
@twilio_request
def handle_representative(resp):
    digits_pressed = request.values.get("Digits", "00000", type=str)
    number = request.values.get("From")
    rep = reps.get_representative_by_id(digits_pressed)

    if rep is not None and rep.contact.phone:
        reminder = db_session.query(Reminder).filter_by(phone_number=number).one()
        reminder.times_forwarded = reminder.times_forwarded + 1
        db_session.commit()

        resp.play(url_for("static", filename="audio/handle_representative_a.wav"))
        resp.play(url_for("static", filename="audio/representative/" + rep.name.prettyname + ".wav"))
        resp.play(url_for("static", filename="audio/handle_representative_c.wav"))

        if app.debug:
            resp.dial(FEEDBACK_NUMBER, timeLimit=60, callerId=choice(TWILIO_NUMBERS))
        else:
            resp.dial(rep.contact.phone, timeLimit=3600, callerId=choice(TWILIO_NUMBERS))

        resp.play(url_for("static", filename="audio/adieu.wav"))

    else:
        resp.play(url_for("static", filename="audio/handle_representative_invalid.wav"))
        resp.redirect(url_for("gather_representative"))

@app.route("/act/handle-reminder-unsubscribe/", methods=["POST"])
@twilio_request
def handle_reminder_unsubscribe(resp):
    direction = request.values.get("Direction")

    if direction == "inbound":
        number = request.values.get("From")
    else:
        number = request.values.get("To")

    reminder = db_session.query(Reminder).filter_by(phone_number=number).one()
    reminder.time = None
    db_session.commit()
    resp.play(url_for("static", filename="audio/handle_reminder_unsubscribe.wav"))

@app.route("/act/gather-reminder-call/", methods=["POST"])
@twilio_request
def gather_reminder_call(resp):
    resp.play(url_for("static", filename="audio/gather_reminder_call.wav"))
    resp.redirect(url_for("gather_reminder_menu"))

@app.route("/act/gather-reminder-menu/", methods=["POST"])
@twilio_request
def gather_reminder_menu(resp):
    with resp.gather(numDigits=1, action=url_for("handle_reminder_menu")) as g:
        g.play(url_for("static", filename="audio/gather_reminder_menu.wav"), loop=4)

@app.route("/act/handle-reminder-menu/", methods=["POST"])
@twilio_request
def handle_reminder_menu(resp):
    digits_pressed = request.values.get("Digits", 0, type=int)
    number = request.values.get("To")

    if digits_pressed == 1:
        reminder = db_session.query(Reminder).filter_by(phone_number=number).one()
        reminder.times_forwarded = reminder.times_forwarded + 1
        db_session.commit()

        rep = reps.get_representative_by_id("00000")
        resp.play(url_for("static", filename="audio/handle_representative_a.wav"))
        resp.play(url_for("static", filename="audio/representative/" + rep.name.prettyname + ".wav"))
        resp.play(url_for("static", filename="audio/handle_representative_c.wav"))

        if app.debug:
            resp.dial(FEEDBACK_NUMBER, timeLimit=60, callerId=choice(TWILIO_NUMBERS))
        else:
            resp.dial(rep.contact.phone, timeLimit=900, callerId=choice(TWILIO_NUMBERS))

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

@app.route("/act/info_tape/", methods=["POST"])
@twilio_request
def info_tape(resp):
    with resp.gather(numDigits=1, action=url_for("gather_menu")) as g:
        g.play(url_for("static", filename="audio/info_tape.wav"))

    resp.redirect(url_for("gather_menu"))

@app.route("/act/reminder_info_tape/", methods=["POST"])
@twilio_request
def reminder_info_tape(resp):
    with resp.gather(numDigits=1, action=url_for("gather_reminder_menu")) as g:
        g.play(url_for("static", filename="audio/info_tape.wav"))

    resp.redirect(url_for("gather_reminder_menu"))

@app.route("/konsultation/form/", methods=["post"])
def consultation_form():
    selected_issues = list(map(lambda x: [i for i in c_issues if i['id'] == x][0],
                               filter(lambda x: x != None,
                                      [request.form.get(issue['id']) for issue in c_issues])))
    if selected_issues == []:
        abort(400)
    
    bmi_text = ''
    bmj_text = ''
    for issue in selected_issues:
        # pull issue from issues array
        if issue['authority'] == 'BMJ':
            bmj_text += issue['text'] + '\n\n'
        elif issue['authority'] == 'BMI':
            bmi_text += issue['text'] + '\n\n'

    return render_template(
        "consultation_form.html", 
        consultation_issues=selected_issues,
        consultation_text_bmi=bmi_text, 
        consultation_text_bmj=bmj_text,
    )

@app.route("/consultation/verify-email/", methods=["post"])
def consultation_verifyemail():
    first_name = request.form.get('consultation-vorname')
    last_name = request.form.get('consultation-nachname')
    email = request.form.get('consultation-email')
    publish_name = request.form.get('consultation-check-name-datenschutz')
    publish_content = request.form.get('consultation-check-parlament')
    newsletter = request.form.get('consultation-check-newsletter')
    bmi_text = request.form.get('consultation-text-bmi')
    bmj_text = request.form.get('consultation-text-bmj')

    if not (all([first_name, last_name, email, publish_name]) and (bmi_text or bmj_text)):
        abort(400)

    try:
        sender = db_session.query(ConsultationSender).filter_by(email_address=email).one()
        if sender.date_validated:
            return render_template("consultation_corrections.html",
                    address_parliament=EMAIL_PARL, address_bmi=EMAIL_BMI, address_bmj=EMAIL_BMJ)
        else:
            db_session.delete(sender)
            db_session.commit()
    except NoResultFound:
        pass

    # sender hasn't sent submission before
    sender = ConsultationSender(first_name, last_name, email, bmi_text, bmj_text, not publish_content, bool(newsletter))
    db_session.add(sender)
    db_session.commit()
    return render_template("consultation_verifyemail.html")

def make_endnotes(md):
    r_notes = r'\[\^[0-9]+\]\(([^)]+)\)'
    footnotes = re.findall(r_notes, md)
    old = ''
    counter = 1
    while md != old:
        old = md
        md = re.sub(r_notes, '[' + str(counter) + ']', md, count=1)
        counter += 1
    endnotes = []
    for c, f in zip(range(1, len(footnotes) + 1), footnotes):
        endnotes.append('[' + str(c) + '] ' + f)
    return md, '\n\n'.join(endnotes)

def send_pdf(src_text, frame_html, filename, name, make_confidential, identifier, email_address, recipients):
    name_nohtml = name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    date = datetime.now().strftime("%d.%m.%Y")
    if make_confidential:
        confidential = "%s wünscht keine Veröffentlichung des Inhalts der Stellungnahme." % name
    else:
        confidential = "Mit einer Veröffentlichung auf der Parlamentswebsite ist %s einverstanden." % name

    text, endnotes = make_endnotes(src_text)
    html = frame_html % \
            {'name': name_nohtml,
             'date': date,
             'text': markdown(text, output_format='html5'),
             'endnotes': markdown(endnotes, output_format='html5')}
    
    weasyprint.HTML(string=html).render().write_pdf(filename)

    with open(filename, 'rb') as f:
        sendmail('"' + MAIL_FROM + '" <' + MAIL_FROM + '>',
                 recipients,
                 'Stellungnahme ' + identifier,
                 CONSULTATION_INTRO % {'ident': identifier, 'name': name, 'confidential': confidential, 'email': email_address},
                 f.read(),
                 'stellungnahme.pdf')


@app.route("/consultation/complete/<hash>")
def consultation_complete(hash):
    try:
        sender = db_session.query(ConsultationSender).filter_by(hash=hash).one()
    except NoResultFound:
        abort(400)

    if sender.date_validated:
        return render_template("consultation_already_verified.html",
                address_parliament=EMAIL_PARL, address_bmi=EMAIL_BMI, address_bmj=EMAIL_BMJ)
    else:
        sender.validate()
        db_session.commit()

    if sender.bmi_text:
        send_pdf(sender.bmi_text,
                 CONSULTATION_PDF_BMI_FRAME,
                 PDF_FOLDER + str(sender.id) + '_bmi.pdf',
                 sender.first_name + ' ' + sender.last_name,
                 sender.confidential_submission,
                 '326/ME',
                 sender.email_address,
                 [EMAIL_BMI, EMAIL_PARL, sender.email_address])

    if sender.bmj_text:
        send_pdf(sender.bmj_text,
                 CONSULTATION_PDF_BMJ_FRAME,
                 PDF_FOLDER + str(sender.id) + '_bmj.pdf',
                 sender.first_name + ' ' + sender.last_name,
                 sender.confidential_submission,
                 '325/ME',
                 sender.email_address,
                 [EMAIL_BMJ, EMAIL_PARL, sender.email_address])

    return render_template("consultation_complete.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
