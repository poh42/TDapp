from ma import ma

# Based on https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/298#issuecomment-614923691
from marshmallow_sqlalchemy.fields import Nested
from models.game import GameModel
from schemas.console import ConsoleSchema
from marshmallow import fields


class BaseGameSchema(ma.SQLAlchemyAutoSchema):
    consoles = Nested(ConsoleSchema, many=True, only=["id"])

    class Meta:
        model = GameModel
        load_instance = True
        dump_only = ("id", "created_at", "updated_at")


class GameSchema(BaseGameSchema):
    consoles = Nested(ConsoleSchema, many=True)

    class Meta(BaseGameSchema.Meta):
        load_instance = True
