"""Tests legal module."""

from flask.testing import FlaskClient


def test_impressum(client: FlaskClient):
    """Tests impressum."""
    assert client.get("/legal/impressum").status_code == 200


def test_privacy(client: FlaskClient):
    """Tests privacy."""
    assert client.get("/legal/privacy").status_code == 200


def test_tos(client: FlaskClient):
    """Tests tos."""
    assert client.get("/legal/termsofservice").status_code == 200
