from __future__ import annotations

from pathlib import Path

from cachelib.file import FileSystemCache
from flask import Flask, g, jsonify
from flask_session import Session

from .config import Config
from .csrf import install_csrf_protection
from .db import initialize_database, seed_missing_staff_operational_profiles
from .logging_config import configure_application_logging
from .routes import register_blueprints


def create_app() -> Flask:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "frontend" / "templates"),
        static_folder=str(BASE_DIR / "frontend" / "static"),
    )

    app.config.from_object(Config())
    app.secret_key = app.config.get("SECRET_KEY")
    configure_application_logging(app.config)

    if app.config.get("SESSION_TYPE") != "cachelib":
        raise RuntimeError(
            "Only the documented CacheLib session backend is supported."
        )
    session_directory = Path(app.config["SESSION_CACHE_DIR"])
    session_directory.mkdir(parents=True, exist_ok=True)
    session_directory.chmod(0o700)
    app.config["SESSION_CACHELIB"] = FileSystemCache(
        cache_dir=str(session_directory),
        threshold=app.config["SESSION_CACHE_THRESHOLD"],
        mode=0o700,
    )
    Session(app)
    install_csrf_protection(app)

    register_blueprints(app)

    @app.after_request
    def identify_replaced_student_session(response):
        if getattr(g, "student_session_replaced", False):
            response.headers["X-CTRL4-Session-Replaced"] = "1"
        return response

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    if app.config.get("DATABASE_INITIALIZE_ON_START", True):
        with app.app_context():
            initialize_database()
            from .services.settings_service import settings_service
            from .services.program_service import program_service

            seed_report = settings_service.seed_approved_mk_ii_settings()
            app.logger.info(
                "Approved settings seed completed (seeded=%s preserved=%s).",
                seed_report["seeded"],
                seed_report["preserved"],
            )
            program_seed_report = program_service.seed_program_catalog()
            app.logger.info(
                "Program catalog seed completed (seeded=%s preserved=%s).",
                program_seed_report["seeded"],
                program_seed_report["preserved"],
            )
            seeded_staff_profiles = seed_missing_staff_operational_profiles()
            app.logger.info(
                "Counselor operational profile seed completed (updated_staff=%s).",
                seeded_staff_profiles,
            )

    return app
