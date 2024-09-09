import bcrypt
from flask_login import UserMixin

from app.utils.db_utils import get_user_data


class User(UserMixin):
    def __init__(self, username, user_id, is_admin):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin
    
    def get_id(self):
        return self.id

    @staticmethod
    def get(username):
        db_user_data = get_user_data(username)
        if db_user_data:
            return User(username, db_user_data['id'], db_user_data['is_auth'])
        return None
    

    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    
