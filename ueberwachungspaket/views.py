from flask import render_template, abort, url_for
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
    rep = reps.get_representative_by_name(prettyname)
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

    resp.say("Welcome to 'Contact Your Representatives'!")
    resp.redirect(url_for("gather_menu"), method="POST")

    return str(resp)

@app.route("/act/gather-representative/", methods=["POST"])
def gather_representative():
    resp = twilio.twiml.Response()

    with resp.gather(numDigits=5, action=url_for("handle_representative"), method="POST") as g:
        g.say("Please provide your representatives code to be redirected.")
        g.say("The code is located at the bottom of your representative's page and is five digits long.")

    return str(resp)

@app.route("/act/handle-representative/", methods=["POST"])
def handle_representative():
    digits_pressed = request.values.get("Digits", None)
    rep = reps.get_representative_by_idn(digits_pressed)
    resp = twilio.twiml.Response()
    
    if rep is not None:
        resp.say("You will now be redirected to " + rep + ".")
        # resp.dial()
    else:
        resp.say("The ID you entered does not exist.")
        resp.redirect(url_for("gather_representative"), method="POST")

    return str(resp)

@app.route("/act/gather-menu/", methods=["POST"])
def gather_menu():
    resp = twilio.twiml.Response()

    with resp.gather(numDigits=1, action=url_for("handle_menu"), method="POST") as g:
        g.say("To talk to a representative enter 1.")
        g.say("To subscribe for a recurring call reminder enter 2.")
        g.say("To unsubscribe your current recurring call reminder enter 3.")

    return str(resp)

@app.route("/act/handle-menu/", methods=["POST"])
def handle_menu():
    digits_pressed = request.values.get("Digits", None)
    resp = twilio.twiml.Response()

    if digits_pressed == "1":
        resp.redirect(url_for("gather_representative"), method="POST")
    elif digits_pressed == "2":
        resp.say("This feature will be available soon.")
    elif digits_pressed == "3":
        resp.say("This feature will be available soon.")
    else:
        resp.say("You did not enter a valid option.")
        resp.redirect(url_for("gather_menu"), method="POST")

    return str(resp)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
