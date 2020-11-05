from ma import ma
from models.game import GameModel
from schemas.console import ConsoleSchema


class GameSchema(ma.SQLAlchemyAutoSchema):
    consoles = ma.Nested(ConsoleSchema, many=True)

    class Meta:
        model = GameModel
        dump_only = ("id", "created_at", "updated_at", "consoles")
        load_instance = True
