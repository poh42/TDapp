from flask_restful import Resource
from sqlalchemy.sql import text
from db import db
from decorators import optional_check_token
from models.console import ConsoleModel
from models.game import GameModel
from schemas.game import GameSchema
from utils.claims import get_claims, is_admin

game_schema = GameSchema()


class GamesByConsole(Resource):
    @classmethod
    def get(cls, console_id):
        if not ConsoleModel.console_id_exists(console_id):
            return {"message": "Console not found"}, 400
        sql = """
        select g.id, g.name, g.image from games g
            inner join games_has_consoles ghc on g.id = ghc.game_id 
            inner join consoles c on c.id = ghc.console_id 
        where c.id = :id AND g.is_active = True
        """
        results = db.engine.execute(text(sql), id=console_id).fetchall()
        if len(results) > 0:
            message = "Games found"
        else:
            message = "Games not found"
        return {"message": message, "games": [dict(r) for r in results]}


class Games(Resource):
    @classmethod
    @optional_check_token
    def get(cls):
        if is_admin():
            games = GameModel.get_all_games()
        else:
            games = GameModel.get_active_games()
        return {"message": "Games found", "games": game_schema.dump(games, many=True)}
