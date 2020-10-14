from tests.base import BaseAPITestCase
import unittest
from unittest.mock import patch
import json
from models.user import UserModel

email = "test@topdog.com"
password = "Pa55w0rd"
username = "asdrubal"


class TestClass:
    uid = 1


class TestUserEndpoints(BaseAPITestCase):
    def test_signup(self):
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


if __name__ == "__main__":
    unittest.main()
