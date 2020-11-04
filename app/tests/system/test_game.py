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
