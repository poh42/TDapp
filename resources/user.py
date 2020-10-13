from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
# from flask_jwt_extended import create_access_token, create_refresh_token
# from libs.strings import gettext
# from models.user import UserModel
# from schemas.user import UserSchema

# user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        pass

class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """

    @classmethod
    def get(cls, user_id: int):
        pass

    @classmethod
    def delete(cls, user_id: int):
        pass


class UserLogin(Resource):
    @classmethod
    def post(cls):
        pass
