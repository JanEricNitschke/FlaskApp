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
from werkzeug.wrappers.response import Response

from .user import User

bp = Blueprint("payment", __name__, url_prefix="/payment")


@bp.route("/checkout", methods=["POST"])
@login_required
def checkout() -> Response:
    """Checkout."""
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234)
                # of the product you want to sell,
                "price": current_app.config["PRODUCT_ID"],
                "quantity": 1,
            },
        ],
        mode="payment",
        submit_type="donate",
        success_url=url_for("payment.success", _external=True, _scheme="https"),
        cancel_url=url_for("payment.cancel", _external=True, _scheme="https"),
        # Has to exist because we are requiring login
        client_reference_id=(
            current_user.get_id()  # pyright: ignore[reportGeneralTypeIssues]
        ),
    )

    return redirect(checkout_session.url, code=303)


@bp.route("/success", methods=["GET"])
@login_required
def success() -> str:
    """Checkout."""
    return render_template("payment/success.html")


@bp.route("/cancel", methods=["GET"])
@login_required
def cancel() -> str:
    """Checkout."""
    return render_template("payment/cancel.html")


@bp.route("/webhook", methods=["POST"])
def webhook() -> Response:
    """Webhook to receive payment confirmation and update db.

    Returns:
        Response: Updated user or success message.
    """
    event = None
    payload = request.data
    sig_header = request.headers["STRIPE_SIGNATURE"]
    event = stripe.Webhook.construct_event(
        payload, sig_header, current_app.config["STRIPE_WH_SECRET"]
    )

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        status, response = User.update_donation(
            session["client_reference_id"], session["amount_total"]
        )
        return Response(response, 200 if status else 500)
    print(f"Unhandled event type {event['type']}", flush=True)
    return jsonify(success=True)
