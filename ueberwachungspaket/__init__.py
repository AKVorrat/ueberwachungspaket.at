from flask import Flask, render_template
from config import SECRET_KEY, DEBUG
from database import init_db, db_session

from ueberwachungspaket.views import general
from ueberwachungspaket.views import act
from ueberwachungspaket.views import consultation

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.from_pyfile("../config/main.py")
app.config.from_pyfile("../config/mail.py")
app.debug = DEBUG
init_db()

app.register_blueprint(general.mod)
app.register_blueprint(act.mod)
app.register_blueprint(consultation.mod)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    app.run()
