import json

from models.challenge_user import ChallengeUserModel
from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.challenge_ import ChallengeModel
from flask import g


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

    def test_challenge_edit(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge: ChallengeModel = fixtures["challenge"]
            data = json.dumps(
                {
                    "type": "1v1",
                    "name": "Edited",
                    "buy_in": 100,
                    "reward": 1000,
                    "status": "ended",
                    "due_date": "2019-01-01 00:00:00",
                }
            )
            with self.test_client() as c:
                rv = c.put(
                    f"/challenge/{challenge.id}",
                    data=data,
                    content_type="application/json",
                )
                json_data = rv.get_json()
                challenge_edited = json_data["challenge"]
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                self.assertEqual(challenge_edited["type"], "1v1", "Wrong type")
                self.assertEqual(challenge_edited["name"], "Edited", "Wrong name")
                self.assertAlmostEqual(challenge_edited["buy_in"], 100, "Wrong buy in")
                self.assertAlmostEqual(challenge_edited["reward"], 1000, "Wrong reward")
                self.assertEqual(
                    challenge_edited["due_date"],
                    "2019-01-01T00:00:00",
                    "Due date is not being edited",
                )

    def test_challenge_list(self):
        with self.app_context():
            create_fixtures()
            with self.test_client() as c:
                rv = c.get("/challenges")
                json_data = rv.get_json()
                self.assertTrue(len(json_data["challenges"]) > 0, "Wrong length")
                self.assertEqual(rv.status_code, 200)

    def test_challenge_results_by_user(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge = fixtures["challenge"]
            with self.test_client() as c:
                rv = c.get(f"/challenges/{challenge.id}/getResultsUser")
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                results = json_data["results"]
                self.assertEqual(len(results), 1, "Wrong number of results")
                self.assertEqual(
                    results[0]["challenge_id"], challenge.id, "Wrong challenge id"
                )
                self.assertEqual(
                    results[0]["challenge_name"], challenge.name, "Wrong challenge name"
                )
                self.assertEqual(results[0]["game_name"], "FIFA", "Wrong game name")

    def test_challenge_someone(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge = fixtures["challenge"]
            second_user = fixtures["second_user"]
            with self.test_client() as c:
                g.claims = {"user_id": "dummy"}
                data = json.dumps({"wager_id": challenge.id})
                rv = c.post(
                    f"/challenge/{second_user.id}/create",
                    data=data,
                    content_type="application/json",
                )
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 200)
                challenge_user = json_data["challenge_user"]
                self.assertEqual(challenge_user["status"], "OPEN", "Wrong status")
                self.assertEqual(
                    challenge_user["wager_id"], challenge.id, "Wrong challenge id"
                )

    def test_get_result(self):
        with self.app_context():
            fixtures = create_fixtures()
            result = fixtures["result_1v1"]
            with self.test_client() as c:
                rv = c.get(
                    f"/challenge/{result.challenge_id}/getResultsChallenge",
                    content_type="application/json",
                )
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                results = json_data["results"]
                self.assertEqual(
                    result.score_player_1,
                    results["score_player_1"],
                    "Wrong score for player 1",
                )
                self.assertEqual(
                    result.score_player_2,
                    results["score_player_2"],
                    "Wrong score for player 1",
                )
                self.assertIn("played", results, "Played should be in the results")

    def test_create_dispute(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge = fixtures["challenge"]
            g.claims = {"user_id": "dummy"}
            with self.test_client() as c:
                comment = "This is a comment"
                data = json.dumps({"comments": comment})
                rv = c.post(
                    f"/challenge/{challenge.id}/report",
                    data=data,
                    content_type="application/json",
                )
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                dispute = json_data["dispute"]
                self.assertEqual(dispute["comments"], comment, "Wrong comment")

    def test_post_challenge(self):
        with self.app_context():
            fixtures = create_fixtures()
            data = {
                "type": "Test",
                "name": "",
                "game_id": fixtures["game"].id,
                "date": "2019-01-01T00:00:00",
                "buy_in": 10,
                "reward": 100,
                "status": "OPEN",
                "due_date": "2019-01-01T00:00:00",
            }
            with self.test_client() as c:
                rv = c.post(
                    "/challenge", data=json.dumps(data), content_type="application/json"
                )
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                challenge_created = json_data["challenge"]
                self.assertEqual(challenge_created["type"], data["type"], "Wrong type")
                self.assertEqual(challenge_created["name"], data["name"], "Wrong name")
                self.assertEqual(
                    challenge_created["game_id"], data["game_id"], "Wrong game id"
                )
                self.assertAlmostEqual(
                    challenge_created["buy_in"], data["buy_in"], "Wrong buy in"
                )
                self.assertAlmostEqual(
                    challenge_created["reward"], data["reward"], "Wrong reward"
                )
                self.assertEqual(challenge_created["date"], data["date"], "Wrong date")
                self.assertEqual(
                    challenge_created["due_date"], data["due_date"], "Wrong due_date"
                )
                self.assertEqual(
                    challenge_created["status"], data["status"], "Wrong type"
                )
