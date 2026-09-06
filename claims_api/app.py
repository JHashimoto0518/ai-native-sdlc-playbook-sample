"""アプリケーションファクトリ。"""

from __future__ import annotations

from flask import Flask

from claims_api.routes import status


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(status.bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
