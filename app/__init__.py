from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from config import conf
from app.models import User
from flask_session import Session
from app.utils import db_utils



cache = Cache(config={'CACHE_TYPE': 'simple'})

def create_app():
    app = Flask(__name__)
    app.config.from_object(conf)
    cache.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'


    @login_manager.user_loader
    def load_user(user_id):
        # Convert user_id to int and get user data
        try:
            user_id = int(user_id)
            db_user_data = db_utils.get_user_by_id(user_id)
            if db_user_data:
                return User(db_user_data['username'], db_user_data['id'], db_user_data['is_auth'])
        except (ValueError, TypeError):
            pass
        return None

    
    # Configure server-side session storage
    app.config['SESSION_TYPE'] = 'filesystem'  # You can also use 'redis', 'memcached', etc.
    app.config['SESSION_FILE_DIR'] = conf.sessions_dir  # Replace with your PythonAnywhere username and desired session directory
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    Session(app)


    from app.routes.main import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint)



    return app

