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


class UserLogin(Resource):
    @classmethod
    def post(cls):
        pass
