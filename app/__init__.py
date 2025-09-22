from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from config import conf
from app.models import User, cache
from flask_session import Session
from app.utils import db_utils


def create_app():
    app = Flask(__name__)
    app.config.from_object(conf)
    
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

