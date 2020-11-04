from functools import wraps
from flask import request, g
from firebase_admin import auth
from models.user import UserModel


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get("authorization"):
            return {"message": "No token provided"}, 400
        try:
            claims = auth.verify_id_token(request.headers["authorization"])
            g.claims = claims
        except:
            return {"message": "Invalid token provided."}, 400
        return f(*args, **kwargs)

    # This is used in tests to check if an endpoint is protected.
    wrap.is_checked_by_token = True
    return wrap


def optional_check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get("authorization"):
            return f(*args, **kwargs)
        try:
            claims = auth.verify_id_token(request.headers["authorization"])
            g.claims = claims
        except:
            return f(*args, **kwargs)
        return f(*args, **kwargs)

    wrap.is_optionally_checked_by_token = True
    return wrap


def _is_admin():
    if not hasattr(g, "claims"):
        return False
    return g.claims.get("admin", False)


def check_is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not _is_admin():
            return {"message": "Unauthorized"}, 400
        return f(*args, **kwargs)

    wrap.is_checked_by_admin_claim = True
    return wrap


def check_is_admin_or_user_authorized(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if _is_admin():
            return f(*args, **kwargs)
        else:
            user_id = request.args.get("user_id", type=int)
            user = UserModel.find_by_firebase_id(g.claims["uid"])
            if not user:
                return {"message": "User not found"}, 400
            if user.id == user_id:
                return f(*args, **kwargs)
            else:
                return {"message": "Unauthorized"}, 400

    wrap.is_checked_by_admin_or_user = True
    return wrap
