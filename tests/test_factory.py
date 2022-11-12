"""Test factory"""

import os
from FlaskApp import create_app


def test_config():
    """Test that testing config loading works"""
    assert not create_app(
        {
            "DATABASE": "test_flaskapp_userdata",
            "AWS_ACCESS_KEY_ID": os.environ["AWS_TESTDB_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_TESTDB_SECRET_ACCESS_KEY"],
            "AWS_DEFAULT_REGION": "eu-central-1",
            "GOOGLE_AUTH_CLIENT_ID": "ABCDEFG",
            "STRIPE_SECRET": "HIJKLMN",
        }
    ).testing
    assert create_app(
        {
            "TESTING": True,
            "DATABASE": "test_flaskapp_userdata",
            "AWS_ACCESS_KEY_ID": os.environ["AWS_TESTDB_ACCESS_KEY_ID"],
            "AWS_SECRET_ACCESS_KEY": os.environ["AWS_TESTDB_SECRET_ACCESS_KEY"],
            "AWS_DEFAULT_REGION": "eu-central-1",
            "GOOGLE_AUTH_CLIENT_ID": "ABCDEFG",
            "STRIPE_SECRET": "HIJKLMN",
        }
    ).testing
