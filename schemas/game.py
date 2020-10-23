from ma import ma
from models.game import GameModel


class GameSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = GameModel
        dump_only = ("id", "created_at", "updated_at")
        load_instance = True
