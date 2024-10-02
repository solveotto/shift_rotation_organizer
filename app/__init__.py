from flask import Flask
from flask_login import LoginManager
from flask_caching import Cache
from config import conf
from app.models import User



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

    from app.routes import main
    app.register_blueprint(main, url_prefix='/')




    return app

