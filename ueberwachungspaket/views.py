from flask import render_template, abort
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

@app.route("/act/mail/")
def mail():
    abort(404)

@app.route("/act/call/")
def call():
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
