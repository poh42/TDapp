from tests.base import BaseAPITestCase
import unittest
from unittest.mock import patch, Mock
import json
from models.user import UserModel

email = "test@topdog.com"
password = "Pa55w0rd"
username = "asdrubal"


class TestUserEndpoints(BaseAPITestCase):
    def test_signup(self):
        class TestClass:
            uid = 1

        with self.test_client() as c:
            with patch("firebase_admin.auth.create_user") as patched_create_user:
                patched_create_user.side_effect = (TestClass(),)
                data = json.dumps(
                    dict(email=email, password=password, username=username)
                )
                rv = c.post("/register", data=data, content_type="application/json")
                json_data = rv.get_json()
                self.assertEqual(
                    "User creation successful",
                    json_data["message"],
                    "Message is incorrect",
                )
                self.assertIsNotNone(
                    UserModel.find_by_username(username), "User creation failed"
                )
                self.assertEqual(rv.status_code, 201, "Wrong status code")

    def test_login(self):
        class TestClass:
            sign_in_with_email_and_password = Mock(return_value={"idToken": "MyToken"})

        with self.test_client() as c:
            with self.app_context():
                with patch("fb.pb.auth") as pb:
                    user = UserModel()
                    user.email = email
                    user.password = password
                    user.username = username
                    user.firebase_id = "dummy"
                    user.save()
                    pb.side_effect = (TestClass,)
                    data = json.dumps(dict(email=email, password=password))
                    rv = c.post("/login", data=data, content_type="application/json")
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 200, "Invalid status code")
                    self.assertDictEqual(
                        {"token": "MyToken"}, json_data, "A token should be returned"
                    )


if __name__ == "__main__":
    unittest.main()
