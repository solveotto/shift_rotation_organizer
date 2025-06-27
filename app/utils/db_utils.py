from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    query = """
    SELECT user_points FROM points WHERE user_id = %s AND shift_title = %s
    """
    result = execute_query(query, (user_id, shift_title), fetch=True)
    
    if result:
        points = result[0][0]
        return points
    else:
        points = 0
        return points


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

    # Gammelt format
    # query = """
    # SELECT shift_title, user_points FROM points WHERE user_id = %s
    # """
    # result = execute_query(query, (user_id, ), fetch=True)

    # return result
    
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

# FØR ALCHEMY
# def add_shifts_to_database(file_path):
#     with open (file_path, 'r') as f:
#         turnus_data = json.load(f)
    
#     for x in turnus_data:
#         for name in x.keys():
#             insert_shift = """
#             INSERT INTO shifts (title)
#             VALUES (%s)
#             """
#             execute_query(insert_shift, (name, ))
            


#### USER LOGIN AND REG ####

def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_pw.decode('utf-8')


def create_new_user(username, hashed_password):
    query = """
    INSERT INTO users (username, password)
    VALUES (%s, %s)
    """
    result = execute_query(query, (username, hash_password(hashed_password)))

    if result:
        print(f"User created")
    else:
        print('Error creating user')

            
def get_user_data(username):
    login_user_query = "SELECT id, username, password, is_auth FROM users WHERE username = %s" if db_type == 'mysql' else "SELECT id, username, password, is_auth FROM users WHERE username = ?"
    result = execute_query(login_user_query, (username, ), fetch=True)
    if result:
        # result[0] is a tuple: (id, username, password, is_auth)
        data = {'id': result[0][0], 'username': result[0][1], 'password': result[0][2], 'is_auth': result[0][3]}
        return data
    else:
        print("Failed to execute login query!")
        return None

def get_user_password(username):
    query = """
    SELECT password FROM users WHERE username = %s
    """
    result = execute_query(query, (username, ), fetch='fetchone')
    return result



### FAVORITES ###

def get_favorite_lst(user_id):
    query_fetch_order = """
        SELECT id, shift_title FROM favorites WHERE user_id = %s ORDER BY order_index
        """
    result = execute_query(query_fetch_order, (user_id, ), fetch='fetchall')
    shift_titles = [item[1] for item in result]
    return shift_titles


def update_favorite_order(user_id):
    try:
        # Fetch the current order of the favorites
        query_fetch_order = """
        SELECT id, shift_title FROM favorites WHERE user_id = %s
        """
        current_database_order = execute_query(query_fetch_order, (user_id, ), fetch='fetchall')
        current_shift_titles = {shift[1] for shift in current_database_order}

        # update curent favorties order in database
        for index, shift_title in enumerate(current_shift_titles):
            query_update_order = """
            INSERT INTO favorites (shift_title, user_id, order_index)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE order_index = VALUES(order_index)
            """

            execute_query(query_update_order, (shift_title, user_id, index))
    except Error as e:
        print(f"Failed to modify database. Changes only stored localy. Error = {e}")
        flash(f'Failed to modify database. Changes only stored localy. Error = {e}', 'danger')


def get_max_ordered_index(user_id):
    session = get_db_session()
    try:
        result = session.query(func.max(Favorites.order_index)).filter_by(user_id=user_id).scalar()
        return result if result is not None else 0
    finally:
        session.close()

def add_favorite(user_id, title, order_index):
    print('ADD FAVORITE EXECUTED')
    query_add_title = """
        INSERT INTO favorites (user_id, shift_title, order_index)
        VALUES (%s, %s, %s)
    """
    execute_query(query_add_title, (user_id, title, order_index))

def remove_favorite(user_id, title):
    query_remove_title = """
        DELETE FROM favorites
        WHERE user_id = %s AND shift_title = %s
    """
    execute_query(query_remove_title, (user_id, title))
    
    # Update order indices of remaining favorites
    query_update_order = """
        UPDATE favorites
        SET order_index = order_index - 1
        WHERE user_id = %s AND order_index > (
            SELECT order_index FROM favorites WHERE user_id = %s AND shift_title = %s
        )
    """
    execute_query(query_update_order, (user_id, user_id, title))


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
 

