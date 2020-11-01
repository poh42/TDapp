from flask_restful import Resource
from sqlalchemy.sql import text
from db import db


class GamesByConsole(Resource):
    def get(self, console_id):
        sql = """
        select g.id, g.name from games g
            inner join games_has_consoles ghc on g.id = ghc.game_id 
            inner join consoles c on c.id = ghc.console_id 
        where c.id = :id
        """
        results = db.engine.execute(text(sql), id=console_id).fetchall()
        return {"message": "Games found", "games": [dict(r) for r in results]}
