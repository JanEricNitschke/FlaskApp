"""Tests auth module"""

from unittest.mock import MagicMock
from flask_login import (
    login_user,
    current_user,
)
from FlaskApp.user import User

# Will probably have to rewrite from scratch for my oauth setup


def test_login(app, client):
    """Tests login"""
    assert client.get("/auth/login").status_code == 200

    webappclient = app.config["client"]
    webappclient.prepare_request_uri = MagicMock(return_value="/redirect_uri")
    response = client.post("/auth/login", data={})
    assert webappclient.prepare_request_uri.called
    assert response.headers["Location"] == "/redirect_uri"


def test_logout(client, app):
    """Tests logout"""
    user = User(
        id_="1",
        name="Test",
        email="test@test.com",
        profile_pic="test.png",
        family_name="Test",
        gender=None,
        locale="en",
    )
    with client and app.test_request_context():
        assert not isinstance(current_user, User)
        login_user(user)
        assert isinstance(current_user, User)
        response = client.get("/auth/logout")
        assert response.status_code == 302
        assert response.headers["Location"] == "/"
        assert not isinstance(current_user, User)
