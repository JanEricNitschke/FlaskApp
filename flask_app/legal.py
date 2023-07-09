"Defines the legalize functionality."

from flask import Blueprint, render_template

bp = Blueprint("legal", __name__, url_prefix="/legal")


@bp.route("/impressum")
def impressum():
    """Impressum."""
    return render_template("legal/impressum.html")


@bp.route("/privacy")
def privacy():
    """Privacy policy."""
    return render_template("legal/privacy.html")


@bp.route("/termsofservice")
def tos():
    """Terms of Service."""
    return render_template("legal/tos.html")
