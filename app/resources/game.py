from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.sql import text
from db import db
from decorators import (
    optional_check_token,
    check_token,
    check_is_admin,
)
from models.console import ConsoleModel
from models.game import GameModel
from schemas.game import GameSchema, BaseGameSchema
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

    @classmethod
    @check_token
    @check_is_admin
    def post(cls):
        # Based on https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/298#issuecomment-614923691
        game = BaseGameSchema().load(request.get_json(), session=db.session)
        game.save_to_db()
        return {"message": "Game saved", "game": game_schema.dump(game)}, 201


class Game(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def put(cls, game_id):
        game: GameModel = GameModel.find_by_id(game_id)
        if game is None:
            return {"message": "Game not found"}, 400
        game_data = request.get_json()
        schema = GameSchema()
        errors = schema.validate(game_data, partial=True)
        if errors:
            raise ValidationError(errors)
        if game_data.get("name"):
            game.name = game_data.get("name")
        if game_data.get("image"):
            game.image = game_data.get("image")
        if game_data.get("description"):
            game.description = game_data.get("description")
        is_active = game_data.get("is_active")
        if is_active is True or is_active is False:
            game.is_active = is_active
        game.save_to_db()
        return {"game": schema.dump(game)}, 200

    @classmethod
    @check_token
    @check_is_admin
    def get(cls, game_id):
        game: GameModel = GameModel.find_by_id(game_id)
        if game is None:
            return {"message": "Game not found"}, 400
        schema = GameSchema()
        return {"game": schema.dump(game)}, 200

    @classmethod
    @check_token
    @check_is_admin
    def delete(cls, game_id):
        game: GameModel = GameModel.find_by_id(game_id)
        if game is None:
            return {"message": "Game not found"}, 400
        game.delete_from_db()
        return {"message": "Game deleted", "game": game_schema.dump(game)}, 200
