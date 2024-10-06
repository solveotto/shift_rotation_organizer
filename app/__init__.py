from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from config import conf
from app.models import User
from flask_session import Session



cache = Cache(config={'CACHE_TYPE': 'simple'})

def create_app():
    app = Flask(__name__)
    app.config.from_object(conf)
    cache.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'


    @login_manager.user_loader
    def load_user(username):
        return User.get(username)

    
    # Configure server-side session storage
    app.config['SESSION_TYPE'] = 'filesystem'  # You can also use 'redis', 'memcached', etc.
    app.config['SESSION_FILE_DIR'] = conf.sessions_dir  # Replace with your PythonAnywhere username and desired session directory
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    Session(app)


    from app.routes import main
    app.register_blueprint(main, url_prefix='/')




    return app

