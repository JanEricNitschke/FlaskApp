"""Tests payment module."""
# have to check what i can actually even test there

from unittest.mock import MagicMock, patch

import pytest
import stripe
from flask_login import (
    login_user,
)

from flask_app.user import User


def test_checkout(client, app):
    """Tests logout."""
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
        assert client.get("/payment/checkout").status_code == 405
        response = client.post("/payment/checkout", data={})
        assert response.status_code == 302
        assert response.headers["Location"] == "/auth/login?next=%2Fpayment%2Fcheckout"
        login_user(user)

        class Object:
            pass

        my_session = Object()
        my_session.url = "/checkout_session"
        stripe.checkout.Session.create = MagicMock(return_value=my_session)
        response = client.post("/payment/checkout", data={})
        assert response.status_code == 303
        assert stripe.checkout.Session.create.called
        assert response.headers["Location"] == "/checkout_session"


def test_success(client, app):
    """Tests success."""
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
        response = client.get("/payment/success")
        assert response.status_code == 302
        assert response.headers["Location"] == "/auth/login?next=%2Fpayment%2Fsuccess"
        login_user(user)
        assert client.get("/payment/success").status_code == 200


def test_cancel(client, app):
    """Tests cancel."""
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
        response = client.get("/payment/cancel")
        assert response.status_code == 302
        assert response.headers["Location"] == "/auth/login?next=%2Fpayment%2Fcancel"
        login_user(user)
        assert client.get("/payment/cancel").status_code == 200


@patch("flask_app.user.User.update_donation")
@patch("stripe.Webhook.construct_event")
def test_webhook(stripe_mock, donation_mock, client):
    """Tests webhook."""
    headers = {"STRIPE_SIGNATURE": ""}
    payload = {}
    event_correct = {
        "type": "checkout.session.completed",
        "data": {"object": {"client_reference_id": "1", "amount_total": 1000}},
    }
    event_wrong = {"type": "wrong", "data": {"object": ""}}
    stripe_mock.side_effect = [
        ValueError("Invalid payload"),
        stripe.error.SignatureVerificationError(
            sig_header="Invalid signature", message=""
        ),
        event_wrong,
        event_correct,
        event_correct,
    ]

    donation_mock.side_effect = [(False, "an error"), (True, "a user")]

    with pytest.raises(ValueError):
        client.post("/payment/webhook", data=payload, headers=headers)
    with pytest.raises(stripe.error.SignatureVerificationError):
        client.post("/payment/webhook", data=payload, headers=headers)
    response = client.post("/payment/webhook", data=payload, headers=headers)
    assert response.status_code == 200
    response = client.post("/payment/webhook", data=payload, headers=headers)
    assert response.status_code == 500
    donation_mock.assert_called_with("1", 1000)
    response = client.post("/payment/webhook", data=payload, headers=headers)
    assert response.status_code == 200
    donation_mock.assert_called_with("1", 1000)
    assert stripe_mock.call_count == 5
    assert donation_mock.call_count == 2
