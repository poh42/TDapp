from ma import ma
from models.challenge_user import ChallengeUserModel
from models.challenge_ import ChallengeModel
from marshmallow import fields, ValidationError


def wager_must_exist(data):
    if not data:
        raise ValidationError("Data not provided")
    challenge = ChallengeModel.find_by_id(data)
    if challenge is None:
        raise ValidationError("Challenge id should be valid")


class ChallengeUserSchema(ma.SQLAlchemyAutoSchema):
    wager_id = fields.Integer(required=True, validate=wager_must_exist)
    challenged = fields.Nested("UserSchema")

    class Meta:
        model = ChallengeUserModel
        dump_only = ("id", "created_at", "updated_at", "challenger_id", "status")
        load_instance = True
