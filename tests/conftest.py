"""Sets up testing enviroment"""

import os
import pytest
from FlaskApp import create_app
from FlaskApp.db import get_db, init_db


@pytest.fixture
def app():
    """Fixture for initializing the app"""
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": "test_flaskapp_userdata",
            "AWS_ACCESS_KEY_ID": os.environ["AWS_TESTDB_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_TESTDB_SECRET_ACCESS_KEY"],
            "AWS_DEFAULT_REGION": "eu-central-1",
            "GOOGLE_AUTH_CLIENT_ID": "ABCDEFG",
            "STRIPE_SECRET": "HIJKLMN",
        }
    )

    with app.app_context():
        init_db()
        table = get_db()
        table.put_item(
            Item={
                "userid": "1",
                "email": "test@test.com",
                "name": "Test",
                "profile_pic": "test.png",
                "paid": False,
                "expires": None,
                "amount": 0,
                "family_name": "Test",
                "gender": None,
                "locale": "en",
            },
            ConditionExpression="attribute_not_exists(userid)",
        )

    yield app
    # remove the above entries from the db
    table.delete_item(Key={"userid": "1"})


@pytest.fixture
def client(app):
    """Fixture to be able to issue client commands"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture to be able to issue cli runner commands"""
    return app.test_cli_runner()


# will have to check how to adapt this to my oauth2 setup
class AuthActions:
    """Define login and logout function to be able to easily call them"""

    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    """Fixture for calling the login, logout functions"""
    return AuthActions(client)
