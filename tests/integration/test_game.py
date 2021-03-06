from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.game import GameModel


class TestIntegrationGame(BaseAPITestCase):
    def test_active_game(self):
        with self.app_context():
            create_fixtures()
            games = GameModel.get_active_games()
            self.assertEqual(len(games), 1, "Wrong game count")
            self.assertEqual(games[0].name, "FIFA", "Wrong title")
