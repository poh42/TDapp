import unittest
from unittest.mock import patch
import importlib
import app
from resources import user, challenge_, game, console
from flask_migrate import upgrade, downgrade
from app import db


class BaseAPITestCase(unittest.TestCase):
    def reload_modules(self):
        modules_to_reload = [app, user, challenge_, game, console]
        for m in modules_to_reload:
            importlib.reload(m)

    def setUp(self):
        def kill_patches():  # Create a cleanup callback that undoes our patches
            patch.stopall()  # Stops all patches started with start()
            self.reload_modules()

        def remove_database():
            with self.app_context():

                connection = db.session.connection()
                # Based on https://stackoverflow.com/a/13823560/1767047
                sql = """
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                """
                connection.execute(sql, multi=True)
                db.session.commit()
                upgrade()

        self.test_client = app.app.test_client
        self.app_context = app.app.app_context
        # We want to make sure this is run so we do this in addCleanup instead of tearDown
        self.addCleanup(kill_patches)
        self.addCleanup(remove_database)
        patch("decorators.check_token", lambda x: x).start()
        patch("decorators.check_is_admin", lambda x: x).start()
        patch("decorators.check_is_admin_or_user_authorized", lambda x: x).start()
        self.reload_modules()
        with self.app_context():
            print("upgrading")
            upgrade()
