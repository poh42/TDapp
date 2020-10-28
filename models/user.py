from db import db
from sqlalchemy.sql import func
from firebase_admin import auth
from utils.mailgun import Mailgun
from flask import request, url_for
from models.confirmation import ConfirmationModel
from models.user_photo import UserPhotoModel
from models.friendship import friendship_table


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
    is_active = db.Column(db.Boolean, default=True)
    allow_public_challenges = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255))

    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    user_photos = db.relationship(
        "UserPhotoModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    user_games = db.relationship(
        "UserGameModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_id(cls, _id) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_username(cls, username) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_firebase_id(cls, firebase_id) -> "UserModel":
        return cls.query.filter_by(firebase_id=firebase_id).first()

    def update_password(self, new_password) -> None:
        auth.update_user(self.firebase_id, password=new_password)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Registration confirmation"
        text = f"Please click to confirm your registration: {link}"
        html = f'<html>Please click to confirm your registration: <a href="{link}">{link}</a></html>'
        return Mailgun.send_email([self.email], subject, text, html)
