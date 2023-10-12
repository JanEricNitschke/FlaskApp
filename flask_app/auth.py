"""Defines the authorization functionality."""
import json

# Third-party libraries
from typing import Any, Union

import requests
from flask import (
    Blueprint,
    abort,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    login_user,
    logout_user,
)
from werkzeug.wrappers.response import Response

from .user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_google_provider_cfg() -> Any:
    """Get google provider config."""
    return requests.get(
        current_app.config["GOOGLE_AUTH_DISCOVERY_URL"], timeout=100
    ).json()


@bp.route("/login/callback")
def callback() -> Response:
    """Login callback for google oauth to call.

    Returns:
        Response: Redirection response to the registration page.
    """
    client = current_app.config["client"]
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    request.url = request.url.replace(
        "http://", "https://", 1
    )  # pyright: ignore [reportGeneralTypeIssues]
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for("auth.callback", _external=True, _scheme="https"),
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            current_app.config["GOOGLE_AUTH_CLIENT_ID"],
            current_app.config["GOOGLE_AUTH_CLIENT_SECRET"],
        ),
        timeout=100,
    )
    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body, timeout=100)
    userinfo_json = userinfo_response.json()
    if userinfo_json.get("email_verified"):
        unique_id = userinfo_json.get("sub")
    else:
        abort(400, "User email not available or not verified by Google.")
    if user := User.get(unique_id):
        # Begin user session by logging the user in
        login_user(user)
        # Send user back to homepage
        return redirect(url_for("index"))

    resp = make_response(redirect(url_for("auth.registration")))
    resp.set_cookie(key="user_info", value=json.dumps(userinfo_json), max_age=60 * 60)
    return resp


@bp.route("/registration", methods=("GET", "POST"))
def registration() -> Union[Response, str]:
    """Registration logic.

    Returns:
        Union[Response, str]: Registration template if the request method is GET,
            otherwise redirects to the index page after login.
    """
    if request.method != "POST":
        return render_template("auth/registration.html")
    # Find out what URL to hit for Google login
    user_info = request.cookies.get("user_info")
    if user_info is None:
        abort(408, "Could not get user information for registration")
    else:
        try:
            userinfo_json = json.loads(user_info)
        except TypeError:
            abort(408, "Could not get user information for registration")
    if userinfo_json.get("email_verified"):
        unique_id = userinfo_json.get("sub")
        users_email = userinfo_json.get("email")
        picture = userinfo_json.get("picture")
        users_name = userinfo_json.get("given_name")
        family_name = userinfo_json.get("family_name")
        gender = userinfo_json.get("gender")
        locale = userinfo_json.get("locale")
    else:
        abort(400, "User email not available or not verified by Google.")
    user = User(
        userid=unique_id,
        name=users_name,
        email=users_email,
        profile_pic=picture,
        family_name=family_name,
        gender=gender,
        locale=locale,
    )
    if not User.get(unique_id):
        User.create(
            userid=unique_id,
            name=users_name,
            email=users_email,
            profile_pic=picture,
            family_name=family_name,
            gender=gender,
            locale=locale,
        )
    login_user(user)
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("user_info")
    return resp


@bp.route("/cancel")
def cancel() -> str:
    """Registration canceled."""
    return render_template("auth/cancel.html")


@bp.route("/login", methods=("GET", "POST"))
def login() -> Union[Response, str]:
    """Login logic."""
    if request.method == "POST":
        # Find out what URL to hit for Google login
        client = current_app.config["client"]
        google_provider_cfg = get_google_provider_cfg()
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]

        # Use library to construct the request for Google login and provide
        # scopes that let you retrieve user's profile from Google
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=url_for("auth.callback", _external=True, _scheme="https"),
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout() -> Response:
    """Logs the user out."""
    logout_user()
    return redirect(url_for("index"))
