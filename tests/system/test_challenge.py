from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.challenge_ import ChallengeModel


class TestChallengeEndpoints(BaseAPITestCase):
    def test_challenge_get(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge: ChallengeModel = fixtures["challenge"]
            with self.test_client() as c:
                rv = c.get(f"/challenge/{challenge.id}")
                self.assertEqual(rv.status_code, 200, "Wrong status code")

    def test_challenge_delete(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge: ChallengeModel = fixtures["challenge"]
            with self.test_client() as c:
                rv = c.delete(
                    f"/challenge/{challenge.id}", content_type="application/json"
                )
                self.assertIsNone(ChallengeModel.find_by_id(challenge.id))
                self.assertEqual(rv.status_code, 200, "Wrong status code")
