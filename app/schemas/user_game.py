from ma import ma
from models.user_game import UserGameModel
from models.console import ConsoleModel
from models.game import GameModel
from marshmallow import fields, ValidationError, Schema

from schemas.console import ConsoleSchema


def console_must_exist(_id):
    if not _id:
        raise ValidationError("Data not provided")
    console_exists = ConsoleModel.console_id_exists(_id)
    if not console_exists:
        raise ValidationError("Console id should be valid")


def game_must_exist(_id):
    if not _id:
        raise ValidationError("Data not provided")
    game = GameModel.find_by_id(_id)
    if game is None:
        raise ValidationError("Game id should be valid")


class UserGameSchemaWithoutModel(Schema):
    game_id = fields.Integer(required=True, validate=game_must_exist)
    console_id = fields.Integer(required=True, validate=console_must_exist)


class BaseUserGameSchema(ma.SQLAlchemyAutoSchema):
    game_id = fields.Integer(required=True)
    console_id = fields.Integer(required=True)
    level = fields.String()

    class Meta:
        model = UserGameModel
        dump_only = ("id", "created_at", "updated_at", "user_id")


class UserGameSchema(BaseUserGameSchema):
    console = fields.Nested(ConsoleSchema)
    game = fields.Nested("GameSchema")

    class Meta(BaseUserGameSchema.Meta):
        load_instance = True
