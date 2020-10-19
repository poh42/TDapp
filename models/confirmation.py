from db import db
from secrets import token_urlsafe
from time import time

CONFIRMATION_EXPIRATION_DELTA = 1800  # 30 minutes


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"

    id = db.Column(db.String(64), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id: int, **kwargs):
        # Initializes expire_at, confirmed, user_id
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = token_urlsafe(32)
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self):
        return time() > self.expire_at  # current time > time ago + confirmation delta

    def force_to_expire(self):
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
