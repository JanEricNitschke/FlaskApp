"""Test factory"""

import os
from unittest.mock import patch
from FlaskApp import create_app, load_user


@patch("FlaskApp.user.User.get")
def test_load_user(get_mock):
    """Tests load user"""
    get_mock.return_value = None
    user_id = "1"
    load_user(user_id)
    get_mock.assert_called_with(user_id)
    user_id = "ABCYW"
    load_user(user_id)
    get_mock.assert_called_with(user_id)


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
