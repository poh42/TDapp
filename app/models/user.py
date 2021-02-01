from datetime import datetime, timedelta

from sqlalchemy import text, and_, or_

from db import db
from sqlalchemy.sql import func
from firebase_admin import auth
from utils.email import send_email
from flask import request, url_for
from models.confirmation import ConfirmationModel
from models.user_photo import UserPhotoModel
from models.friendship import (
    friendship_table,
    is_friend_of_user as is_friend_of_user_internal,
)

DAYS_ALL = "ALL"
DAYS_WEEKENDS = "WEEKENDS"
DAYS_WEEK = "WEEK"


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
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
    is_private = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(255))
    dob = db.Column(db.Date)
    playing_days = db.Column(db.String(16), default=DAYS_ALL)
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    user_photos = db.relationship(
        "UserPhotoModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    user_games = db.relationship(
        "UserGameModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    # Based on
    # https://blog.ramosly.com/sqlalchemy-orm-setting-up-self-referential-many-to-many-relationships-866c97d9308b
    friends = db.relationship(
        "UserModel",
        secondary=friendship_table,
        primaryjoin=id == friendship_table.c.follower_id,
        secondaryjoin=id == friendship_table.c.followed_id,
        backref=db.backref("children"),
        lazy="dynamic",
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

    def update_email(self, email) -> None:
        """Sets a new email"""
        self.email = email
        auth.update_user(self.firebase_id, email=email)

    def update_password(self, new_password) -> None:
        """Sets a new password"""
        auth.update_user(self.firebase_id, password=new_password)

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def send_confirmation_email(self):
        link = request.url_root[:-1] + url_for(
            "confirmation", confirmation_id=self.most_recent_confirmation.id
        )
        subject = "Welcome to TopDog"
        text = f"""\
Your Play TopDog account has been successfully created. Welcome to the pack!
Your username is: {self.username}
Please click this link to activate your account: {link}
Want some help getting acquainted with the TopDog platform? Checkout our How To’s, FAQ’s, and Tutorial Videos. 
For any membership help, or questions please join our Discord or contact support@playtopdog.com. 
Ready to get in the game and start winning? http://lets.playtopdog.com/
Welcome to the world of TopDog, we look forward to watching you be rewarded for playing your favorite games!
Game On,
The TopDog Team

Website, Instagram, Facebook, Twitch
"""
        html = f"""\
<html>
   <div>
      <p>Your Play TopDog account has been successfully created. Welcome to the pack</p>
   </div>
   <div>
      <p>
        Your username is: {self.username}<br/>
        <a href="{link}">Please click this link to activate your account</a><br/>
        Want some help getting acquainted with the TopDog platform?<br/> 
        Checkout our 
            <a href="https://playtopdog.com/game-specs">How To&rsquo;s</a>, 
            <a href="https://playtopdog.com/faqs">FAQ&rsquo;s</a>, and 
            <a href="https://playtopdog.com/tutorial-videos-1">Tutorial Videos</a>.<br/>
        For any membership help, or questions please join our 
            <a href="https://discord.gg/vqbVxsFh">Discord</a> or contact 
            <a href = "mailto: abc@example.com">support@playtopdog.com</a>.<br/>
        Ready to get in the game and start winning?
            <a href="http://lets.playtopdog.com/">Let’s play TopDog</a>, <br/>
        Welcome to the world of TopDog, we look forward to watching you be 
        rewarded for playing your favorite games!<br/>
        Game On,<br/>
        The TopDog Team
      </p>
   </div>
   <p>
   <a href="https://playtopdog.com/">Website</a>, 
   <a href="https://www.instagram.com/playtopdog/">Instagram</a>, 
   <a href="https://www.facebook.com/playtopdog">Facebook</a>, 
   <a href="https://www.twitch.tv/playtopdog">Twitch</a></p>
</html>
"""
        return send_email([self.email], subject, text, html)

    @classmethod
    def get_top_earners(cls, days=7):
        sql = """
        with t as (
            select SUM(t2.credit_change) as credit_change , t2.user_id from transactions t2
                    where t2.created_at >= :time_ago
            group by t2.user_id 
        ) select
             u.*,
             coalesce(t.credit_change, 0) as credit_change from users u
            left join t on t.user_id = u.id
          order by COALESCE(t.credit_change, 0) desc
        """
        time_ago = datetime.today() - timedelta(days=days)
        data = db.engine.execute(text(sql), time_ago=time_ago).fetchall()
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

    def is_friend_of_user(self, other_id):
        return is_friend_of_user_internal(self.id, other_id)

    def add_friend(self, other_id):
        insert = friendship_table.insert().values(
            [
                dict(follower_id=self.id, followed_id=other_id),
                dict(follower_id=other_id, followed_id=self.id),
            ]
        )
        db.engine.execute(insert)

    def remove_friend(self, other_id):
        remove = friendship_table.delete().where(
            or_(
                and_(
                    friendship_table.c.follower_id == self.id,
                    friendship_table.c.followed_id == other_id,
                ),
                and_(
                    friendship_table.c.follower_id == other_id,
                    friendship_table.c.followed_id == self.id,
                ),
            )
        )
        db.engine.execute(remove)

    def get_friends(self):
        """Gets friends of user"""
        sql = """
           select u.* from users u
             inner join friendships f on f.followed_id = u.id
           where f.follower_id = :id
        """
        query = (
            db.session.query(self.__class__)
            .from_statement(text(sql))
            .params(id=self.id)
        )
        return query.all()

    def can_show_all_info(self, other_id) -> bool:
        """Returns if a user can show all the data"""
        if self.id == other_id:
            return True
        if self.is_private and not self.is_friend_of_user(other_id):
            return False
        return True

    @classmethod
    def get_public_users(cls):
        """Returns a list of users, this is used for the public user list"""
        sql = """
        SELECT u.id, u.name, u.last_name, u.avatar, u.username
            FROM users u
        ORDER BY u.id ASC
        """
        results = db.engine.execute(text(sql)).fetchall()
        return [dict(r) for r in results]

    def can_challenge_user(self, other_id):
        """Returns if a user can be challenged"""
        if self.id == int(other_id):
            return False, "Can't challenge yourself"
        other_user = UserModel.find_by_id(other_id)
        if other_user is None:
            return False, "User not found"
        if not other_user.is_private:
            return True, None
        is_friend = self.is_friend_of_user(other_id)
        if is_friend:
            return True, None
        else:
            return (
                False,
                "You can't challenge a user that's private and not your friend",
            )

    def get_credits(self):
        sql = """select t.credit_total from transactions t 
        where user_id = :user_id order by id desc limit 1"""
        data = db.engine.execute(text(sql), user_id=self.id).fetchone()
        if data is None:
            return 0
        return data["credit_total"]

    def has_user_game(self, game_id, console_id):
        sql = """select 1 from user_games u WHERE u.user_id = :user_id 
            AND u.game_id = :game_id
            AND u.console_id = :console_id
        """
        data = db.engine.execute(
            text(sql), user_id=self.id, game_id=game_id, console_id=console_id
        ).fetchone()
        return data is not None

    def update_user_games(self, user_games):
        connection = db.engine.connect()
        transaction = connection.begin()
        sql_delete = "DELETE FROM user_games u WHERE u.user_id = :user_id"
        connection.execute(text(sql_delete), user_id=self.id)
        sql_insert = text(
            "INSERT INTO user_games (game_id, console_id, gamertag, level, user_id) "
            "VALUES (:game_id, :console_id, :gamertag, :level, :user_id)"
        )
        for i in user_games:
            connection.execute(
                sql_insert,
                game_id=i["game_id"],
                console_id=i["console_id"],
                gamertag=i["gamertag"],
                level=i["level"],
                user_id=self.id,
            )
        transaction.commit()
