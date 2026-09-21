"""A deliberately small Flask application for CI security demonstrations."""

from flask import Flask, jsonify


def create_app() -> Flask:
    """Create the application so tests and production use the same entry point."""
    app = Flask(__name__)

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        return {"status": "ok"}, 200

    @app.get("/")
    def index() -> tuple[object, int]:
        return jsonify(service="devsecops-demo", message="secure CI starts here"), 200

    return app


app = create_app()

