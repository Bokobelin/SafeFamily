"""Run the Flask application."""

from src.safe_family.app import create_app
from src.safe_family.rules.scheduler import load_schedules

flask_app = create_app()

with flask_app.app_context():
    load_schedules()


if __name__ == "__main__":
    flask_app.run(debug=True)
