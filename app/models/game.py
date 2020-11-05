from db import db
from sqlalchemy.sql import func

from models.console import ConsoleModel
from models.game_has_console import game_has_console_table
from models.user_game import UserGameModel


class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    is_active = db.Column(db.Boolean, default=True)
    challenges = db.relationship(
        "ChallengeModel", lazy="dynamic", cascade="all, delete-orphan"
    )
    consoles = db.relationship(
        "ConsoleModel", cascade="all", secondary=game_has_console_table
    )

    @classmethod
    def get_active_games(cls):
        return (
            cls.query.outerjoin(ConsoleModel, cls.consoles)
            .filter(cls.is_active == True)
            .all()
        )

    @classmethod
    def get_all_games(cls):
        return cls.query.outerjoin(ConsoleModel, cls.consoles).all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
