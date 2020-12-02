USER_FIELDS_TO_EXCLUDE = (
    "playing_hours_begin",
    "playing_hours_end",
    "dob",
    "phone",
    "firebase_id",
    "accepted_terms",
    "range_bet_low",
    "range_bet_high",
)


def get_fields_user_to_exclude(prefix: str, additional=None):
    if additional is None:
        additional = tuple()
    ret_val = []
    for val in set(USER_FIELDS_TO_EXCLUDE + additional):
        ret_val.append(f"{prefix}.{val}")
    return tuple(ret_val)
