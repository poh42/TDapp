from db import db
from sqlalchemy.sql import func

STATUS_OPEN = "OPEN"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_DECLINED = "DECLINED"


class ChallengeUserModel(db.Model):
    __tablename__ = "challenge_users"
    id = db.Column(db.Integer, primary_key=True)
    challenger_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    challenged_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    wager_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    challenger = db.relationship("UserModel", foreign_keys=[challenger_id])
    challenged = db.relationship("UserModel", foreign_keys=[challenged_id])
    challenge = db.relationship("ChallengeModel", foreign_keys=[wager_id])

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
