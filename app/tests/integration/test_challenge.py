from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.challenge_ import ChallengeModel


def get_challenge(challenges, name):
    for c in challenges:
        if c.name == name:
            return c
    return None


class TestIntegrationChallenge(BaseAPITestCase):
    def test_find_user_challenges(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            with self.subTest(msg="all challenges"):
                challenges = ChallengeModel.find_user_challenges(user_login.id)
                self.assertEqual(len(challenges), 2, "Wrong number of challenges")
            with self.subTest(msg="get upcoming challenges"):
                challenges = ChallengeModel.find_user_challenges(
                    user_login.id, upcoming=True
                )
                self.assertEqual(
                    len(challenges),
                    1,
                    "Wrong number of challenges in upcoming challenges call",
                )
                c = get_challenge(challenges, "Upcoming challenge")
                self.assertIsNotNone(c, "Upcoming challenge should not be none")
            with self.subTest(msg="get past challenges"):
                challenges = ChallengeModel.find_user_challenges(
                    user_login.id, last_results=10
                )
                self.assertEqual(
                    len(challenges),
                    1,
                    "Wrong number of challenges in get past challenges call",
                )
                c = get_challenge(challenges, "Challenge")
                self.assertIsNotNone(c, "Challenge should not be none")
                self.assertTrue(
                    hasattr(c, "results_1v1"), "It should have an attribute result_1v1"
                )
                result = c.results_1v1
                self.assertEqual(result.score_player_1, 1)
                self.assertEqual(result.score_player_2, 0)
