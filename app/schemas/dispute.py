from ma import ma
from models.challenge_ import ChallengeModel
from models.dispute import DisputeModel
from marshmallow import fields, Schema, ValidationError, validates_schema

from models.user import UserModel


class DisputeSchema(ma.SQLAlchemyAutoSchema):
    challenge_id = fields.Integer(required=False)

    class Meta:
        model = DisputeModel
        dump_only = ("id", "created_at", "updated_at", "challenge_id", "user_id")
        load_instance = True


class DisputeAdminSchema(ma.SQLAlchemyAutoSchema):
    challenge_id = fields.Integer(required=False)
    challenge = fields.Nested("ChallengeSchema")

    class Meta:
        model = DisputeModel
        dump_only = ("id", "created_at", "updated_at", "user_id")
        load_instance = True


def validate_challenge_id(_id):
    challenge = ChallengeModel.find_by_id(_id)
    if challenge is None:
        raise ValidationError("Challenge should be valid")


def validate_user_id(_id):
    user = UserModel.find_by_id(_id)
    if user is None:
        raise ValidationError("User id should be valid")


class SettleDisputeSchema(Schema):
    # challenge_id = fields.Integer(required=True, validate=validate_challenge_id)
    score_player_1 = fields.Integer(required=True)
    score_player_2 = fields.Integer(required=True)
    # user_id_1 = fields.Integer(required=True, validate=validate_user_id)
    # user_id_2 = fields.Integer(required=True, validate=validate_user_id)
    winner_id = fields.Integer(required=True, validate=validate_user_id)