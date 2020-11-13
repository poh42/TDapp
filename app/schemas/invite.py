from ma import ma
from models.invite import InviteModel
from schemas.user import UserSchema
from marshmallow import fields


class InviteSchema(ma.SQLAlchemyAutoSchema):
    user_inviting = fields.Nested(UserSchema)

    class Meta:
        model = InviteModel
        dump_only = ("id", "user_inviting", "user_invited")
        load_instance = True
