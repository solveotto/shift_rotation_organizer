from flask import Flask
from flask_session import Session
from config import AppConfig
from app.extensions import cache, mail, login_manager
from app.database import create_tables
from app.models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)

    # Email configuration (optional - using Mailgun API by default)
    app.config['MAIL_SERVER'] = AppConfig.SMTP_SERVER
    app.config['MAIL_PORT'] = AppConfig.SMTP_PORT
    app.config['MAIL_USE_TLS'] = AppConfig.SMTP_USE_TLS
    app.config['MAIL_USE_SSL'] = AppConfig.SMTP_USE_SSL
    app.config['MAIL_USERNAME'] = AppConfig.SMTP_USERNAME
    app.config['MAIL_PASSWORD'] = AppConfig.SMTP_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = (AppConfig.SENDER_NAME, AppConfig.SENDER_EMAIL)

    # Initialize Flask extensions
    mail.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Create database tables if they don't exist
    create_tables()

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_id = int(user_id)
            return User.get_by_id(user_id)
        except (ValueError, TypeError):
            pass
        return None

    # Configure server-side session storage
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = AppConfig.sessions_dir
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    Session(app)

    from app.routes.main import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    return app
