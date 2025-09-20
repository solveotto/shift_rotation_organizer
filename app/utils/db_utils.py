import sys
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, func, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import json
import bcrypt
from flask import flash

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
from config import conf

# SQLAlchemy Models
Base = declarative_base()



class DBUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_auth = Column(Integer, default=0)

class Favorites(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    shift_title = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('user_id', 'shift_title'),)

class Shifts(Base):
    __tablename__ = 'shifts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), unique=True, nullable=False)




config = conf.CONFIG
db_type = config['general'].get('db_type', 'mysql')

if db_type == 'mysql':
    mysql_host = config['mysql']['host']
    mysql_user = config['mysql']['user']
    mysql_password = config['mysql']['password']
    mysql_database = config['mysql']['database']
    DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
elif db_type == 'sqlite':
    sqlite_path = config['sqlite']['path']
    DATABASE_URL = f"sqlite:///{sqlite_path}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        'connect_timeout': 20,
        'read_timeout': 20,
        'write_timeout': 20,
    } if db_type == 'mysql' else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

def add_shifts_to_database(file_path):
    session = get_db_session()
    try:
        with open(file_path, 'r') as f:
            turnus_data = json.load(f)
        
        for x in turnus_data:
            for name in x.keys():
                # Check if shift already exists to avoid duplicates
                existing = session.query(Shifts).filter_by(title=name).first()
                if not existing:
                    new_shift = Shifts(title=name)
                    session.add(new_shift)
        
        session.commit()
        print("Shifts added to database successfully")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding shifts to database: {e}")
        return False
    finally:
        session.close()


#### USER LOGIN AND REG ####

def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_pw.decode('utf-8')


def create_new_user(username, hashed_password):
    session = get_db_session()
    try:
        new_user = DBUser(username=username, password=hash_password(hashed_password))
        session.add(new_user)
        session.commit()
        print(f"User created")
        return True
    except Exception as e:
        session.rollback()
        print(f'Error creating user: {e}')
        return False
    finally:
        session.close()

            
def get_user_data(username):
    session = get_db_session()
    try:
        result = session.query(DBUser).filter_by(username=username).first()
        if result:
            data = {
                'id': result.id, 
                'username': result.username, 
                'password': result.password, 
                'is_auth': result.is_auth
            }
            return data
        else:
            print("Failed to execute login query!")
            return None
    finally:
        session.close()

def get_user_password(username):
    session = get_db_session()
    try:
        result = session.query(DBUser.password).filter_by(username=username).first()
        return result.password if result else None
    finally:
        session.close()



### FAVORITES ###

def get_favorite_lst(user_id):
    session = get_db_session()
    try:
        results = session.query(Favorites.shift_title).filter_by(user_id=user_id).order_by(Favorites.order_index).all()
        shift_titles = [result.shift_title for result in results]
        return shift_titles
    finally:
        session.close()


def update_favorite_order(user_id):
    session = get_db_session()
    try:
        # Fetch the current order of the favorites
        current_favorites = session.query(Favorites).filter_by(user_id=user_id).all()
        current_shift_titles = [favorite.shift_title for favorite in current_favorites]

        # Update current favorites order in database
        for index, shift_title in enumerate(current_shift_titles):
            favorite = session.query(Favorites).filter_by(user_id=user_id, shift_title=shift_title).first()
            if favorite:
                favorite.order_index = index
        
        session.commit()
        print("Favorite order updated successfully")
        return True
    except Exception as e:
        session.rollback()
        print(f"Failed to modify database. Changes only stored locally. Error = {e}")
        flash(f'Failed to modify database. Changes only stored locally. Error = {e}', 'danger')
        return False
    finally:
        session.close()


def get_max_ordered_index(user_id):
    session = get_db_session()
    try:
        result = session.query(func.max(Favorites.order_index)).filter_by(user_id=user_id).scalar()
        return result if result is not None else 0
    finally:
        session.close()

def add_favorite(user_id, title, order_index):
    print('ADD FAVORITE EXECUTED')
    session = get_db_session()
    try:
        new_favorite = Favorites(user_id=user_id, shift_title=title, order_index=order_index)
        session.add(new_favorite)
        session.commit()
        print("Favorite added successfully")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding favorite: {e}")
        return False
    finally:
        session.close()

def remove_favorite(user_id, title):
    session = get_db_session()
    try:
        favorite = session.query(Favorites).filter_by(user_id=user_id, shift_title=title).first()
        if favorite:
            session.delete(favorite)
            session.commit()
            print(f"Favorite removed: {title}")
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error removing favorite: {e}")
        return False
    finally:
        session.close()

### ADMIN FUNCTIONS ###

def get_all_users():
    """Get all users from the database"""
    session = get_db_session()
    try:
        users = session.query(DBUser).all()
        return [
            {
                'id': user.id,
                'username': user.username,
                'is_auth': user.is_auth
            }
            for user in users
        ]
    finally:
        session.close()

def get_user_by_id(user_id):
    """Get a specific user by ID"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'is_auth': user.is_auth
            }
        return None
    finally:
        session.close()

def create_user(username, password, is_auth=0):
    """Create a new user"""
    session = get_db_session()
    try:
        # Check if username already exists
        existing_user = session.query(DBUser).filter_by(username=username).first()
        if existing_user:
            return False, "Username already exists"
        
        new_user = DBUser(
            username=username,
            password=hash_password(password),
            is_auth=is_auth
        )
        session.add(new_user)
        session.commit()
        return True, "User created successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error creating user: {e}"
    finally:
        session.close()

def update_user(user_id, username, password=None, is_auth=None):
    """Update an existing user"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "User not found"
        
        # Check if new username conflicts with existing user
        if username != user.username:
            existing_user = session.query(DBUser).filter_by(username=username).first()
            if existing_user:
                return False, "Username already exists"
        
        user.username = username
        if password:
            user.password = hash_password(password)
        if is_auth is not None:
            user.is_auth = is_auth
        
        session.commit()
        return True, "User updated successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error updating user: {e}"
    finally:
        session.close()

def delete_user(user_id):
    """Delete a user and all associated data"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "User not found"
        
        # Delete associated favorites
        session.query(Favorites).filter_by(user_id=user_id).delete()
        
        # Delete the user
        session.delete(user)
        session.commit()
        return True, "User deleted successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error deleting user: {e}"
    finally:
        session.close()

def toggle_user_auth(user_id):
    """Toggle user authentication status"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "User not found"
        
        user.is_auth = 1 if user.is_auth == 0 else 0
        session.commit()
        return True, f"User authentication {'enabled' if user.is_auth == 1 else 'disabled'}"
    except Exception as e:
        session.rollback()
        return False, f"Error toggling user auth: {e}"
    finally:
        session.close()

if __name__ == '__main__':
    create_new_user('testuser', 'testuser')

    #try:
    #    username = get_user_data('testuser')
    #    print(username)
    #except TypeError:
    #    print("User Does Not Exsist")
    
    
    
    # result = execute_query(query, fetch=True)
    # print(result)
 

