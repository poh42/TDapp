from db import db
from sqlalchemy.sql import func

STATUS_OPEN = "OPEN"
STATUS_READY = "READY"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_DECLINED = "DECLINED"
STATUS_PENDING = "PENDING"
STATUS_FINISHED = "FINISHED"
STATUS_COMPLETED = "COMPLETED"
STATUS_REJECTED = "REJECTED"
STATUS_STARTED = "STARTED"
STATUS_DISPUTED = "DISPUTED"
STATUS_SOLVED = "SOLVED"


class ChallengeUserModel(db.Model):
    __tablename__ = "challenge_users"
    id = db.Column(db.Integer, primary_key=True)
    challenger_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenged_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    wager_id = db.Column(
        db.Integer, db.ForeignKey("challenges.id"), nullable=False, unique=True
    )
    status_challenger = db.Column(db.String(45), nullable=False, default=STATUS_OPEN)
    status_challenged = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    challenger = db.relationship("UserModel", foreign_keys=[challenger_id])
    challenged = db.relationship("UserModel", foreign_keys=[challenged_id])
    challenge = db.relationship("ChallengeModel", foreign_keys=[wager_id])

    @property
    def declined(self):
        return self.status_challenged == STATUS_DECLINED

    @property
    def open(self):
        return self.status_challenger == STATUS_OPEN

    @property
    def accepted(self):
        return self.status_challenged == STATUS_ACCEPTED

    @property
    def completed(self):
        return (
            self.status_challenger == STATUS_COMPLETED
            and self.status_challenged == STATUS_COMPLETED
        )

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_wager_id(cls, wager_id):
        return cls.query.filter_by(wager_id=wager_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
