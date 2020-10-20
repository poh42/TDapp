from flask_restful import Resource
from flask import request, g
from firebase_admin import auth
from marshmallow import ValidationError

from decorators import check_token, check_is_admin, check_is_admin_or_user_authorized
from utils.claims import set_is_admin
from fb import pb
from requests import HTTPError

import simplejson as json
from models.user import UserModel
from models.confirmation import ConfirmationModel
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
            confirmation = ConfirmationModel(user_instance.id)
            confirmation.save_to_db()
            user_instance.send_confirmation_email()
        except auth.EmailAlreadyExistsError as e:
            return {"message": "Email is already registered"}, 400
        except Exception as e:
            log.error(e)
            print(e)
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
            if (
                not user_instance.most_recent_confirmation
                or not user_instance.most_recent_confirmation.confirmed
            ):
                return {"message": "User not confirmed"}, 400
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
        """
        Set user as admin
        """
        payload = admin_status_schema.load(request.get_json())
        user: UserModel = UserModel.find_by_id(user_id)
        set_is_admin(user.firebase_id, payload["is_admin"])
        return {"message": "Admin status set", **admin_status_schema.dump(payload)}


class User(Resource):
    @classmethod
    @check_token
    @check_is_admin_or_user_authorized
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 400
        return {"message": "User found", "user": user_schema.dump(user)}

    @classmethod
    @check_token
    @check_is_admin_or_user_authorized
    def put(cls, user_id):
        """
        Edit user endpoint
               --
        """
        user: UserModel = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 400
        json_data = request.get_json()
        errors = user_schema.validate(json_data, partial=True)
        if errors:
            raise ValidationError(errors)
        if json_data.get("email") and user.email != json_data["email"]:
            if UserModel.find_by_email(json_data["email"]):
                raise ValidationError({"email": "Email already in use"})
            user.email = json_data["email"]
        if json_data.get("name"):
            user.name = json_data["name"]
        if json_data.get("playing_hours_begin") and json_data.get("playing_hours_end"):
            user.playing_hours_begin = json_data["playing_hours_begin"]
            user.playing_hours_end = json_data["playing_hours_end"]
        if json_data.get("range_bet_low") and json_data.get("range_bet_high"):
            user.range_bet_low = json_data["range_bet_low"]
            user.range_bet_high = json_data["range_bet_high"]
        if json_data.get("phone"):
            user.phone = json_data["phone"]
        if (
            json_data.get("is_active", None) is not None
            and hasattr(g, "claims")
            and g.claims.get("admin") is True
        ):
            user.is_active = json_data["is_active"]
        try:
            user.save()
        except Exception as e:
            print(e)
        if json_data.get("password"):
            user.update_password(json_data["password"])
        return {"message": "Edit successful", "user": user_schema.dump(user)}, 200
