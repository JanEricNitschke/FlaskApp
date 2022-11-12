"""Sets up testing enviroment"""

import os
import pytest
from FlaskApp import create_app
from FlaskApp.db import get_db, init_db


@pytest.fixture(scope="session", autouse=True)
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
            "GOOGLE_AUTH_DISCOVERY_URL": (
                "https://accounts.google.com/.well-known/openid-configuration"
            ),
            "PRODUCT_ID": "",
            "STRIPE_WH_SECRET": "",
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
