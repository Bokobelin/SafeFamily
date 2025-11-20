"""Run the Flask application."""

from flask import redirect

from src.safe_family.app import create_app
from src.safe_family.rules.scheduler import load_schedules

flask_app = create_app()

with flask_app.app_context():
    load_schedules()


@flask_app.route("/")
def index():
    """Redirect to the suspicious URLs view.

    This route redirects users to the main page for viewing suspicious URLs.
    """
    return redirect("/todo")


if __name__ == "__main__":
    flask_app.run(debug=True)
