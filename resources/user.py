from flask_restful import Resource
from flask import request, jsonify
from firebase_admin import auth
from marshmallow import ValidationError

from decorators import check_token, check_is_admin, check_is_admin_or_user_authorized
from utils.claims import set_is_admin
from fb import pb
from requests import HTTPError

import simplejson as json
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


class User(Resource):
    @classmethod
    @check_token
    @check_is_admin_or_user_authorized
    def put(cls, user_id):
        """
        Edit user endpoint
               ---
               description: Edits user settings
               tags:
                - user
               produces:
                - application/json
               parameters:
               - in: "body"
                 name: "body"
                 description: |
                    User settings to be edited. All fields are optional however if
                    playing_hours_begin is specified then playing_hours_end
                    should be specified.\n
                    Same case occurs with range_bet_low and range_bet_high attributes.
                 schema:
                   type: object
                   properties:
                     playing_hours_begin:
                        type: integer
                        minimum: 0
                        maximum: 23
                     playing_hours_end:
                        type: integer
                        minimum: 0
                        maximum: 23
                     range_bet_low:
                        type: number
                        minimum: 0
                     range_bet_high:
                        type: number
                        minimum: 0
                     phone:
                        type: string
                     name:
                        type: string
                     password:
                        type: string
               responses:
                   200:
                       description: User settings edited
                       schema:
                           type: object
                           properties:
                             message:
                                description: A success message
                                type: string
                             user:
                                description: The user
                                schema: User
                                example:
                                    id: 1
                                    email: user@example.com"
                                    username: "kyloRen"
                                    firebase_id: "string"
                                    last_active: "2019-08-24T14:15:22Z"
                                    accepted_terms: true
                                    is_banned: true
                                    playing_hours_begin: "2019-08-24T14:15:22Z"
                                    playing_hours_end: "2019-08-24T14:15:22Z"
                                    range_bet_low: 0
                                    range_bet_high: 0
                                    name: "example.com"
                                    phone: "string"
        """
        user: UserModel = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 400
        json_data = request.get_json()
        errors = user_schema.validate(json_data, partial=True)
        if errors:
            raise ValidationError(errors)
        if json_data.get("email"):
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
        try:
            user.save()
        except Exception as e:
            print(e)
        if json_data.get("password"):
            user.update_password(json_data["password"])
        return {"message": "Edit successful", "user": user_schema.dump(user)}, 200
