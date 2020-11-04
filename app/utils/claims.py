from firebase_admin import auth
from flask import g


def set_is_admin(firebase_id: str, value: bool):
    if not value:
        claims_to_set = {"admin": None}  # We erase the claim
    else:
        claims_to_set = {"admin": True}
    auth.set_custom_user_claims(firebase_id, claims_to_set)


def get_claims() -> dict:
    """Gets current claims from firebase"""
    if hasattr(g, "claims"):
        return g.claims
    return dict()


def is_admin() -> bool:
    """Gets if a user is administrator based on the current claims"""
    return get_claims().get("admin", False)
