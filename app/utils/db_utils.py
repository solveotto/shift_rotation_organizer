from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.orm import sessionmaker, declarative_base
import configparser
import json
import bcrypt
from flask import flash


# SQLAlchemy Models
Base = declarative_base()



class DBUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_auth = Column(Integer, default=0)

class Points(Base):
    __tablename__ = 'points'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    shift_title = Column(String(255), nullable=False)
    user_points = Column(Integer, default=0)
    rated_at = Column(DateTime, default=func.current_timestamp())
    __table_args__ = (UniqueConstraint('user_id', 'shift_title'),)

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




config = configparser.ConfigParser()
config.read('config.ini')
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

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

def set_user_points(user_id, shift_title, amount):
    session = get_db_session()
    try:
        existing = session.query(Points).filter_by(user_id=user_id, shift_title=shift_title).first()
        if existing:
            existing.user_points = amount
            existing.rated_at = func.current_timestamp()
        else:
            new_point = Points(user_id=user_id, shift_title=shift_title, user_points=amount)
            session.add(new_point)
        session.commit()
        print("Shift points adjusted.")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error setting user points: {e}")
        return False
    finally:
        session.close()


def get_user_points(user_id, shift_title):
    session = get_db_session()
    try:
        result = session.query(Points.user_points).filter_by(user_id=user_id, shift_title=shift_title).first()
        if result:
            return result.user_points
        else:
            return 0
    finally:
        session.close()


def get_shift_rating(user_id, shift_title):
    session = get_db_session()
    try:
        result = session.query(Points).filter_by(user_id=user_id, shift_title=shift_title).first()
        if result:
            return result.shift_title, result.user_points  # Same return format as before
        else:
            return '', 0
    finally:
        session.close()
    
    
def get_all_ratings(user_id):
    try:
        session = get_db_session()
        results = session.query(Points.shift_title, Points.user_points).filter_by(user_id=user_id).all()
        return [(result.shift_title, result.user_points) for result in results]
    finally:
        session.close()

    
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
        # First, get the order_index of the favorite to be removed
        favorite_to_remove = session.query(Favorites).filter_by(user_id=user_id, shift_title=title).first()
        if not favorite_to_remove:
            print("Favorite not found")
            return False
        
        removed_order_index = favorite_to_remove.order_index
        
        # Delete the favorite
        session.delete(favorite_to_remove)
        
        # Update order indices of remaining favorites
        remaining_favorites = session.query(Favorites).filter(
            Favorites.user_id == user_id,
            Favorites.order_index > removed_order_index
        ).all()
        
        for favorite in remaining_favorites:
            favorite.order_index -= 1
        
        session.commit()
        print("Favorite removed successfully")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error removing favorite: {e}")
        return False
    finally:
        session.close()


if __name__ == '__main__':
    create_new_user('testuser', 'testuser')
    #add_points_to_user('test1', 10)
    #username, user_id = login('solve')

    #set_user_points('4', 'OSL_01', 17)

    #try:
    #    username = get_user_data('testuser')
    #    print(username)
    #except TypeError:
    #    print("User Does Not Exsist")
    
    
    
    # result = execute_query(query, fetch=True)
    # print(result)
 

