"""Tests user module."""


from flask import Flask

from flask_app.db import get_db
from flask_app.user import User


def test_get(app: Flask):
    """Test User.get()."""
    with app.app_context():
        assert User.get("2") is None
        user = User.get("1")
        assert isinstance(user, User)
        assert user.name == "Test"


def test_create(app: Flask):
    """Tests User.create()."""
    with app.app_context():
        assert (
            User.create(
                id_="1",
                name="Test",
                email="test@test.com",
                profile_pic="test.png",
            )
            is None
        )
        response = User.create(
            id_="2",
            name="Test2",
            email="test@test.de",
            profile_pic="test2.png",
        )
        assert response is not None
        assert isinstance(response, User)
        table = get_db()
        assert "Item" in table.get_item(Key={"userid": "2"})
        table.delete_item(Key={"userid": "2"})


def test_update_donation(app: Flask):
    """Tests User.update_donation()."""
    with app.app_context():
        success, user = User.update_donation("1", 1000)
        assert success is True
        assert isinstance(user, dict)
        assert user["paid"] is True
        assert user["amount"] == 1000
        success, user = User.update_donation("2", 2000)
        assert success is False
        assert isinstance(user, str)
