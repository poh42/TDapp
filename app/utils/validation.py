from marshmallow import ValidationError


def validate_lower_upper_fields(
    data: dict,
    lower_key: str,
    upper_key: str,
    message_case_none: str,
    message_case_bigger: str,
):
    lower = data.get(lower_key, None)
    upper = data.get(upper_key, None)
    if (lower is None and upper is not None) or (lower is not None and upper is None):
        raise ValidationError(message_case_none)
    if lower is None and upper is None:
        return  # Nothing to do here
    if lower > upper:
        raise ValidationError(message_case_bigger)


def validate_user_game_fields(fields):
    try:
        array_fields = [(f["console_id"], f["game_id"]) for f in fields]
    except KeyError:
        raise ValidationError("Keys are not in array")
    if not len(array_fields) == len(set(array_fields)):
        raise ValidationError("Duplicated game console pair")
