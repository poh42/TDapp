from ma import ma
from models.dispute import DisputeModel
from marshmallow import fields


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
