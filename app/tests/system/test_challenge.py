from datetime import datetime, timedelta
import json
from unittest.mock import patch

from models.challenge_user import ChallengeUserModel
from models.user import UserModel
from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.challenge_ import ChallengeModel
from flask import g

from models.challenge_user import (
    ChallengeUserModel,
    STATUS_OPEN,
    STATUS_PENDING,
    STATUS_ACCEPTED,
    STATUS_DECLINED,
    STATUS_READY,
    STATUS_STARTED,
    STATUS_FINISHED,
    STATUS_COMPLETED,
    STATUS_DISPUTED,
    STATUS_SOLVED
)


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
                self.assertEqual(
                    challenge_user["status_challenger"], "OPEN", "Wrong status"
                )
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
            challenge = fixtures["upcoming_challenge"]
            user = fixtures["user_login"]
            g.claims = {"user_id": user.firebase_id}
            with self.test_client() as c:
                with self.subTest("Good report"):
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

                with self.subTest("wrong challenge id"):
                    rv = c.post(
                        f"/challenge/3000/report",
                        data=data,
                        content_type="application/json",
                    )
                    json_data = rv.get_json()
                    self.assertEqual(rv.status_code, 400, "Wrong status code")
                    self.assertEqual(json_data["message"], "Challenge not found")
                with self.subTest("Challenge belongs to other user"):
                    g.claims = {"user_id": "dummy"}
                    rv = c.post(
                        f"/challenge/{challenge.id}/report",
                        data=data,
                        content_type="application/json",
                    )
                    self.assertEqual(rv.status_code, 400)
                    json_data = rv.get_json()
                    self.assertEqual(
                        json_data["message"], "This user cannot report this challenge"
                    )

    def test_post_challenge(self):
        with self.app_context():
            fixtures = create_fixtures()
            data = {
                "type": "Test",
                "game_id": fixtures["game"].id,
                "date": "2019-01-01T00:00:00",
                "buy_in": 10,
                "status": "OPEN",
                "due_date": "2019-01-01T00:00:00",
                "console_id": fixtures["console"].id,
            }
            with self.test_client() as c:
                g.claims = {"uid": fixtures["user_login"].firebase_id}
                rv = c.post(
                    "/challenge", data=json.dumps(data), content_type="application/json"
                )
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                challenge_created = json_data["challenge"]
                self.assertEqual(challenge_created["type"], data["type"], "Wrong type")
                self.assertEqual(
                    challenge_created["game_id"], data["game_id"], "Wrong game id"
                )
                self.assertAlmostEqual(
                    challenge_created["buy_in"], data["buy_in"], "Wrong buy in"
                )
                self.assertAlmostEqual(challenge_created["reward"], 20, "Wrong reward")
                self.assertEqual(challenge_created["date"], data["date"], "Wrong date")
                self.assertEqual(
                    challenge_created["status"], data["status"], "Wrong type"
                )

    def test_get_disputes(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge: ChallengeModel = fixtures["challenge"]
            with self.test_client() as c:
                rv = c.get(f"/challenge/{challenge.id}/report/dispute")
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                json_data = rv.get_json()
                self.assertTrue(
                    len(json_data["disputes"]) > 0,
                    "There should be disputes in the database",
                )

    def test_challenge_accept(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge_user: ChallengeUserModel = fixtures["challenge_user"]
            with self.test_client() as c:
                with self.subTest(shouldAccept=False, msg="Wrong user"):
                    g.claims = {"user_id": fixtures["user"].firebase_id}
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 400, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Cannot accept challenge from a different user",
                        json_data["message"],
                        "Wrong message",
                    )
                g.claims = {"user_id": fixtures["user_login"].firebase_id}
                with self.subTest(shouldAccept=True):
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 200, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge accepted", json_data["message"], "Wrong message"
                    )
                with self.subTest(shouldAccept=False, msg="Challenge accepted"):
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 400, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge already accepted",
                        json_data["message"],
                        "Wrong message",
                    )

    def test_challenge_decline(self):
        with self.app_context():
            fixtures = create_fixtures()
            challenge_user: ChallengeUserModel = fixtures["challenge_user"]
            with self.test_client() as c:
                with self.subTest(shouldAccept=False, msg="Wrong user"):
                    g.claims = {"user_id": fixtures["user"].firebase_id}
                    rv = c.post(f"/challenge/{challenge_user.id}/decline")
                    self.assertEqual(rv.status_code, 400, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Cannot decline challenge from a different user",
                        json_data["message"],
                        "Wrong message",
                    )
                g.claims = {"user_id": fixtures["user_login"].firebase_id}
                with self.subTest(shouldAccept=True):
                    rv = c.post(f"/challenge/{challenge_user.id}/decline")
                    self.assertEqual(rv.status_code, 200, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge declined", json_data["message"], "Wrong message"
                    )
                with self.subTest(shouldAccept=False, msg="Challenge declined"):
                    rv = c.post(f"/challenge/{challenge_user.id}/decline")
                    self.assertEqual(rv.status_code, 400, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge already declined",
                        json_data["message"],
                        "Wrong message",
                    )

    def test_challenges_users(self):
        with self.app_context():
            with self.test_client() as c:
                fixtures = create_fixtures()
                user_login = fixtures["user_login"]
                user_private = fixtures["private_user"]
                user_public_test = fixtures["user"]
                with self.subTest("user does not exist"):
                    claims = {"uid": "test"}
                    with patch.object(g, "claims", claims, create=True):
                        rv = c.get("/challenge/999999999999/user")
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 400)
                        self.assertEqual(json_data["message"], "User not found")
                with self.subTest("user login challenges"):
                    claims = {"uid": user_login.firebase_id, "admin": False}
                    with patch.object(g, "claims", claims, create=True):
                        rv = c.get(f"/challenge/{user_login.id}/user?upcoming=true")
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 200)
                        self.assertTrue(len(json_data["challenges"]) > 0)
                with self.subTest("user private login challenges"):
                    claims = {"uid": user_login.firebase_id, "admin": False}
                    with patch.object(g, "claims", claims, create=True):
                        rv = c.get(f"/challenge/{user_private.id}/user")
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 400)
                        self.assertEqual(
                            json_data["message"],
                            "User challenges for this user are private",
                        )
                with self.subTest("user private login as an admin"):
                    claims = {"uid": user_login.firebase_id, "admin": True}
                    with patch.object(g, "claims", claims, create=True):
                        rv = c.get(f"/challenge/{user_private.id}/user?lastResults=10")
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 200)
                        self.assertIn("challenges", json_data)
                with self.subTest("user get challenges of a public user"):
                    claims = {"uid": user_login.firebase_id, "admin": False}
                    with patch.object(g, "claims", claims, create=True):
                        rv = c.get(f"/challenge/{user_public_test.id}/user")
                        json_data = rv.get_json()
                        self.assertEqual(rv.status_code, 200)
                        self.assertIn("challenges", json_data)

    def test_challenge_status_update(self):
        with self.app_context():
            with self.test_client() as c:
                fixtures = create_fixtures()
                challenge: ChallengeModel = fixtures["challenge"]
                challenge_users: ChallengeUserModel = fixtures["challenge_user"]
                with self.subTest("Correct transition to READY"):
                    g.claims = {"uid": "myLbdKL8dFhipvanv4AnIUaJpqd2"}
                    challenge.date = datetime.now()
                    challenge.status = STATUS_ACCEPTED
                    challenge_users.status_challenger = STATUS_OPEN
                    challenge_users.status_challenged = STATUS_ACCEPTED
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 200, "Challenge updated successfully"
                    )
                    self.assertEqual(challenge.status, STATUS_ACCEPTED)
                    self.assertEqual(challenge_users.status_challenger, STATUS_OPEN)
                    self.assertEqual(challenge_users.status_challenged, STATUS_READY)
                with self.subTest("Correct transition to READY both users"):
                    g.claims = {"uid": "dummy_2"}
                    challenge.date = datetime.now()
                    challenge.status = STATUS_ACCEPTED
                    challenge_users.status_challenger = STATUS_OPEN
                    challenge_users.status_challenged = STATUS_READY
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 200, "Challenge updated successfully"
                    )
                    self.assertEqual(challenge.status, STATUS_READY)
                    self.assertEqual(challenge_users.status_challenger, STATUS_READY)
                    self.assertEqual(challenge_users.status_challenged, STATUS_READY)
                with self.subTest("Incorrect transition to READY - not in time frame"):
                    g.claims = {"uid": "dummy_2"}
                    challenge.date = datetime.now() - timedelta(minutes=10)
                    challenge.status = STATUS_ACCEPTED
                    challenge_users.status_challenger = STATUS_OPEN
                    challenge_users.status_challenged = STATUS_ACCEPTED
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 403, "Incorrect transition for challenge"
                    )
                    self.assertEqual(challenge.status, STATUS_ACCEPTED)
                    self.assertEqual(challenge_users.status_challenger, STATUS_OPEN)
                    self.assertEqual(challenge_users.status_challenged, STATUS_ACCEPTED)
                with self.subTest("Correct transition to COMPLETED"):
                    g.claims = {"uid": "dummy_2"}
                    challenge.status = STATUS_FINISHED
                    challenge_users.status_challenger = STATUS_FINISHED
                    challenge_users.status_challenged = STATUS_COMPLETED
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 200, "Challenge updated successfully"
                    )
                    self.assertEqual(challenge.status, STATUS_COMPLETED)
                    self.assertEqual(challenge_users.status_challenger, STATUS_COMPLETED)
                    self.assertEqual(challenge_users.status_challenged, STATUS_COMPLETED)
                with self.subTest("Correct transition to DISPUTED"):
                    g.claims = {"uid": "myLbdKL8dFhipvanv4AnIUaJpqd2"}
                    challenge.status = STATUS_COMPLETED
                    challenge_users.status_challenger = STATUS_COMPLETED
                    challenge_users.status_challenged = STATUS_COMPLETED
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 200, "Challenge updated successfully"
                    )
                    self.assertEqual(challenge.status, STATUS_DISPUTED)
                    self.assertEqual(challenge_users.status_challenger, STATUS_COMPLETED)
                    self.assertEqual(challenge_users.status_challenged, STATUS_DISPUTED)
                with self.subTest("User not in challenge"):
                    g.claims = {"uid": "dummy"}
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 403, "User does not belong to challenge"
                    )
                with self.subTest("Invalid challenge user status"):
                    g.claims = {"uid": "dummy_2"}
                    rv = c.put(f"/challenge/{challenge.id}/updateChallenge")
                    self.assertEqual(
                        rv.status_code, 403, "Invalid challenge user status"
                    )

    def test_direct_challenges(self):
        with self.app_context():
            fixtures = create_fixtures()
            with self.test_client() as c:
                g.claims = {"uid": fixtures["user_login"].firebase_id}
                rv = c.get("/challenges/direct")
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                challenges = json_data["challenges"]
                self.assertEqual(fixtures["direct_challenge"].id, challenges[0]["id"])
