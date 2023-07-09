"Defines the homepage functionality."

from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("homepage", __name__)


@bp.route("/")
@login_required
def index():
    """Index and homepage."""
    return render_template("homepage/index.html")
