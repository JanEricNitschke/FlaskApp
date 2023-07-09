"""The Application Factory."""

import contextlib
import os
from typing import Optional

import stripe
from flask import Flask
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient

from . import auth, db, homepage, legal, payment
from .user import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    """Defines user_loader."""
    return User.get(user_id)


def create_app(test_config=None):
    """Create and configure the application."""
    application = Flask(__name__, instance_relative_config=True)
    application.config.from_mapping(SECRET_KEY="dev", DATABASE="flaskapp_userdata")
    os.environ["WSGI.URL_SCHEME"] = "https"
    if test_config is None:
        # load the instance config if it exists, when not testing
        application.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        application.config.from_mapping(test_config)

    # ensure instance folder exists
    with contextlib.suppress(OSError):
        os.makedirs(application.instance_path)


    client = WebApplicationClient(application.config["GOOGLE_AUTH_CLIENT_ID"])
    application.config["client"] = client

    stripe.api_key = application.config["STRIPE_SECRET"]

    login_manager.init_app(application)

    db.init_app(application)

    application.register_blueprint(auth.bp)
    login_manager.login_view = "auth.login"

    application.register_blueprint(homepage.bp)
    application.add_url_rule("/", endpoint="index")

    application.register_blueprint(payment.bp)

    application.register_blueprint(legal.bp)

    return application


if __name__ == "__main__":
    application = create_app()
