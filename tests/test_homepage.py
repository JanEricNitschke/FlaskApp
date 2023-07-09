"""Tests homepage module."""

from flask_login import (
    login_user,
)

from flask_app.user import User


def test_homepage(client, app):
    """Tests homepage."""
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
        response = client.get("/")
        assert response.status_code == 302
        assert response.headers["Location"] == "/auth/login?next=%2F"
        login_user(user)
        assert client.get("/").status_code == 200
