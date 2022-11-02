"""Defines the authorization functionality"""
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


# Python standard libraries
import json

# Third-party libraries
import requests

from .db import get_db
from .user import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

# Flask-Login helper to retrieve a user from our db


# @bp.route("/register", methods=("GET", "POST"))
# def register():
#     """Registration logic"""
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         db = get_db()
#         error = None

#         if not username:
#             error = "Username is required"
#         elif not password:
#             error = "Password is required"

#         if error is None:
#             try:
#                 db.put_item(
#                     Item={
#                         "userid": username,
#                         "email": "email@test.com",
#                         "name": "testname",
#                         "profile_pic": "testpic",
#                         "paid": False,
#                         "expires": None,
#                     },
#                     ConditionExpression="attribute_not_exists(userid)",
#                 )
#             except ClientError as e:
#                 # Ignore the ConditionalCheckFailedException, bubble up
#                 # other exceptions.
#                 if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
#                     raise
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))

#         flash(error)

#     return render_template("auth/register.html")


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
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
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
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google
    user = User(id_=unique_id, name=users_name, email=users_email, profile_pic=picture)

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

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
            redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )
        return redirect(request_uri)

        # username = request.form["username"]
        # password = request.form["password"]
        # db = get_db()
        # error = None
        # response = db.get_item(Key={"userid": username})
        # if "Item" not in response:
        #     error = "Incorrect username."
        #     response["Item"] = {}

        # user = response["Item"]
        # if error is None:
        #     session.clear()
        #     session["user_id"] = user["userid"]
        #     return redirect(url_for("index"))

        # flash(error)

    return render_template("auth/login.html")


# @bp.before_app_request
# def load_logged_in_user():
#     """Loads a user that is already logged in"""
#     user_id = session.get("user_id")

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().get_item(Key={"userid": user_id})["Item"]


@bp.route("/logout")
def logout():
    """Logs the user out"""
    logout_user()
    return redirect(url_for("index"))


# def login_required(view):
#     """Wraps any function that requires a logged in user. If there is none it redirects to the login page"""

#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return redirect(url_for("auth.login"))

#         return view(**kwargs)

#     return wrapped_view
