from flask_restful import Resource
from flask import request, g
from firebase_admin import auth
from marshmallow import ValidationError

from decorators import check_token, check_is_admin
from utils.claims import set_is_admin
from fb import pb
from requests import HTTPError
import json

from models.user import UserModel
from schemas.user import UserSchema
from schemas.admin_status import AdminStatusSchema
import logging

log = logging.getLogger(__name__)

user_schema = UserSchema()
admin_status_schema = AdminStatusSchema()


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


class SetAdminStatus(Resource):
    @classmethod
    @check_token
    @check_is_admin
    def post(cls, user_id):
        payload = admin_status_schema.load(request.get_json())
        user: UserModel = UserModel.find_by_id(user_id)
        set_is_admin(user.firebase_id, payload["is_admin"])
        return {"message": "Admin status set", **admin_status_schema.dump(payload)}
