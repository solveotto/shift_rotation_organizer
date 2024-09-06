import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_login import UserMixin

from app.utils.db_utils import get_user_data, get_user_password


class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @staticmethod
    def get(username):
        userdata = get_user_data(username)
        if userdata:
            return User(username)
        return None
    

    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# def login_user(username, password):
#     user = User.get(username)
#     if user:
        
#         stored_password = get_user_password(username)

#         print(stored_password)
#         if stored_password and User.verify_password(stored_password[0][0], password):
#             return user
#     return None