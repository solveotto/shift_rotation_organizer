from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from flask_mail import Mail
from config import conf
from app.models import User, cache
from flask_session import Session
from app.utils import db_utils

# Create global mail instance
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(conf)

    # Email configuration
    app.config['MAIL_SERVER'] = conf.CONFIG.get('email', 'smtp_server')
    app.config['MAIL_PORT'] = conf.CONFIG.getint('email', 'smtp_port')
    app.config['MAIL_USE_TLS'] = conf.CONFIG.getboolean('email', 'smtp_use_tls')
    app.config['MAIL_USERNAME'] = conf.CONFIG.get('email', 'smtp_username')
    app.config['MAIL_PASSWORD'] = conf.CONFIG.get('email', 'smtp_password')
    app.config['MAIL_DEFAULT_SENDER'] = (
        conf.CONFIG.get('email', 'sender_name'),
        conf.CONFIG.get('email', 'sender_email')
    )

    # Initialize Flask-Mail
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
    app.config['SESSION_FILE_DIR'] = conf.sessions_dir 
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    Session(app)


    from app.routes.main import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)



    return app

