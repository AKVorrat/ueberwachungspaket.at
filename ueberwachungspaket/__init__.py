from flask import Flask
from config import *
from database import init_db, db_session

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config.from_pyfile("../config/main.py")
app.config.from_pyfile("../config/mail.py")
app.debug = DEBUG
init_db()

if __name__ == "__main__":
    app.run()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

from . import views
