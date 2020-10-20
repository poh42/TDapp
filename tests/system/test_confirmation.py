from tests.base import BaseAPITestCase
from tests.utils import create_dummy_user
from models.confirmation import ConfirmationModel
from unittest.mock import patch


class TestConfirmationEndpoints(BaseAPITestCase):
    def test_confirmation_endpoint(self):
        with self.test_client() as c:
            with self.app_context():
                user = create_dummy_user()
                confirmation = ConfirmationModel(user.id)
                confirmation.id = "dummy"
                confirmation.save_to_db()
                self.assertFalse(
                    confirmation.confirmed,
                    "Confirmation confirmed should be false at the beginning of the test",
                )
                with patch(
                    "resources.confirmation.render_template", return_value=""
                ) as rt:
                    rv = c.get("/user/confirm/dummy")
                    self.assertEqual(rv.status_code, 200)
                    rt.assert_called_once_with(
                        "confirmation_page.html", email=user.email
                    )
                    self.assertTrue(
                        ConfirmationModel.find_by_id("dummy").confirmed,
                        "Now Confirmation.confirmed it should be true",
                    )
