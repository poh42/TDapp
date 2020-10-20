from db import db
from sqlalchemy.sql import func


class GameModel(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    challenges = db.relationship(
        "ChallengeModel", lazy="dynamic", cascade="all, delete-orphan"
    )
