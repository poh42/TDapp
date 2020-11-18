import json

from models.game import GameModel
from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from unittest.mock import patch


class TestGameEndpoints(BaseAPITestCase):
    def test_get_games(self):
        with self.app_context():
            create_fixtures()
            with self.test_client() as c:
                with self.subTest(is_admin=True):
                    with patch("resources.game.is_admin", return_value=True):
                        rv = c.get("/games")
                        json_data = rv.get_json()
                        has_non_active_games = False
                        for game in json_data["games"]:
                            if not game["is_active"]:
                                has_non_active_games = True
                                break
                        self.assertTrue(
                            has_non_active_games, "It has no non-active games"
                        )

                with self.subTest(is_admin=False):
                    with patch("resources.game.is_admin", return_value=False):
                        rv = c.get("/games")
                        json_data = rv.get_json()
                        every_game_is_active = all(
                            [game["is_active"] for game in json_data["games"]]
                        )
                        self.assertTrue(
                            every_game_is_active,
                            "There should not be any non active games in the response",
                        )

    def test_add_game(self):
        with self.app_context():
            fixtures = create_fixtures()
            console = fixtures["console"]
            post_data = {
                "image": "image_url_here",
                "name": "Test",
                "consoles": [{"id": console.id}],
            }
            with self.test_client() as c:
                rv = c.post(
                    "/games",
                    data=json.dumps(post_data),
                    content_type="application/json",
                )
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 201, "Wrong status code")
                self.assertEqual(json_data["message"], "Game saved", "Wrong message")
                game_data = json_data["game"]
                self.assertTrue(game_data["is_active"], "Should be true")
                self.assertEqual(game_data["name"], "Test", "Wrong name")
                self.assertEqual(game_data["image"], "image_url_here", "Wrong url")
                self.assertIn(
                    "consoles", game_data, "Consoles not present in game data"
                )
                self.assertEqual(len(game_data["consoles"]), 1, "Wrong len")
                console_data = game_data["consoles"][0]
                self.assertEqual(console.name, console_data["name"], "Wrong name")

    def test_delete_game(self):
        with self.app_context():
            fixtures = create_fixtures()
            game = fixtures["game"]
            with self.test_client() as c:
                rv = c.delete(f"/games/{game.id}")
                json_data = rv.get_json()
                self.assertEqual(rv.status_code, 200, "Wrong status code")
                self.assertIsNone(GameModel.find_by_id(game.id))
                self.assertEqual(json_data["message"], "Game deleted")
