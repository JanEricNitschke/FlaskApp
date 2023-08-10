"""Tests the database part of the app."""


import pytest
from flask import Flask
from flask.testing import FlaskCliRunner

from flask_app.db import get_db


def test_get_close_db(app: Flask):
    """Tests getting and closing the database."""
    with app.app_context():
        database = get_db()
        assert database is get_db()


def test_init_db_command(runner: FlaskCliRunner, monkeypatch: pytest.MonkeyPatch):
    """Tests the db init command."""

    class Recorder:
        """Records stuff."""

        called = False

    def fake_init_db() -> None:
        Recorder.called = True

    monkeypatch.setattr("flask_app.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
