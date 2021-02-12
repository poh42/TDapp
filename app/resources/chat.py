# Se me ocurren tres endpoints.

# Crear channel, que tendria como parametros
# user_id: El user id de la segunda persona que esta en el canal
# la primera persona se obtendria por el claim
# el user id se obtendria del firebase_id y el nickname seria el username
# El algoritmo seria algo asi,

"""
Chequear con el view user si los dos user ids existen, si no crearlos y setear la variable chat created a 1 de cada uno
Crear channel
"""
import os
import requests
from flask import g
from flask_restful import Resource

from decorators import check_token
from models.user import UserModel

API_TOKEN = os.environ.get("SENDBIRD_API_TOKEN")
API_URL = os.environ.get("SENDBIRD_API_URL")

if API_TOKEN is None:
    print("Warning: API TOKEN is None. Please check your settings")

if API_URL is None:
    print("Warning: API URL is None. Please check your settings")


def _create_user(user):
    data = {
        "user_id": user.firebase_id,
        "profile_url": "",
        "nickname": user.username,
    }
    api_headers = {"Api-Token": API_TOKEN}
    response = requests.post(
        f"{API_URL}/users", json=data, headers=api_headers
    )  # We might need to check if the user already exists
    if response:
        user.is_sendbird_user_created = True
        user.save()
    return response


def _create_channel(user1, user2):
    api_headers = {"Api-Token": API_TOKEN}
    user_ids = [user1.firebase_id, user2.firebase_id]
    data = {
        "user_ids": user_ids,
        "is_distinct": True,
    }
    return requests.post(f"{API_URL}/group_channels", headers=api_headers, json=data)


CODE_USER_EXISTS = (
    400202  # This is a code that specifies that the user was already created
)


class CreateChannel(Resource):
    @classmethod
    @check_token
    def post(cls, user_id):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        other_user = UserModel.find_by_id(user_id)
        if other_user is None:
            return {"message": "User not found"}, 404
        if not current_user.is_sendbird_user_created:
            response = _create_user(current_user)
            json_data = response.json()
            if not response and json_data.get("code") != CODE_USER_EXISTS:
                return {
                    "message": f"There was an error creating the user {current_user.username} in the chat"
                }, 500
        if not other_user.is_sendbird_user_created:
            response = _create_user(other_user)
            json_data = response.json()
            if not response and json_data.get("code") != CODE_USER_EXISTS:
                return {
                    "message": f"There was an error creating the user {other_user.username} in the chat"
                }, 500
        response = _create_channel(current_user, other_user)
        if response:
            return {
                "message": "Channel created",
                "channel_url": response.json().get("channel_url"),
            }, 201
        else:
            return {"message": "There was an error creating the channel"}, 500
