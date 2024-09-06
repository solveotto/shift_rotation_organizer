from flask_login import UserMixin

# Example user data
users = {
    'user1': {'password': 'password1'},
    'user2': {'password': 'password2'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

    @staticmethod
    def get(username):
        if username in users:
            return User(username)
        return None