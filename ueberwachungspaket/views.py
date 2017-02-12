from flask import render_template, abort
import twilio.twiml
from . import app, reps

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/abgeordnete/")
def representatives():
    return render_template("representatives.html", reps=reps.representatives)

@app.route("/a/<prettyname>/")
def representative(prettyname):
    rep = reps.get_representative(prettyname)
    if rep != None:
        return render_template("representative.html", rep=rep)
    else:
        abort(404)

@app.route("/faq/")
def faq():
    return render_template("faq.html")

@app.route("/datenschutz/")
def privacy():
    return render_template("privacy.html")

@app.route("/act/mail/", methods=["POST"])
def mail():
    idn = request.form.get("id")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    abort(404)

@app.route("/act/call/", methods=["GET", "POST"])
def call():
    resp = twilio.twiml.Response()
    resp.say("Hello. This is a test. Goodbye!")
    return str(resp)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
