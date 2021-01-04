from flask import g

from tests.base import BaseAPITestCase
from tests.utils import create_fixtures


class TestCreditEndpoints(BaseAPITestCase):
    def test_get_credits(self):
        with self.app_context():
            fixtures = create_fixtures()
            g.claims = {"uid": fixtures["user_login"].firebase_id}
            with self.test_client() as c:
                rv = c.get("/credit")
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                self.assertAlmostEqual(
                    json_data["credit_total"], 10, "Wrong credit total"
                )
