from ma import ma
from marshmallow import fields

from models.user_challenge_scores import UserChallengeScoresModel


class UserChallengeScoreSchema(ma.SQLAlchemyAutoSchema):
    user_id = fields.Integer(required=True)
    challenge_id = fields.Integer(required=True)

    class Meta:
        model = UserChallengeScoresModel
        load_instance = True
        dump_only = ("created_at", "updated_at", "user_id", "challenge_id")
