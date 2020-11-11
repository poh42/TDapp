from models.user_game import UserGameModel
from tests.base import BaseAPITestCase
from sqlalchemy import inspect

from tests.utils import create_fixtures


class TestIntegrationGame(BaseAPITestCase):
    def test_get_user_game_instance(self):
        with self.app_context():
            fixtures = create_fixtures()
            user_login = fixtures["user_login"]
            console = fixtures["console"]
            game = fixtures["game"]
            with self.subTest(state="transient"):
                instance = UserGameModel.get_user_game_instance(
                    user_login.id, game.id, console.id
                )
                instance.gamertag = "testtag"
                state = inspect(instance)
                self.assertTrue(state.transient, "Object should be transient")
                instance.save_to_db()
            with self.subTest(state="persistent"):
                instance = UserGameModel.get_user_game_instance(
                    user_login.id, game.id, console.id
                )
                state = inspect(instance)
                self.assertFalse(state.transient, "Object should be transient")
                self.assertTrue(state.persistent, "Object should be persistent")
