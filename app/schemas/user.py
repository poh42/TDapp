from ma import ma
from models.user import UserModel
from marshmallow import fields, validate, validates_schema
from utils.validation import validate_lower_upper_fields
from schemas.user_game import UserGameSchema

USER_PUBLIC_FIELDS = ("id", "user_games", "username", "friends", "avatar")

FIELDS_TO_EXCLUDE = (
    "playing_hours_begin",
    "playing_hours_end",
    "dob",
    "phone",
    "firebase_id",
    "accepted_terms",
    "range_bet_low",
    "range_bet_high",
)


class UserSchema(ma.SQLAlchemyAutoSchema):
    email = fields.Email(required=True)
    password = fields.String(validate=validate.Length(min=6), required=True)
    playing_hours_begin = fields.Integer(validate=validate.Range(0, 23))
    playing_hours_end = fields.Integer(validate=validate.Range(0, 23))
    user_games = fields.Nested(UserGameSchema, many=True)
    friends = fields.Nested(
        "self",
        many=True,
        exclude=("friends", "is_private",)  # This exclude avoids infinite recursion
        + FIELDS_TO_EXCLUDE,
    )

    @validates_schema
    def validate_related_fields(self, data, **kwargs):
        validate_lower_upper_fields(
            data,
            "playing_hours_begin",
            "playing_hours_end",
            "playing_hours_begin and playing_hours_end must be specified together",
            "playing_hours_begin should be smaller or equal to playing_hours_end",
        )
        validate_lower_upper_fields(
            data,
            "range_bet_low",
            "range_bet_high",
            "range_bet_low and range_bet_high must be specified together",
            "range_bet_low should be smaller or equal to range_bet_high",
        )

    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id", "firebase_id", "created_at", "updated_at", "friends")
        load_instance = True
