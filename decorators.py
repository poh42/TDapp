from functools import wraps
from flask import request
from firebase_admin import auth


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get("authorization"):
            return {"message": "No token provided"}, 400
        try:
            user = auth.verify_id_token(request.headers["authorization"])
            request.user = user
        except:
            return {"message": "Invalid token provided."}, 400
        return f(*args, **kwargs)

    # This is used in tests to check if an endpoint is protected.
    wrap.is_checked_by_token = True
    return wrap
