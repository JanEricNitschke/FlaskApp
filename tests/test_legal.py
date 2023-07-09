"""Tests legal module."""


def test_impressum(client):
    """Tests impressum."""
    assert client.get("/legal/impressum").status_code == 200


def test_privacy(client):
    """Tests privacy."""
    assert client.get("/legal/privacy").status_code == 200


def test_tos(client):
    """Tests tos."""
    assert client.get("/legal/termsofservice").status_code == 200
