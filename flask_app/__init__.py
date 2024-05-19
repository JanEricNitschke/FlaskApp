"""The Application Factory."""

import contextlib
import os
from collections.abc import Mapping
from typing import Any

import stripe
from flask import Flask
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient

from . import auth, db, homepage, legal, payment
from .user import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    """Defines user_loader."""
    return User.get(user_id)


def create_app(test_config: Mapping[str, Any] | None = None) -> Flask:
    """Create and configure the application.

    Returns:
        Flask: The flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",  # noqa: S106
        DATABASE="flaskapp_userdata",
    )
    os.environ["WSGI.URL_SCHEME"] = "https"
    if test_config is None:
        # load the instance config if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure instance folder exists
    with contextlib.suppress(OSError):
        os.makedirs(app.instance_path)

    client = WebApplicationClient(app.config["GOOGLE_AUTH_CLIENT_ID"])
    app.config["client"] = client

    stripe.api_key = app.config["STRIPE_SECRET"]

    login_manager.init_app(app)

    db.init_app(app)

    app.register_blueprint(auth.bp)
    login_manager.login_view = "auth.login"  # pyright: ignore [reportAttributeAccessIssue]

    app.register_blueprint(homepage.bp)
    app.add_url_rule("/", endpoint="index")

    app.register_blueprint(payment.bp)

    app.register_blueprint(legal.bp)

    return app


# This needs to be removed for AWS
# and the application = create_app() line
# has to come down to the base level.
if __name__ == "__main__":
    application = create_app()
