from db import db
from sqlalchemy.sql import func


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    username = db.Column(db.String(80), unique=True, nullable=False)
    firebase_id = db.Column(db.String(255), unique=True, nullable=False)
    accepted_terms = db.Column(db.Boolean, default=False)
    playing_hours_begin = db.Column(db.Integer)
    playing_hours_end = db.Column(db.Integer)
    range_bet_low = db.Column(db.Numeric(precision=10, scale=2))
    range_bet_high = db.Column(db.Numeric(precision=10, scale=2))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_firebase_id(cls, firebase_id):
        return cls.query.filter_by(firebase_id=firebase_id).first()

    def save(self):
        db.session.add(self)
        db.session.commit()
