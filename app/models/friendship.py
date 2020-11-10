from sqlalchemy import text

from db import db

friendship_table = db.Table(
    "friendships",
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


def is_friend_of_user(user_1_id, user_2_id):
    sql = "SELECT 1 from friendships f WHERE f.follower_id = :user_1_id AND f.followed_id = :user_2_id LIMIT 1"
    results = db.engine.execute(
        text(sql), user_1_id=user_1_id, user_2_id=user_2_id
    ).fetchall()
    return len(results) > 0
