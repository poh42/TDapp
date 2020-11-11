from ma import ma
from models.user_game import UserGameModel
from marshmallow import fields


class BaseUserGameSchema(ma.SQLAlchemyAutoSchema):
    game_id = fields.Integer(required=True)
    console_id = fields.Integer(required=True)
    level = fields.String()

    class Meta:
        model = UserGameModel
        dump_only = ("id", "created_at", "updated_at", "user_id")


class UserGameSchema(BaseUserGameSchema):
    class Meta(BaseUserGameSchema.Meta):
        load_instance = True
