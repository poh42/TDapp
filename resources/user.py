from flask_restful import Resource
from flask import request
from firebase_admin import auth

from models.user import UserModel
from schemas.user import UserSchema
import logging

log = logging.getLogger(__name__)

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        json_data = request.get_json()
        user_instance: UserModel = user_schema.load(json_data)
        try:
            user_firebase = auth.create_user(
                email=user_instance.email, password=json_data["password"]
            )
            user_instance.firebase_id = user_firebase.uid
            user_instance.save()
        except auth.EmailAlreadyExistsError as e:
            return {"message": "Email is already registered"}, 400
        except Exception as e:
            log.error(e)
            return {"message": "There was an error creating the user"}, 400
        return (
            {
                "message": "User creation successful",
                "user": user_schema.dumps(user_instance),
            },
            201,
        )


class UserLogin(Resource):
    @classmethod
    def post(cls):
        pass
