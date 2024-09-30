import bcrypt
import app.utils.db_utils as db_utils
from flask_login import UserMixin
from flask_caching import Cache


cache = Cache(config={'CACHE_TYPE': 'simple'})

class User(UserMixin):
    def __init__(self, username, user_id, is_admin):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin

    def get_id(self):
        return self.id
    
    def get_username(self):
        return self.username

    @staticmethod
    def get(username):
        from app import cache  # Import cache object from app module
        user = cache.get(f'user_{username}')
        if not user:
            db_user_data = db_utils.get_user_data(username)
            if db_user_data:
                user = User(username, db_user_data['id'], db_user_data['is_auth'])
                cache.set(f'user_{username}', user, timeout=60)
        return user
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    
