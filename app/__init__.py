from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
from config import AppConfig
from app.models import User, cache
from flask_session import Session
from app.utils import db_utils

# Create global mail instance
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)

    # Email configuration (optional - using Mailgun API by default)
    app.config['MAIL_SERVER'] = AppConfig.CONFIG.get('email', 'smtp_server', fallback='smtp.gmail.com')
    app.config['MAIL_PORT'] = AppConfig.CONFIG.getint('email', 'smtp_port', fallback=587)
    app.config['MAIL_USE_TLS'] = AppConfig.CONFIG.getboolean('email', 'smtp_use_tls', fallback=True)
    app.config['MAIL_USE_SSL'] = AppConfig.CONFIG.getboolean('email', 'smtp_use_ssl', fallback=False)
    app.config['MAIL_USERNAME'] = AppConfig.CONFIG.get('email', 'smtp_username', fallback='')
    app.config['MAIL_PASSWORD'] = AppConfig.CONFIG.get('email', 'smtp_password', fallback='')
    app.config['MAIL_DEFAULT_SENDER'] = (
        AppConfig.CONFIG.get('email', 'sender_name', fallback='Turnushjelper'),
        AppConfig.CONFIG.get('email', 'sender_email', fallback='noreply@mail.turnushjelper.no')
    )

    # Initialize Flask-Mail (not actively used - using Mailgun API instead)
    mail.init_app(app)

    # Initialize cache (no db initialization needed - we use SQLAlchemy Core)
    cache.init_app(app)

    # Create database tables if they don't exist
    db_utils.create_tables()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'


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

