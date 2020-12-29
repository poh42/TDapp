import unittest

from models.invite import InviteModel
from tests.base import BaseAPITestCase
from unittest.mock import patch, Mock, call
import json
from models.user import UserModel
from models.confirmation import ConfirmationModel
from models.user_game import UserGameModel
from flask import g
from db import db
from tests.utils import (
    create_dummy_user,
    password,
    username,
    email,
    avatar,
    create_dummy_console,
    create_dummy_game,
    create_fixtures,
)


class TestUserEndpoints(BaseAPITestCase):
    def test_signup(self):
        class TestClass:
            uid = 1

        with self.test_client() as c:
            with self.app_context():
                console = create_dummy_console()
                game = create_dummy_game()
                with patch("firebase_admin.auth.create_user") as patched_create_user:
                    with patch("models.user.send_email") as send_email:
                        patched_create_user.side_effect = (TestClass(),)
                        data = json.dumps(
                            dict(
                                email=email,
                                password=password,
                                username=username,
                                avatar=avatar,
                                user_games=[
                                    {
                                        "console_id": console.id,
                                        "game_id": game.id,
                                        "gamertag": "Test",
                                    }
                                ],
                            )
                        )
                        rv = c.post(
                            "/user/register", data=data, content_type="application/json"
                        )
                        json_data = rv.get_json()
                        self.assertEqual(
                            "User creation successful",
                            json_data["message"],
                            "Message is incorrect",
                        )
                        user = UserModel.find_by_username(username)
                        self.assertIsNotNone(user, "User creation failed")
                        self.assertEqual(user.avatar, avatar, "Avatar not found")
                        self.assertEqual(rv.status_code, 201, "Wrong status code")
                        send_email.assert_called_once()
                        args, kwargs = send_email.call_args
                        self.assertEqual(args[0][0], email)
                        self.assertEqual(
                            args[1], "Registration confirmation", "Wrong title"
                        )
                        self.assertIn(
                            "Please click to confirm your registration:",
                            args[2],
                            "Check if the message being sent is correct",
                        )
                        self.assertIn(
                            "Please click to confirm your registration:",
                            args[3],
                            "Check if the message being sent is correct",
                        )
                        user_games = UserGameModel.query.filter_by(
                            user_id=user.id
                        ).all()
                        self.assertEqual(
                            len(user_games),
                            1,
                            "More user games were created than intended",
                        )
                        user_game = user_games[0]
                        self.assertIsNotNone(user_game, "UserGameModel creation failed")
                        self.assertEqual(
                            user_game.console_id, console.id, "Wrong console id"
                        )
                        self.assertEqual(user_game.game_id, game.id, "Wrong game id")
                        self.assertEqual(
                            user_game.level, "beginner", "Wrong user_game level"
                        )  # TODO check what should be default level

    def test_login(self):
        class TestClass:
            sign_in_with_email_and_password = Mock(return_value={"idToken": "MyToken"})

        with self.test_client() as c:
            with self.app_context():
                with patch("fb.pb.auth") as pb:
                    user = create_dummy_user()
                    confirmation = ConfirmationModel(user.id)
                    confirmation.confirmed = True
                    confirmation.save_to_db()
                    pb.side_effect = (TestClass,)
                    data = json.dumps(dict(email=email, password=password))
                    rv = c.post(
                        "/user/login", data=data, content_type="application/json"
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Invalid status code")
                    self.assertEqual(
                        json_data["token"], "MyToken", "A token should be provided"
                    )
                    self.assertIn(
                        "user", json_data, "User should be present in the body"
                    )

    def test_login_not_confirmed(self):
        with self.test_client() as c:
            with self.app_context():
                create_dummy_user()
                data = json.dumps(dict(email=email, password=password))
                rv = c.post("/user/login", data=data, content_type="application/json")
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 400, "Invalid status code")
                self.assertEqual(
                    json_data["message"],
                    "User not confirmed",
                    "User is by mistake already confirmed",
                )

    def test_set_admin(self):
        with self.test_client() as c:
            with self.app_context():
                user = create_dummy_user()
                with patch(
                    "firebase_admin.auth.set_custom_user_claims", return_value=None
                ) as set_custom_claims_mock:
                    data = json.dumps(dict(is_admin=True))
                    rv = c.post(
                        f"/user/set_admin/{user.id}",
                        data=data,
                        content_type="application/json",
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Invalid status code")
                    self.assertDictEqual(
                        {"message": "Admin status set", "is_admin": True},
                        json_data,
                        "Wrong response",
                    )
                    set_custom_claims_mock.assert_called_once_with(
                        user.firebase_id, {"admin": True}
                    )

    def test_user_settings(self):
        with self.test_client() as c:
            with self.app_context():
                user = create_dummy_user()
                with patch("firebase_admin.auth.update_user") as update_user_mock:

                    data = json.dumps(
                        {
                            "range_bet_low": 100,
                            "playing_hours_end": 20,
                            "range_bet_high": 120,
                            "phone": "885",
                            "email": "asdr@hotmail.com",
                            "name": "Test",
                            "last_name": "Another test",
                            "playing_hours_begin": 1,
                            "password": "1234567",
                            "is_private": True,
                            "dob": "1990-01-01",
                            "avatar": "my_avatar",
                            "username": "new_username",
                            "playing_days": "WEEKENDS",
                            "drivers_license": "https://my-license.com/",
                        }
                    )
                    rv = c.put(
                        f"/user/{user.id}", data=data, content_type="application/json"
                    )
                    json_data = rv.get_json()
                    user_data = json_data["user"]
                    calls = [
                        call(user.firebase_id, email="asdr@hotmail.com"),
                        call(user.firebase_id, password="1234567"),
                    ]
                    update_user_mock.assert_has_calls(calls)
                    self.assertEqual(user_data["avatar"], "my_avatar")
                    self.assertEqual(user_data["username"], "new_username")
                    self.assertEqual(user_data["playing_days"], "WEEKENDS")
                    self.assertEqual(
                        user_data["range_bet_low"], 100, "Range bet low should be 100"
                    )
                    self.assertEqual(
                        user_data["range_bet_high"], 120, "Range bet high should be 120"
                    )
                    self.assertEqual(user_data["phone"], "885", "Phone should be 885")
                    self.assertEqual(
                        user_data["email"], "asdr@hotmail.com", "Email should be valid"
                    )
                    self.assertEqual(
                        user_data["playing_hours_begin"],
                        1,
                        "Playing hours begin should be 1",
                    )
                    self.assertEqual(
                        user_data["playing_hours_end"],
                        20,
                        "Playing hours end should be 20",
                    )
                    self.assertEqual(
                        user_data["name"], "Test", "Name should be equal to test"
                    )
                    self.assertEqual(
                        user_data["last_name"],
                        "Another test",
                        "Name should be equal to Another test",
                    )
                    self.assertEqual(
                        user_data["dob"], "1990-01-01", "Date should be correct"
                    )
                    self.assertTrue(user_data["is_private"])
                    self.assertFalse(
                        "password" in user_data,
                        "Password should not be in the return data",
                    )
                    self.assertEqual(rv.status_code, 200, "Invalid status code")

    def test_user_settings_is_active(self):
        data = json.dumps({"is_active": False})
        with self.test_client() as c:
            with self.app_context():
                user = create_dummy_user()
                with patch("firebase_admin.auth.update_user") as update_user_mock:
                    from flask import g

                    g.claims = {"admin": True}
                    rv = c.put(
                        f"/user/{user.id}", data=data, content_type="application/json"
                    )
                    json_data = rv.get_json()
                    self.assertIn("user", json_data)
                    update_user_mock.assert_not_called()
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    new_user = UserModel.find_by_id(user.id)
                    self.assertFalse(new_user.is_active, "Value not changed")

    def test_user_get(self):
        with self.test_client() as c:
            with self.app_context():
                fixtures = create_fixtures()
                user = fixtures["user"]
                g.claims = {"uid": user.firebase_id}
                rv = c.get(f"/user/{user.id}", content_type="application/json")
                json_data = rv.get_json()
                user_data = json_data["user"]

                self.assertEqual(
                    user.name, user_data["name"], f"Name should be equal to {user.name}"
                )
                self.assertFalse(
                    "password" in user_data,
                    "Password should not be in the return data",
                )
                self.assertEqual(user.id, user_data["id"])
                self.assertEqual(user.firebase_id, user_data["firebase_id"])
                self.assertIsNotNone(user.avatar, "Avatar should not be None")
                with self.subTest("Private user"):
                    private_user = fixtures["private_user"]
                    rv = c.get(
                        f"/user/{private_user.id}", content_type="application/json"
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    user_data = json_data["user"]
                    self.assertNotIn("dob", user_data)
                    self.assertNotIn("phone", user_data)

    def test_get_user_list(self):
        with self.app_context():
            fixtures = create_fixtures()
            with self.test_client() as c:
                with self.subTest(get="all"):
                    rv = c.get("/users", content_type="application/json")
                    self.assertEqual(rv.status_code, 200)
                    json_data = rv.get_json()
                    self.assertTrue(len(json_data["users"]) > 0)
                with self.subTest(get="friends"):
                    g.claims = {"user_id": "dummy"}
                    rv = c.get("/users?friends=true")
                    self.assertEqual(rv.status_code, 200)
                    json_data = rv.get_json()
                    self.assertTrue(len(json_data["users"]) == 1)
                    self.assertEqual(
                        json_data["users"][0]["id"],
                        fixtures["second_user"].id,
                        "Wrong friend",
                    )
                with self.subTest(get="game"):
                    rv = c.get("/users?game=FIF", content_type="application/json")
                    self.assertEqual(rv.status_code, 200)
                    json_data = rv.get_json()
                    self.assertTrue(len(json_data["users"]) == 1)
                with self.subTest(get="game_not_found"):
                    rv = c.get("/users?game=not_found")
                    self.assertEqual(rv.status_code, 200)
                    json_data = rv.get_json()
                    self.assertTrue(len(json_data["users"]) == 0)

    def test_top_earners(self):
        with self.app_context():
            fixtures = create_fixtures()
            with self.test_client() as c:
                rv = c.get("/users/topEarners", content_type="application/json")
                self.assertEqual(rv.status_code, 200)
                json_data = rv.get_json()
                self.assertTrue(len(json_data["users"]) > 0)
                self.assertEqual(
                    json_data["users"][0]["credit_change"],
                    fixtures["transaction"].credit_change,
                )

    def test_remove_friend(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            user_to_befriend = fixtures["user"]
            user_login.add_friend(user_to_befriend.id)
            claims = {"uid": user_login.firebase_id}
            with self.test_client() as c:
                with patch.object(g, "claims", claims, create=True):
                    with self.subTest("removing a friendship"):
                        rv = c.post(
                            f"/user/{user_to_befriend.id}/deleteFriend",
                            content_type="application/json",
                        )
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 200, "Wrong status code")
                        self.assertFalse(
                            user_login.is_friend_of_user(user_to_befriend.id),
                            "Friendship relationship was removed",
                        )
                        self.assertEqual(json_data["message"], "Friend removed")
                    with self.subTest("trying to delete an already deleted friendship"):
                        rv = c.post(
                            f"/user/{user_to_befriend.id}/deleteFriend",
                            content_type="application/json",
                        )
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 400, "Wrong status code")
                        self.assertEqual(
                            json_data["message"],
                            "You are not a friend of this user",
                        )

    def test_add_user_invite(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            user_to_invite = fixtures["user"]
            claims = {"uid": user_login.firebase_id}
            with self.test_client() as c:
                with patch.object(g, "claims", claims, create=True):
                    with self.subTest("Inviting oneself"):
                        rv = c.post(
                            f"/user/invites/{user_login.id}/create",
                            content_type="application/json",
                        )
                        self.assertEqual(rv.status_code, 400, "Wrong status code")
                        json_data = rv.get_json()
                        self.assertEqual(
                            json_data["message"],
                            "Cannot invite the same user you are using for login",
                        )
                    with self.subTest("Creating an invitation"):
                        # Let's check if an invitation already exists
                        self.assertFalse(
                            InviteModel.is_already_invited(
                                user_login.id, user_to_invite.id
                            ),
                            "This should be false",
                        )
                        rv = c.post(
                            f"/user/invites/{user_to_invite.id}/create",
                            content_type="application/json",
                        )
                        json_data = rv.get_json()
                        self.assertEqual(json_data["message"], "Added invite")
                        self.assertEqual(rv.status_code, 201, "Wrong status code")
                        self.assertTrue(
                            InviteModel.is_already_invited(
                                user_login.id, user_to_invite.id
                            ),
                            "This should be True",
                        )
                    with self.subTest("Invitation already created"):
                        rv = c.post(
                            f"/user/invites/{user_to_invite.id}/create",
                            content_type="application/json",
                        )
                        self.assertEqual(rv.status_code, 400)
                        json_data = rv.get_json()
                        self.assertEqual(
                            json_data["message"],
                            "You already have an invitation to this user in place",
                        )

    def test_decline_invite(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            invite = fixtures["invite"]
            claims = {"uid": user_login.firebase_id}
            with patch.object(g, "claims", claims, create=True):
                with self.test_client() as c:
                    self.assertFalse(
                        invite.rejected,
                        "Before the test, the invite should not be rejected",
                    )
                    rv = c.post(
                        f"/user/invites/{invite.id}/decline",
                        content_type="application/json",
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    self.assertEqual(
                        json_data["message"],
                        "Invite declined",
                        "Wrong message returned",
                    )
                    new_invite = InviteModel.find_by_id(invite.id)
                    self.assertTrue(new_invite.rejected, "Invite should be rejected")

    def test_accept_invite(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            invite: InviteModel = fixtures["invite"]
            claims = {"uid": user_login.firebase_id}
            with patch.object(g, "claims", claims, create=True):
                with self.test_client() as c:
                    self.assertFalse(invite.accepted)
                    self.assertFalse(invite.rejected)
                    self.assertTrue(invite.pending)
                    rv = c.post(
                        f"/user/invites/{invite.id}/accept",
                        content_type="application/json",
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 201, "Wrong status code")
                    self.assertEqual(json_data["message"], "Friendship added")
                    new_invite = InviteModel.find_by_id(invite.id)
                    self.assertTrue(new_invite.accepted)
                    self.assertFalse(new_invite.rejected)
                    self.assertFalse(new_invite.pending)

    def test_get_user_invites(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            claims = {"uid": user_login.firebase_id}
            with patch.object(g, "claims", claims, create=True):
                with self.test_client() as c:
                    rv = c.get(f"/user/invites")
                    self.assertEqual(rv.status_code, 200)
                    json_data = rv.get_json()
                    invites = json_data["invites"]
                    self.assertEqual(len(invites), 1, "Wrong invite length")
                    invite = invites[0]
                    self.assertIn(
                        "user_inviting",
                        invite,
                        "User invite is not on the user_invited endpoint",
                    )

    def test_get_friends(self):
        with self.app_context():
            fixtures = create_fixtures()
            user = fixtures["user"]
            # We add this friend here so we don't make other tests to fail
            user.add_friend(fixtures["user_login"].id)
            with self.test_client() as c:
                rv = c.get(f"/user/{user.id}/friends", content_type="application/json")
                self.assertEqual(rv.status_code, 200)
                json_data = rv.get_json()
                self.assertEqual(
                    len(json_data["friends"]), 2, "Wrong number of friends"
                )

    def test_is_friend_of(self):
        with self.app_context():
            fixtures = create_fixtures()
            user = fixtures["user"]
            user2 = fixtures["second_user"]
            with self.test_client() as c:
                with self.subTest(is_friend=True):
                    rv = c.get(f"/user/isFriend/{user.id}/{user2.id}")
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    json_data = rv.get_json()
                    self.assertTrue(json_data["is_friend"], "Friend should be true")
                with self.subTest(is_friend=True, reversed_order=True):
                    rv = c.get(f"/user/isFriend/{user2.id}/{user.id}")
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    json_data = rv.get_json()
                    self.assertTrue(json_data["is_friend"], "Friend should be true")
                user.remove_friend(user2.id)
                with self.subTest(is_friend=False):
                    rv = c.get(f"/user/isFriend/{user.id}/{user2.id}")
                    self.assertEqual(rv.status_code, 200, "Wrong status code")
                    json_data = rv.get_json()
                    self.assertFalse(json_data["is_friend"], "Friend should be false")

    def test_get_public_user_list(self):
        with self.app_context():
            fixtures = create_fixtures()
            with self.test_client() as c:
                rv = c.get("/users/public")
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                self.assertGreater(
                    len(json_data["users"]), 0, "User should be returned"
                )
