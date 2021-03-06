from random import shuffle
from json import load
from flask import Blueprint, render_template, abort, request, jsonify
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from config import TWILIO_NUMBERS, ACTIVISM_LIST_POST_URL, ACTIVISM_LIST_POST_REFERER
from database.models import Representatives, Opinion, ConsultationSender, Activist
from database import db_session
from datetime import datetime
import requests

mod = Blueprint("general", __name__)
reps = Representatives()


@mod.route("/")
def index():
    with open("ueberwachungspaket/data/quotes_2.0.json", "r") as json_file:
        quotes = load(json_file)
    shuffle(quotes)
    consultation_count = 9143 #db_session.query(func.count(ConsultationSender.date_validated)).one()[0]
    opinions = db_session.query(Opinion).count()
    return render_template(
        "general/index.html",
        quotes=quotes,
        opinion_count=opinions,
        consultation_count=consultation_count
    )


#@mod.route("/politiker/")
def representatives():
    reps_random = reps.representatives + reps.government
    shuffle(reps_random)
    return render_template(
        "act/representatives.html",
        reps=reps_random
    )


#@mod.route("/p/<prettyname>/")
def representative(prettyname):
    rep = reps.get_representative_by_name(prettyname)
    if rep:
        return render_template(
            "act/representative.html",
            rep=rep,
            twilio_number=TWILIO_NUMBERS[0]
        )
    else:
        abort(404)


@mod.route("/weitersagen/")
def share():
    return render_template("general/share.html")


@mod.route("/unterstützer/")
def supporters():
    return render_template("general/supporters.html")


@mod.route("/faq/")
def faq():
    return render_template("general/faq.html")


@mod.route("/datenschutz/")
def privacy():
    return render_template("general/privacy.html")

#@mod.route("/join/", methods=["POST"])
def join():
    email = request.form.get('email')
    phone = request.form.get('phonenumber')

    if not email:
        abort(400)

    activist = Activist(email, phone, datetime.now())

    try:
        db_session.add(activist)
        db_session.commit()
    except IntegrityError:
        return jsonify({'status': 'error', 'reason': 'already_subscribed'})

    requests.post(ACTIVISM_LIST_POST_URL, data={'email': email}, headers={'referer': ACTIVISM_LIST_POST_REFERER})

    return jsonify({'status': 'success', 'reason': ''})
