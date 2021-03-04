import os
import requests
from flask import g, request
from flask_restful import Resource

from decorators import check_token
from models.user import UserModel
from schemas.chat import SendMessageSchema

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


def _send_message(channel_url, user_id, message):
    api_headers = {"Api-Token": API_TOKEN}
    data = {
        "message_type": "MESG",
        "user_id": user_id,
        "message": message,
    }
    return requests.post(
        f"{API_URL}/group_channels/{channel_url}/messages",
        headers=api_headers,
        json=data,
    )


def _is_member_channel(channel_url, user_id):
    print(channel_url, user_id)
    api_headers = {"Api-Token": API_TOKEN}
    return requests.get(
        f"{API_URL}/group_channels/{channel_url}/members/{user_id}", headers=api_headers
    )


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
            json_data = response.json()
            return {
                "message": "Channel created",
                "data": {
                    "channel_url": json_data.get("channel_url"),
                    "created_at": json_data.get("created_at"),
                },
            }, 201
        else:
            return {"message": "There was an error creating the channel"}, 500


class SendMessage(Resource):
    @classmethod
    @check_token
    def post(cls):
        data = SendMessageSchema().load(request.get_json())
        response = _send_message(
            data.get("channel_url"), g.claims["uid"], data.get("message")
        )
        if response:
            message = response.json()
            value = {
                "created_at": message.get("created_at"),
                "message": message.get("message"),
                "message_id": message.get("message_id"),
                "nickname": message.get("user").get("nickname"),
            }
            return {"message": "Message sent", "data": value}, 201
        else:
            print(response.content)
            return {"message": "There was an error sending the message"}, 500


def _list_messages(channel_url, message_ts, prev_limit=15, next_limit=15):
    api_headers = {"Api-Token": API_TOKEN}
    params = {
        "message_ts": message_ts,
        "prev_limit": prev_limit,
        "next_limit": next_limit,
    }
    return requests.get(
        f"{API_URL}/group_channels/{channel_url}/messages",
        params=params,
        headers=api_headers,
    )


class ListMessagesFromChannel(Resource):
    @classmethod
    @check_token
    def get(cls, channel_url, timestamp):
        current_user = UserModel.find_by_firebase_id(g.claims["uid"])
        response = _is_member_channel(channel_url, current_user.firebase_id)
        if response:
            content = response.json()
            if not content.get("is_member"):
                return {"message": "User is not member of channel"}, 400
        else:
            return {"message": "User is not member of channel"}, 400

        prev_limit = request.args.get("prev_limit", type=int, default=15)
        next_limit = request.args.get("next_limit", type=int, default=15)

        if prev_limit < 1:
            prev_limit = 1
        if next_limit < 1:
            next_limit = 1

        data = _list_messages(channel_url, timestamp, prev_limit, next_limit)
        json_data = data.json()
        ret_val = []
        for message in json_data["messages"]:
            value = {
                "created_at": message.get("created_at"),
                "message": message.get("message"),
                "message_id": message.get("message_id"),
                "nickname": message.get("user").get("nickname"),
            }
            ret_val.append(value)
        return {"messages": ret_val}, 200
