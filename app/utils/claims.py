from firebase_admin import auth


def set_is_admin(firebase_id: str, value: bool):
    if not value:
        claims_to_set = {"admin": None}  # We erase the claim
    else:
        claims_to_set = {"admin": True}
    auth.set_custom_user_claims(firebase_id, claims_to_set)
