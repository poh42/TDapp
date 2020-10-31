from datetime import datetime, timedelta

from sqlalchemy import text

from db import db
from sqlalchemy.sql import func
from firebase_admin import auth
from utils.email import send_email
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
        return send_email([self.email], subject, text, html)

    @classmethod
    def get_top_earners(cls):
        sql = """
        with t as (
            select SUM(t2.credit_change) as credit_change , t2.user_id from transactions t2
                    where t2.created_at >= :week_ago
            group by t2.user_id 
        ) select u.*, coalesce(t.credit_change, 0) as credit_change from users u
            left join t on t.user_id = u.id
          order by COALESCE(t.credit_change, 0) desc
        """
        week_ago = datetime.today() - timedelta(days=7)
        data = db.engine.execute(text(sql), week_ago=week_ago).fetchall()
        return [dict(d) for d in data]

    @classmethod
    def filter_users_by_game(cls, title):
        sql = """
         select u.* from users u
            inner join user_games t on t.user_id = u.id
            inner join games g ON t.game_id = g.id
         WHERE g.name ILIKE :title
         order by u.username ASC
        """
        data = db.engine.execute(text(sql), title=f"%{title}%").fetchall()
        return [dict(d) for d in data]

    def filter_by_friends(self):
        sql = """
        SELECT u.* from users u
            INNER JOIN friendships f ON u.id = f.followed_id
        WHERE f.follower_id = :own_id
        ORDER BY u.username ASC
        """
        data = db.engine.execute(text(sql), own_id=self.id).fetchall()
        return [dict(d) for d in data]

    @classmethod
    def get_all_users(cls):
        sql = "SELECT u.* from users u"
        data = db.engine.execute(text(sql)).fetchall()
        return [dict(d) for d in data]
