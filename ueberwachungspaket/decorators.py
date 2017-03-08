from flask import abort, current_app, request
from functools import wraps
from twilio.util import RequestValidator
from config import *

def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(TWILIO_SECRET)
        url = request.url.encode("idna").decode("utf-8")
        signature = request.headers.get("X-TWILIO-SIGNATURE", "")

        request_valid = validator.validate(url, request.form, signature)

        if request_valid or current_app.debug:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function
