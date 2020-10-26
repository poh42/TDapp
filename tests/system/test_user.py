from tests.base import BaseAPITestCase
from unittest.mock import patch, Mock, PropertyMock
import json
from models.user import UserModel
from models.confirmation import ConfirmationModel
from tests.utils import create_dummy_user, password, username, email, avatar


class TestUserEndpoints(BaseAPITestCase):
    def test_signup(self):
        class TestClass:
            uid = 1

        with self.test_client() as c:
            with patch("firebase_admin.auth.create_user") as patched_create_user:
                with patch("utils.mailgun.Mailgun.send_email") as send_email:
                    patched_create_user.side_effect = (TestClass(),)
                    data = json.dumps(
                        dict(email=email, password=password, username=username, avatar=avatar)
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
                    self.assertIsNotNone(
                        user, "User creation failed"
                    )
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
                    print(args)

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
                    self.assertDictEqual(
                        {"token": "MyToken"}, json_data, "A token should be returned"
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
                            "playing_hours_begin": 1,
                            "password": "1234567",
                            "allow_public_challenges": False,
                        }
                    )
                    rv = c.put(
                        f"/user/{user.id}", data=data, content_type="application/json"
                    )
                    json_data = rv.get_json()
                    user_data = json_data["user"]
                    update_user_mock.assert_called_once_with(
                        user.firebase_id, password="1234567"
                    )
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
                    self.assertFalse(user_data["allow_public_challenges"])
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
                user = create_dummy_user()
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
