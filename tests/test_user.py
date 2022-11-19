"""Tests user module"""

from FlaskApp.user import User
from FlaskApp.db import get_db


def test_get(app):
    """Test User.get()"""
    with app.app_context():
        assert User.get("2") is None
        user = User.get("1")
        assert isinstance(user, User)
        assert user.name == "Test"


def test_create(app):
    """Tests User.create()"""
    with app.app_context():
        assert (
            User.create(
                "1",
                "Test",
                "test@test.com",
                "test.png",
            )
            is None
        )
        response = User.create(
            "2",
            "Test2",
            "test@test.de",
            "test2.png",
        )
        assert response is not None
        assert isinstance(response, User)
        table = get_db()
        assert "Item" in table.get_item(Key={"userid": "2"})
        table.delete_item(Key={"userid": "2"})


def test_update_donation(app):
    """Tests User.update_donation()"""
    with app.app_context():
        success, user = User.update_donation("1", 1000)
        assert success is True
        assert isinstance(user, dict)
        assert user["paid"] is True
        assert user["amount"] == 1000
        success, user = User.update_donation("2", 2000)
        assert success is False
        assert isinstance(user, str)
