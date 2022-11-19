"""Tests auth module"""

import json
from unittest.mock import MagicMock, patch
from flask_login import (
    login_user,
    current_user,
)
from FlaskApp.user import User
from FlaskApp.auth import get_google_provider_cfg

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


@patch("FlaskApp.auth.requests.get")
def test_get_google_provider_cfg(get_mock, app):
    """Tests get google provider cfg"""
    with app.app_context():
        get_google_provider_cfg()
        get_mock.assert_called_with(
            app.config["GOOGLE_AUTH_DISCOVERY_URL"], timeout=100
        )


@patch("FlaskApp.auth.get_google_provider_cfg")
@patch("FlaskApp.auth.login_user")
@patch("FlaskApp.user.User.get")
@patch("FlaskApp.auth.requests.post")
@patch("FlaskApp.auth.requests.get")
def test_callback(
    get_mock,
    post_mock,
    user_get_mock,
    login_mock,
    mock_google_prov,
    app,
    client,
):
    """Tests callback"""
    webappclient = app.config["client"]
    mock_google_prov.return_value = {"token_endpoint": "", "userinfo_endpoint": ""}
    webappclient.prepare_token_request = MagicMock(return_value=("A", "B", "C"))
    webappclient.parse_request_body_response = MagicMock(return_value=None)
    webappclient.add_token = MagicMock(return_value=("D", "E", "F"))
    unauthorized_response = {}
    authorized_response_small = {
        "email_verified": True,
        "sub": "2",
        "email": "test@test.com",
        "picture": "test.png",
        "given_name": "Test",
    }
    authorized_response_big = {
        "email_verified": True,
        "sub": "1",
        "email": "test@test.com",
        "picture": "test.png",
        "given_name": "Test",
        "family_name": "Test",
        "gender": "male",
        "locale": "en",
    }
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        unauthorized_response,
        authorized_response_small,
        authorized_response_big,
    ]
    get_mock.return_value = mock_response

    mock_post_response = MagicMock()
    mock_post_response.json.return_value = {"empty": True}
    post_mock.return_value = mock_post_response

    def user_get_side_effects(unique_id):
        return unique_id == "1"

    user_get_mock.side_effect = user_get_side_effects

    response = client.get("auth/login/callback", query_string={"code": ""})
    assert webappclient.prepare_token_request.call_count == 1
    assert webappclient.parse_request_body_response.call_count == 1
    assert webappclient.prepare_token_request.call_count == 1
    assert mock_google_prov.call_count == 1
    assert post_mock.call_count == 1
    assert not user_get_mock.called
    assert not login_mock.called
    assert response.status_code == 400

    response = client.get("auth/login/callback", query_string={"code": ""})
    assert webappclient.prepare_token_request.call_count == 2
    assert webappclient.parse_request_body_response.call_count == 2
    assert webappclient.prepare_token_request.call_count == 2
    assert mock_google_prov.call_count == 2
    assert post_mock.call_count == 2
    assert user_get_mock.called
    assert not login_mock.called
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/registration"

    response = client.get("auth/login/callback", query_string={"code": ""})
    assert webappclient.prepare_token_request.call_count == 3
    assert webappclient.parse_request_body_response.call_count == 3
    assert webappclient.prepare_token_request.call_count == 3
    assert mock_google_prov.call_count == 3
    assert post_mock.call_count == 3
    assert user_get_mock.call_count == 2
    assert login_mock.call_count == 1
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_cancel(client):
    """Tests cancel"""
    assert client.get("/auth/cancel").status_code == 200


@patch("FlaskApp.auth.login_user")
def test_registration(login_mock, client):
    """Tests registration"""
    assert client.get("/auth/registration").status_code == 200
    response = client.post("/auth/registration")
    assert response.status_code == 408
    unverified_false = {
        "email_verified": False,
        "sub": "2",
        "email": "test@test.com",
        "picture": "test.png",
        "given_name": "Test",
    }
    unverified_missing = {
        "sub": "2",
        "email": "test@test.com",
        "picture": "test.png",
        "given_name": "Test",
    }
    client.set_cookie("localhost", "user_info", json.dumps(unverified_false))
    response = client.post("/auth/registration")
    assert response.status_code == 400
    client.set_cookie("localhost", "user_info", json.dumps(unverified_missing))
    response = client.post("/auth/registration")
    assert response.status_code == 400
    assert not login_mock.called
    verified = {
        "email_verified": True,
        "sub": "1",
        "email": "test@test.com",
        "picture": "test.png",
        "given_name": "Test",
        "family_name": "Test",
        "gender": "male",
        "locale": "en",
    }
    client.set_cookie("localhost", "user_info", json.dumps(verified))
    response = client.post("/auth/registration")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert login_mock.called
    assert "Set-Cookie" in response.headers
    assert "user_info=;" in response.headers["Set-Cookie"]
    assert "Expires=Thu, 01 Jan 1970 00:00:00 GMT" in response.headers["Set-Cookie"]
    assert "Max-Age=0" in response.headers["Set-Cookie"]
