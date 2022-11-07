"""Defines the authorization functionality"""
import json
from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)

from flask_login import (
    login_user,
    logout_user,
)

# Third-party libraries
import requests
from .user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_google_provider_cfg():
    return requests.get(
        current_app.config["GOOGLE_AUTH_DISCOVERY_URL"], timeout=100
    ).json()


@bp.route("/login/callback")
def callback():
    client = current_app.config["client"]
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    request.url = request.url.replace("http://", "https://", 1)
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
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        family_name = None
        gender = None
        locale = None
        if "family_name" in userinfo_response.json():
            family_name = userinfo_response.json()["family_name"]
        if "gender" in userinfo_response.json():
            gender = userinfo_response.json()["gender"]
        if "locale" in userinfo_response.json():
            locale = userinfo_response.json()["locale"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id,
        name=users_name,
        email=users_email,
        profile_pic=picture,
        family_name=family_name,
        gender=gender,
        locale=locale,
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(
            unique_id,
            users_name,
            users_email,
            picture,
            family_name=family_name,
            gender=gender,
            locale=locale,
        )

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Login logic"""
    # OAuth 2 client setup

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
def logout():
    """Logs the user out"""
    logout_user()
    return redirect(url_for("index"))
