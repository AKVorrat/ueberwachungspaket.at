from flask import Flask
from config import *
from database import init_db, db_session
from .representatives import Representatives

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config["TWILIO_NUMBERS"] = TWILIO_NUMBERS
reps = Representatives()
init_db()

if __name__ == "__main__":
    app.run()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

from . import views
