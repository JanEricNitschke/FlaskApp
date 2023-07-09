"""Handles payments."""
import stripe
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from .user import User

bp = Blueprint("payment", __name__, url_prefix="/payment")


@bp.route("/checkout", methods=(["POST"]))
@login_required
def checkout():
    """Checkout."""
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell,
                "price": current_app.config["PRODUCT_ID"],
                "quantity": 1,
            },
        ],
        mode="payment",
        submit_type="donate",
        success_url=url_for("payment.success", _external=True, _scheme="https"),
        cancel_url=url_for("payment.cancel", _external=True, _scheme="https"),
        client_reference_id=current_user.id,
    )

    return redirect(checkout_session.url, code=303)


@bp.route("/success", methods=(["GET"]))
@login_required
def success():
    """Checkout."""
    return render_template("payment/success.html")


@bp.route("/cancel", methods=(["GET"]))
@login_required
def cancel():
    """Checkout."""
    return render_template("payment/cancel.html")


@bp.route("/webhook", methods=(["POST"]))
def webhook():
    """Webhook to receive payment confirmation and update db."""
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
        session = event["data"]["object"]
        status, response = User.update_donation(
            session["client_reference_id"], session["amount_total"]
        )
        if not status:
            return response, 500
        return response, 200

    print(f"Unhandled event type {event['type']}", flush=True)
    return jsonify(success=True)
