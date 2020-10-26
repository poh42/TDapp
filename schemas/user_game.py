from ma import ma
from models.user_game import UserGameModel
from marshmallow import fields


class UserGameSchema(ma.SQLAlchemyAutoSchema):
    game_id = fields.Integer()
    console_id = fields.Integer()

    class Meta:
        model = UserGameModel
        dump_only = ("id", "created_at", "updated_at", "user_id")
        load_instance = True
