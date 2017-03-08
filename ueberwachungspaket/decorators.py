from urllib.parse import urlparse, urlunparse
from flask import abort, current_app, request
from functools import wraps
from twilio.util import RequestValidator
from config import *

def validate_twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(TWILIO_SECRET)
        url = list(urlparse(request.url))
        url[1] = url[1].encode("idna").decode("utf-8")
        url = urlunparse(url)

        signature = request.headers.get("X-TWILIO-SIGNATURE", "")

        request_valid = validator.validate(url, request.form, signature)

        if request_valid or current_app.debug:
            return f(*args, **kwargs)
        else:
            return abort(403)

    return decorated_function
