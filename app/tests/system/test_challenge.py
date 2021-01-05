from datetime import datetime, timedelta
import json
from unittest.mock import patch

from models.challenge_user import ChallengeUserModel
from models.user_challenge_scores import UserChallengeScoresModel
from models.user import UserModel
from models.results_1v1 import Results1v1Model
from models.transaction import TransactionModel
from models.user_game import UserGameModel
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
    STATUS_SOLVED,
)


class TestChallengeEndpoints(BaseAPITestCase):
    def post_user_game(self, fixtures):
        user_game = UserGameModel()
        user_game.game_id = fixtures["game"].id
        user_game.user_id = fixtures["user_login"].id
        user_game.console_id = fixtures["console"].id
        user_game.level = "dummy"
        user_game.gamertag = "dummy"
        user_game.save_to_db()

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

    def test_post_direct_challenge(self):
        with self.app_context():
            fixtures = create_fixtures()
            self.post_user_game(fixtures)
            with self.test_client() as c:
                with self.subTest("Private user"):
                    data = {
                        "type": "1v1",
                        "game_id": fixtures["game"].id,
                        "date": "2019-01-01T00:00:00",
                        "buy_in": 10,
                        "console_id": fixtures["console"].id,
                        "challenged_id": fixtures["private_user"].id,
                    }
                    g.claims = {"uid": fixtures["user_login"].firebase_id}
                    rv = c.post(
                        "/challenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(rv.status_code, 400, "Wrong status code.")
                    json_data = rv.get_json()
                    self.assertEqual(
                        json_data["message"],
                        "You can't challenge a user that's private and not your friend",
                    )
                with self.subTest("User not found"):
                    data = {
                        "type": "1v1",
                        "game_id": fixtures["game"].id,
                        "date": "2019-01-01T00:00:00",
                        "buy_in": 10,
                        "console_id": fixtures["console"].id,
                        "challenged_id": 1000000,
                    }
                    g.claims = {"uid": fixtures["user_login"].firebase_id}
                    rv = c.post(
                        "/challenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(rv.status_code, 400, "Wrong status code.")
                    json_data = rv.get_json()
                    self.assertEqual(json_data["message"], "User not found")
                with self.subTest("Challenge yourself"):
                    data = {
                        "type": "1v1",
                        "game_id": fixtures["game"].id,
                        "date": "2019-01-01T00:00:00",
                        "buy_in": 10,
                        "console_id": fixtures["console"].id,
                        "challenged_id": fixtures["user_login"].id,
                    }
                    g.claims = {"uid": fixtures["user_login"].firebase_id}
                    rv = c.post(
                        "/challenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(rv.status_code, 400, "Wrong status code.")
                    json_data = rv.get_json()
                    self.assertEqual(json_data["message"], "Can't challenge yourself")

    def test_create_challenge_no_transactions(self):
        with self.app_context():
            fixtures = create_fixtures()
            data = {
                "type": "Test",
                "game_id": fixtures["game"].id,
                "date": "2019-01-01T00:00:00",
                "buy_in": 10,
                "console_id": fixtures["console"].id,
            }
            with self.test_client() as c:
                with patch(
                    "resources.challenge_.TransactionModel.find_by_user_id",
                    return_value=None,
                ):
                    g.claims = {"uid": fixtures["user"].firebase_id}
                    rv = c.post(
                        f"/challenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(rv.status_code, 403, "Wrong status code")
                    json_data = rv.get_json()
                    self.assertEqual(
                        json_data["message"], "Not enough credits", "Wrong message"
                    )

    def test_post_challenge(self):
        with self.app_context():
            fixtures = create_fixtures()
            self.post_user_game(fixtures)
            data = {
                "type": "Test",
                "game_id": fixtures["game"].id,
                "date": "2019-01-01T00:00:00",
                "buy_in": 10,
                "console_id": fixtures["console"].id,
            }
            with self.test_client() as c:
                g.claims = {"uid": fixtures["user_login"].firebase_id}
                prev_transaction = fixtures["transaction2"]
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
                self.assertEqual(challenge_created["status"], "OPEN", "Wrong type")
                self.assertEqual(challenge_created["due_date"], "2019-01-01T00:05:00")
                transaction = TransactionModel.find_by_user_id(
                    UserModel.find_by_firebase_id("myLbdKL8dFhipvanv4AnIUaJpqd2").id
                )
                self.assertEqual(
                    transaction.credit_total,
                    int(prev_transaction.credit_total)
                    - int(challenge_created["buy_in"]),
                )

    def test_post_challenge_without_user_game(self):
        with self.app_context():
            fixtures = create_fixtures()
            data = {
                "type": "Test",
                "game_id": fixtures["game"].id,
                "date": "2019-01-01T00:00:00",
                "buy_in": 10,
                "console_id": fixtures["console"].id,
            }
            with self.test_client() as c:
                g.claims = {"uid": fixtures["user_login"].firebase_id}
                rv = c.post(
                    "/challenge", data=json.dumps(data), content_type="application/json"
                )
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 400, "Wrong status code")
                self.assertEqual(
                    json_data["message"], "User game console relation not matching"
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
                    prev_transaction = fixtures["transaction2"]
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 200, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge accepted", json_data["message"], "Wrong message"
                    )
                    transaction = TransactionModel.find_by_user_id(
                        UserModel.find_by_firebase_id("myLbdKL8dFhipvanv4AnIUaJpqd2").id
                    )
                    challenge = ChallengeModel.find_by_id(challenge_user.wager_id)
                    self.assertEqual(
                        transaction.credit_total,
                        int(prev_transaction.credit_total) - int(challenge.buy_in),
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

    def test_challenge_accept_not_direct(self):
        with self.app_context():
            fixtures = create_fixtures()

            class TestTransaction:
                credit_total = 1000

            with patch(
                "resources.challenge_.TransactionModel.find_by_user_id",
                return_value=TestTransaction(),
            ):
                with self.test_client() as c:
                    g.claims = {"user_id": fixtures["user"].firebase_id}
                    challenge_user = fixtures["challenge_user_not_direct"]
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 200, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Challenge accepted",
                        json_data["message"],
                        "Wrong message",
                    )

    def test_challenge_accept_not_direct_return_value_none(self):
        with self.app_context():
            fixtures = create_fixtures()

            with patch(
                "resources.challenge_.TransactionModel.find_by_user_id",
                return_value=None,
            ):
                with self.test_client() as c:
                    g.claims = {"user_id": fixtures["user"].firebase_id}
                    challenge_user = fixtures["challenge_user_not_direct"]
                    rv = c.post(f"/challenge/{challenge_user.id}/accept")
                    self.assertEqual(rv.status_code, 403, "Wrong status")
                    json_data = rv.get_json()
                    self.assertEqual(
                        "Not enough credits",
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
                with self.subTest("Correct transition to COMPLETED"):
                    g.claims = {"uid": "dummy_2"}
                    current_user_id = UserModel.find_by_firebase_id("dummy_2").id
                    rival_user_id = UserModel.find_by_firebase_id(
                        "myLbdKL8dFhipvanv4AnIUaJpqd2"
                    ).id
                    challenge.status = STATUS_FINISHED
                    challenge_users.status_challenger = STATUS_FINISHED
                    challenge_users.status_challenged = STATUS_COMPLETED
                    data = {
                        "own_score": 0,
                        "opponent_score": 1,
                        "screenshot": "",
                    }
                    result_1v1: Results1v1Model = fixtures["result_1v1"]
                    result_1v1.challenge_id = 2
                    result_1v1.save_to_db()
                    prev_transaction = TransactionModel.find_by_user_id(rival_user_id)
                    rv = c.put(
                        f"/challenge/{challenge.id}/updateChallenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(
                        challenge_users.status_challenger, STATUS_COMPLETED
                    )
                    self.assertEqual(
                        challenge_users.status_challenged, STATUS_COMPLETED
                    )
                    self.assertEqual(challenge.status, STATUS_COMPLETED)
                    challenge_user_score = (
                        UserChallengeScoresModel.find_by_challenge_id_user_id(
                            challenge.id, current_user_id
                        )
                    )
                    self.assertEqual(challenge_user_score.own_score, data["own_score"])
                    self.assertEqual(
                        challenge_user_score.opponent_score, data["opponent_score"]
                    )
                    challenge_rival_score = (
                        UserChallengeScoresModel.find_by_challenge_id_user_id(
                            challenge.id, rival_user_id
                        )
                    )
                    self.assertEqual(
                        challenge_rival_score.own_score, data["opponent_score"]
                    )
                    self.assertEqual(
                        challenge_rival_score.opponent_score, data["own_score"]
                    )

                    result_1v1 = Results1v1Model.find_by_challenge_id(challenge.id)
                    self.assertEqual(result_1v1.winner_id, rival_user_id)
                    transaction = TransactionModel.find_by_user_id(result_1v1.winner_id)
                    self.assertEqual(
                        transaction.credit_total,
                        prev_transaction.credit_total + challenge.reward,
                    )
                    self.assertEqual(
                        rv.status_code, 200, "Challenge updated successfully"
                    )
                    result_1v1.challenge_id = 3
                    result_1v1.save_to_db()
                    challenge_user_score.challenge_id = 3
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
                    self.assertEqual(
                        challenge_users.status_challenger, STATUS_COMPLETED
                    )
                    self.assertEqual(challenge_users.status_challenged, STATUS_DISPUTED)
                with self.subTest("Transition to DISPUTED for scores mismatch"):
                    g.claims = {"uid": "dummy_2"}
                    current_user_id = UserModel.find_by_firebase_id("dummy_2").id
                    challenge.status = STATUS_FINISHED
                    challenge_users.status_challenger = STATUS_FINISHED
                    challenge_users.status_challenged = STATUS_COMPLETED
                    data = {
                        "own_score": 1,
                        "opponent_score": 0,
                        "screenshot": "",
                    }
                    rv = c.put(
                        f"/challenge/{challenge.id}/updateChallenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )
                    self.assertEqual(challenge_users.status_challenger, STATUS_DISPUTED)
                    self.assertEqual(challenge_users.status_challenged, STATUS_DISPUTED)
                    self.assertEqual(challenge.status, STATUS_DISPUTED)
                    self.assertEqual(
                        rv.status_code, 202, "Challenge updated successfully"
                    )

                with self.subTest("Transition to Complete on Tie"):
                    g.claims = {"uid": "dummy_2"}
                    current_user_id = UserModel.find_by_firebase_id("dummy_2").id
                    rival_user_id = UserModel.find_by_firebase_id(
                        "myLbdKL8dFhipvanv4AnIUaJpqd2"
                    ).id
                    challenge.status = STATUS_FINISHED
                    challenge_users.status_challenger = STATUS_FINISHED
                    challenge_users.status_challenged = STATUS_COMPLETED
                    challenge_user_score = (
                        UserChallengeScoresModel.find_by_challenge_id_user_id(
                            challenge.id, current_user_id
                        )
                    )
                    challenge_user_score.challenge_id = 2
                    challenge_rival_score = (
                        UserChallengeScoresModel.find_by_challenge_id_user_id(
                            challenge.id, rival_user_id
                        )
                    )
                    challenge_rival_score.own_score = 1
                    challenge_rival_score.opponent_score = 1
                    challenge_rival_score.save_to_db()
                    data = {
                        "own_score": 1,
                        "opponent_score": 1,
                        "screenshot": "",
                    }

                    prev_user_transaction = TransactionModel.find_by_user_id(
                        current_user_id
                    )
                    prev_rival_transaction = TransactionModel.find_by_user_id(
                        rival_user_id
                    )
                    rv = c.put(
                        f"/challenge/{challenge.id}/updateChallenge",
                        data=json.dumps(data),
                        content_type="application/json",
                    )

                    self.assertEqual(
                        rv.status_code, 202, "Challenge updated successfully"
                    )
                    self.assertEqual(
                        challenge_users.status_challenger, STATUS_COMPLETED
                    )
                    self.assertEqual(
                        challenge_users.status_challenged, STATUS_COMPLETED
                    )
                    self.assertEqual(challenge.status, STATUS_COMPLETED)
                    user_transaction = TransactionModel.find_by_user_id(current_user_id)
                    self.assertEqual(
                        user_transaction.credit_total,
                        prev_user_transaction.credit_total + challenge.buy_in,
                    )
                    rival_transaction = TransactionModel.find_by_user_id(rival_user_id)
                    self.assertEqual(
                        rival_transaction.credit_total,
                        prev_rival_transaction.credit_total + challenge.buy_in,
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
