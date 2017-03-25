try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse
from functools import wraps
from flask import abort, current_app, request
from twilio.twiml import Response
from twilio.util import RequestValidator
from config import *

def twilio_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        validator = RequestValidator(TWILIO_SECRET)
        url = list(urlparse(request.url))
        url[1] = url[1].encode("idna").decode("utf-8")
        url = urlunparse(url)

        signature = request.headers.get("X-TWILIO-SIGNATURE", "")

        request_valid = validator.validate(url, request.form, signature)

        if request_valid or current_app.debug:
            resp = Response()
            f(resp, *args, **kwargs)
            return str(resp)

        else:
            return abort(403)

    return decorated_function
