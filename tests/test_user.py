"""Tests user module."""

import re
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
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
                userid="1",
                name="Test",
                email="test@test.com",
                profile_pic="test.png",
            )
            is None
        )
        response = User.create(
            userid="2",
            name="Test2",
            email="test@test.de",
            profile_pic="test2.png",
        )
        assert response is not None
        assert isinstance(response, User)
        assert (
            User.create(
                userid="2",
                name="Test2",
                email="test@test.de",
                profile_pic="test2.png",
            )
            is None
        )
        with patch("flask.g.db.put_item") as put_item_mock:
            put_item_mock.side_effect = [
                ClientError({}, "SomeOperation"),
                ClientError({"Error": {"Code": "SomeOtherCode"}}, "SomeOperation"),
                KeyError("SomeKeyError"),
            ]
            with pytest.raises(
                ClientError,
                match=re.escape(
                    "An error occurred (Unknown) when calling the SomeOperation "
                    "operation: Unknown"
                ),
            ):
                User.create(
                    userid="2",
                    name="Test2",
                    email="test@test.de",
                    profile_pic="test2.png",
                )
            with pytest.raises(
                ClientError,
                match=re.escape(
                    "An error occurred (SomeOtherCode) when calling the SomeOperation "
                    "operation: Unknown"
                ),
            ):
                User.create(
                    userid="2",
                    name="Test2",
                    email="test@test.de",
                    profile_pic="test2.png",
                )
            with pytest.raises(
                KeyError,
                match=re.escape("SomeKeyError"),
            ):
                User.create(
                    userid="2",
                    name="Test2",
                    email="test@test.de",
                    profile_pic="test2.png",
                )

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
        assert user == "User with id 2 does not exist in user database."
        assert isinstance(user, str)
        with patch("flask.g.db.update_item") as update_item_mock:
            update_item_mock.side_effect = [
                ClientError({}, "SomeOperation"),
                ClientError({"Error": {"Code": "SomeOtherCode"}}, "SomeOperation"),
                KeyError("SomeKeyError"),
            ]

            success, user = User.update_donation("2", 1000)
            assert success is False
            assert (
                user == "ClientError('An error occurred (Unknown) when"
                " calling the SomeOperation "
                "operation: Unknown')"
            )

            success, user = User.update_donation("2", 1000)
            assert success is False
            assert (
                user == "ClientError('An error occurred (SomeOtherCode) when"
                " calling the SomeOperation "
                "operation: Unknown')"
            )

            success, user = User.update_donation("2", 1000)
            assert success is False
            assert user == "KeyError('SomeKeyError')"
