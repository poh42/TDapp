from flask_restful import Resource
from flask import request
from firebase_admin import auth
from marshmallow import ValidationError
from fb import pb
from requests import HTTPError
import json

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
                "user": user_schema.dump(user_instance),
            },
            201,
        )


class UserLogin(Resource):
    @classmethod
    def post(cls):
        json_data = request.get_json()
        errors = user_schema.validate(json_data, partial=("username",))
        if errors:
            raise ValidationError(errors)
        email = json_data["email"]
        password = json_data["password"]
        user_instance = UserModel.find_by_email(email)
        if user_instance:
            try:
                user = pb.auth().sign_in_with_email_and_password(email, password)
                jwt = user["idToken"]
                return {"token": jwt}, 200
            except HTTPError as e:
                try:
                    error_data = json.loads(e.strerror)
                    if (
                        error_data
                        and error_data.get("error")
                        and error_data["error"].get("message", "") == "INVALID_PASSWORD"
                    ):
                        return {"message": "Invalid password"}, 400
                    else:
                        return {"message": "There was an error logging in"}, 400
                except:
                    return {"message": "There was an error logging in"}, 400
            except Exception as e:
                log.error(e.__class__.__name__)
                log.error(e)
                return {"message": "There was an error logging in"}, 400
        else:
            return {"message": "User not found"}
