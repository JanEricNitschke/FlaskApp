"""Tests the databse part of the app."""

from flask_app.db import get_db


def test_get_close_db(app):
    """Tests getting and closing the database."""
    with app.app_context():
        db = get_db()
        assert db is get_db()


def test_init_db_command(runner, monkeypatch):
    """Tests the db init command."""

    class Recorder:
        """Records stuff."""

        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("flask_app.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
