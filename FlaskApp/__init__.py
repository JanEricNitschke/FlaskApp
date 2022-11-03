"""The Application Factory"""
import os

from flask import Flask, flash

from flask_login import (
    LoginManager,
)
import stripe

from oauthlib.oauth2 import WebApplicationClient


def create_app(test_config=None):
    """create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", DATABASE="flaskapp_userdata")

    if test_config is None:
        # load the instance config if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    client = WebApplicationClient(app.config["GOOGLE_AUTH_CLIENT_ID"])
    app.config["client"] = client

    stripe.api_key = app.config["STRIPE_SECRET"]

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hellow, World"

    from .user import User

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)
    login_manager.login_view = "auth.login"

    from . import homepage

    app.register_blueprint(homepage.bp)
    app.add_url_rule("/", endpoint="index")

    from . import payment

    app.register_blueprint(payment.bp)

    return app
