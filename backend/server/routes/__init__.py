from ..auth import auth_bp
from .appointment_routes import appointment_bp
from .account_routes import account_bp
from .chatbot_routes import chatbot_bp
from .dashboard_routes import dashboard_bp
from .settings_routes import settings_bp
from .conversation_routes import conversation_bp
from .health_routes import health_bp
from .frontend_routes import frontend_bp
from .notification_routes import notification_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(conversation_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(frontend_bp)
