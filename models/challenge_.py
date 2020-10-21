from db import db
from sqlalchemy.sql import func


class ChallengeModel(db.Model):
    __tablename__ = "challenges"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    buy_in = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    reward = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    game = db.relationship("GameModel")

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
