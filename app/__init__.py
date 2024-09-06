from flask import Flask
from flask_login import LoginManager
from config import Config
from app.forms import User





def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'


    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    from app.routes import main
    app.register_blueprint(main, url_prefix='/')


    return app

