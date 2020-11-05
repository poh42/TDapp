from tests.base import BaseAPITestCase
from tests.utils import create_fixtures
from models.game import GameModel


class TestIntegrationGame(BaseAPITestCase):
    def test_active_game(self):
        with self.app_context():
            create_fixtures()
            games = GameModel.get_active_games()
            for g in games:
                with self.subTest(game=g.name):
                    self.assertTrue(
                        hasattr(g, "consoles"), "Attribute consoles is not present"
                    )
                    self.assertTrue(
                        hasattr(g.consoles, "__iter__"), "Object is not iterable"
                    )
            self.assertEqual(len(games), 5, "Wrong game count")

            def check_has_game_title(title):
                for g in games:
                    if g.name == title:
                        return True
                return False

            self.assertTrue(check_has_game_title("FIFA"), "Wrong title")

    def test_get_all_games(self):
        with self.app_context():
            create_fixtures()
            games = GameModel.get_all_games()
            has_non_active_games = False
            for game in games:
                if not game.is_active:
                    has_non_active_games = True
                with self.subTest(game=game.name):
                    self.assertTrue(
                        hasattr(game, "consoles"), "Attribute consoles is not present"
                    )
                    self.assertTrue(
                        hasattr(game.consoles, "__iter__"), "Object is not iterable"
                    )
            self.assertTrue(has_non_active_games)
