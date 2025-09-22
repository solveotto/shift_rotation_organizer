import bcrypt
import app.utils.db_utils as db_utils
from flask_login import UserMixin
from flask_caching import Cache

class User(UserMixin):
    def __init__(self, username, user_id, is_admin):
        self.id = user_id
        self.username = username
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)
    
    def get_username(self):
        return self.username

    @staticmethod
    def get(username):
        """Get user by username - used by Flask-Login"""
        from app import cache
        user = cache.get(f'user_{username}')
        if not user:
            db_user_data = db_utils.get_user_data(username)
            if db_user_data:
                user = User(username, db_user_data['id'], db_user_data['is_auth'])
                cache.set(f'user_{username}', user, timeout=60)
        return user

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return User.get(username)

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID (required for Flask-Login)"""
        session = db_utils.get_db_session()
        try:
            from app.utils.db_utils import DBUser
            db_user = session.query(DBUser).filter_by(id=user_id).first()
            if db_user:
                return User(db_user.username, db_user.id, db_user.is_auth)
            return None
        finally:
            session.close()
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a password against the stored hash"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    
    def set_password(self, password):
        """Hash and set the password"""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return hashed
    
    def verify_password_instance(self, password):
        """Verify a password for this user instance"""
        # Get the stored password from database
        stored_password = db_utils.get_user_password(self.username)
        if stored_password:
            return User.verify_password(stored_password, password)
        return False

# Keep cache for backwards compatibility
cache = Cache(config={'CACHE_TYPE': 'simple'})