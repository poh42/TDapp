import secrets
from time import time

from models.confirmation import ConfirmationModel
from models.user import UserModel

users = {
    "maureen": {
        "firebase_id": "r4aoFsnrOJSOq07YGSvwhqJTgDL2",
        "username": "maureen",
        "name": "Maureen",
        "last_name": "Hernandez",
        "email": "maureen@example.com",
        "is_private": True,
    },
    "asdrubal": {
        "firebase_id": "1iOHjsMYg2g9rU9bLRPCSX2Kjc93",
        "username": "asdrubal",
        "name": "Asdrubal",
        "last_name": "Suarez",
        "email": "asdrubal@example.com",
        "is_private": False,
    },
    "roger": {
        "firebase_id": "bjhmjGZI2oUKnb3ZKEW86Qw8Xnm1",
        "username": "roger",
        "name": "Roger",
        "last_name": "Gonzalez",
        "email": "roger@example.com",
        "is_private": False,
    },
    "tomas": {
        "firebase_id": "wiS6jtUBI6h6EGqsbjrVq2l0GBp1",
        "username": "tomas",
        "name": "Tomas",
        "last_name": "Peralta",
        "email": "tom@example.com",
        "is_private": False,
    },
    "phil": {
        "firebase_id": "yQ4cwuCBy7e0eCibSIZ0DkAR7hn1",
        "username": "phil",
        "name": "Phillip",
        "last_name": "Oh",
        "email": "phil@example.com",
        "is_private": True,
    },
    "ryan": {
        "firebase_id": "zanyylsS3JP85YNiRc3kBLGQixB2",
        "username": "ryan",
        "name": "Ryan",
        "last_name": "Ross",
        "email": "ryan@example.com",
        "is_private": False,
    },
    "noah": {
        "firebase_id": "XcRls82ASCMts9hA8hhIKPtINCo2",
        "username": "noah",
        "name": "Noah",
        "last_name": "",
        "email": "noah@example.com",
        "is_private": False,
    },
}

# NOTE we are going to need to create working confirmations for each user in order for them to be able to log in


def create_user(user_data):
    user = UserModel(**user_data)
    user.save()
    confirmation = ConfirmationModel(user.id)
    confirmation.confirmed = True  # We override the default confirmation value
    confirmation.save_to_db()
    return user


def save():
    ret_val = dict()
    for key, value in users.items():
        user = create_user(value)
        ret_val[key] = user
    return ret_val
