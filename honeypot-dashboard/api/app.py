"""Flask app factory: dashboard page + JSON API."""

import os

from dotenv import load_dotenv
from flask import Flask, render_template

from api.auth import requires_auth
from api.middleware import register_middleware
from api.routes.analysis import bp as analysis_bp
from api.routes.attacks import bp as attacks_bp
from api.routes.export import bp as export_bp
from api.routes.stats import bp as stats_bp

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static",
    )
    app.secret_key = os.getenv("SECRET_KEY", "dev")
    register_middleware(app)
    app.register_blueprint(attacks_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(export_bp)

    @app.route("/")
    @requires_auth
    def index():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8080)
