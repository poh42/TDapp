from flask_restful import Resource
from flask import request, g
from firebase_admin import auth
from marshmallow import ValidationError

from decorators import check_token, check_is_admin, check_is_admin_or_user_authorized
from models.invite import InviteModel, STATUS_PENDING
from schemas.invite import InviteSchema
from schemas.user_game import BaseUserGameSchema
from utils.claims import set_is_admin
from fb import pb
from requests import HTTPError

import simplejson as json
from models.user import UserModel
from models.confirmation import ConfirmationModel
from models.user_game import UserGameModel
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
                return {"token": jwt, "user": user_schema.dump(user_instance)}, 200
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
        if json_data.get("is_private", None) is not None:
            user.is_private = json_data["is_private"]
        if json_data.get("phone"):
            user.phone = json_data["phone"]
        if (
            json_data.get("is_active", None) is not None
            and hasattr(g, "claims")
            and g.claims.get("admin") is True
        ):
            user.is_active = json_data["is_active"]
        if json_data.get("dob"):
            user.dob = json_data["dob"]
        if json_data.get("last_name"):
            user.last_name = json_data["last_name"]
        try:
            user.save()
        except Exception as e:
            print(e)
        if json_data.get("password"):
            user.update_password(json_data["password"])
        return {"message": "Edit successful", "user": user_schema.dump(user)}, 200


class UserList(Resource):
    @classmethod
    @check_token
    def get(cls):
        if request.args.get("topEarners"):
            return {"users": UserModel.get_top_earners()}, 200
        if request.args.get("friends"):
            claims = g.claims
            current_user = UserModel.find_by_firebase_id(claims["user_id"])
            return {"users": current_user.filter_by_friends()}, 200
        game_title = request.args.get("game")
        if game_title:
            return {"users": UserModel.filter_users_by_game(game_title)}, 200
        return {"users": UserModel.get_all_users()}, 200


class UserGamesLibrary(Resource):
    @classmethod
    @check_token
    @check_is_admin_or_user_authorized
    def put(cls, user_id):
        schema = BaseUserGameSchema()
        data: dict = schema.load(request.get_json())
        game_id = data.get("game_id")
        console_id = data.get("console_id")
        instance = UserGameModel.get_user_game_instance(user_id, game_id, console_id)
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save_to_db()
        return {"user_game": schema.dump(instance)}, 200


class AddFriend(Resource):
    @check_token
    def post(self, user_id):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        if current_user.is_friend_of_user(user_id):
            return {"message": "You are already a friend of this user"}, 400
        current_user.add_friend(user_id)
        return {"message": "You are now a friend of this user"}, 201


class RemoveFriend(Resource):
    @check_token
    def post(self, user_id):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        if not current_user.is_friend_of_user(user_id):
            return {"message": "You are not a friend of this user"}, 400
        current_user.remove_friend(user_id)
        return {"message": "Friend removed"}, 200


class AddUserInvite(Resource):
    @check_token
    def post(self, user_id):
        if not UserModel.find_by_id(user_id):
            return {"message": "User not found"}, 404
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        if InviteModel.is_already_invited(current_user.id, user_id):
            return (
                {"message": "You already have an invitation to this user in place"},
                400,
            )
        if current_user.is_friend_of_user(user_id):
            return {"message": "You already are a friend of this user"}, 400
        invite = InviteModel(user_inviting_id=current_user.id, user_invited_id=user_id)
        invite.save_to_db()
        return {"message": "Added invite"}, 201


class DeclineInvite(Resource):
    @check_token
    def post(self, invite_id):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        invite: InviteModel = InviteModel.find_by_id(invite_id)
        if invite is None:
            return {"message": "Invite not found"}, 400
        if not (
            invite.user_invited_id == current_user.id
            or invite.user_inviting == current_user.id
        ):
            return {"message": "Can't reject other user's invite"}, 400
        invite.reject()
        invite.save_to_db()
        return {"message": "Invite declined"}, 200


class AcceptInvite(Resource):
    @check_token
    def post(self, invite_id):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        invite: InviteModel = InviteModel.find_by_id(invite_id)
        if invite is None:
            return {"message": "Invite not found"}, 400
        if invite.user_invited_id != current_user.id:
            return {"message": "Can't accept other user's invite"}, 400
        invite.accept()
        invite.save_to_db()
        current_user.add_friend(invite.user_inviting_id)
        return {"message": "Friendship added"}, 201


class GetInvites(Resource):
    @classmethod
    @check_token
    def get(cls):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        status = request.args.get("status", STATUS_PENDING)
        invites = InviteModel.get_user_invites(current_user.id, status=status)
        return {"invites": InviteSchema().dump(invites, many=True)}


class UserFriends(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user is None:
            return {"message": "User not found"}, 400
        friends = user.get_friends()
        return {"friends": user_schema.dump(friends, many=True)}


class IsFriend(Resource):
    @classmethod
    def get(cls, user_1_id, user_2_id):
        user1 = UserModel.find_by_id(user_1_id)
        user2 = UserModel.find_by_id(user_2_id)
        if user1 is None and user2 is None:
            return {"message": "Users not found"}, 400
        if user1 is None:
            return {"message": f"User {user_1_id} not found"}, 400
        if user2 is None:
            return {"message": f"User {user_2_id} not found"}, 400
        is_friend = user1.is_friend_of_user(user_2_id)
        if is_friend:
            message = f"User {user_1_id} is friend of {user_2_id}"
        else:
            message = f"User {user_1_id} is not friend of {user_2_id}"
        return {"is_friend": is_friend, "message": message}, 200
