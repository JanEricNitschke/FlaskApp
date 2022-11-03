from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
    jsonify,
)

from flask_login import login_user, logout_user, login_required, current_user
import stripe


# Python standard libraries
import json

# Third-party libraries
import requests
from .user import User

bp = Blueprint("payment", __name__, url_prefix="/payment")


@bp.route("/checkout", methods=(["POST"]))
@login_required
def checkout():
    """checkout"""
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell,
                    "price": "price_1M00WXArSIx0pb8xSYDLF394",
                    "quantity": 1,
                },
            ],
            mode="payment",
            submit_type="donate",
            success_url=request.host_url + url_for("payment.success"),
            cancel_url=request.host_url + url_for("payment.cancel"),
            client_reference_id=current_user.id,
        )
    except Exception as e:
        return str(request.host + url_for("payment.success"))

    return redirect(checkout_session.url, code=303)


@bp.route("/success", methods=(["GET"]))
@login_required
def success():
    """checkout"""
    return render_template("payment/success.html")


@bp.route("/cancel", methods=(["GET"]))
@login_required
def cancel():
    """checkout"""
    return render_template("payment/cancel.html")


@bp.route("/webhook", methods=(["POST"]))
def webhook():
    """Webhook to receive payment confirmation and update db"""
    event = None
    payload = request.data
    sig_header = request.headers["STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config["STRIPE_WH_SECRET"]
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event["type"] == "checkout.session.completed":
        print(event, flush=True)
        session = event["data"]["object"]
        User.updateDonation(session["client_reference_id"], session["amount_total"])
    return jsonify(success=True)
