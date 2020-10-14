import unittest
from unittest.mock import patch
import importlib
import app
from flask_migrate import upgrade, downgrade


class BaseAPITestCase(unittest.TestCase):
    def setUp(self):
        def kill_patches():  # Create a cleanup callback that undoes our patches
            patch.stopall()  # Stops all patches started with start()
            importlib.reload(
                app
            )  # Reload our UUT module which restores the original decorator

        def remove_database():
            with self.app_context():
                try:
                    downgrade()
                except:
                    pass
                upgrade()

        self.test_client = app.app.test_client
        self.app_context = app.app.app_context
        # We want to make sure this is run so we do this in addCleanup instead of tearDown
        self.addCleanup(kill_patches)
        self.addCleanup(remove_database)
        patch("decorators.check_token", lambda x: x).start()
        importlib.reload(
            app
        )  # Reloads the uut.py module which applies our patched decorator
        with self.app_context():
            print("upgrading")
            upgrade()
