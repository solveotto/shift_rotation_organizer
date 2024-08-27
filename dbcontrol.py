import mysql.connector
from mysql.connector import Error
import bcrypt
import configparser
import json



config = configparser.ConfigParser()
config.read('config.ini')
mysql_host = config['mysql']['host']
mysql_user = config['mysql']['user']
mysql_password = config['mysql']['password']
mysql_database = config['mysql']['database']


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_pw.decode('utf-8')

    
def execute_query(query, params=None, fetch=False):
    try:
        conn = mysql.connector.connect(
                host = mysql_host,
                user = mysql_user,
                password = mysql_password,
                database = mysql_database)
        
        if conn and conn.is_connected():
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return True
        else:
            print("Failed to connect to the database")
            return False
    except Error as e:
        print(f"Error executing query: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def create_new_user(username, password):
    query = """
    INSERT INTO users (username, password)
    VALUES (%s, %s)
    """
    hashed_password = hash_password(password)
    result = execute_query(query, (username, hashed_password))

    if result:
        print(f"User created")
    else:
        print('Error creating user')

            
def login(username):
    login_user_query = """
            SELECT *
            FROM users
            WHERE username = %s
            """
    result = execute_query(login_user_query, (username,), fetch=True)
    if result:
        user = result[0][1]
        user_id = result[0][0]
        if user:
            return user, user_id
        else:
            print(f"User {username} not found.")
    else:
        print("Failed to execute login query.")


def get_shift_title(shift_title):
    query = """
    SELECT id FROM shifts WHERE title = %s
    """
    result = execute_query(query, (shift_title, ), fetch=True)
    if result:
        shift_title = result[0][0]
        return shift_title
    else:
        print("Shift not found.")




def set_user_points(user_id, shift_title, amount):
    insert_rating_query = """
    INSERT INTO points (user_id, shift_title, user_points)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE user_points = %s, rated_at = CURRENT_TIMESTAMP
    """
    result = execute_query(insert_rating_query, (user_id, shift_title, amount, amount))
    if result:
        print("Shift points adjusted.")

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
    query = """
    SELECT user_points, shift_title FROM points WHERE user_id = %s AND shift_title = %s
    """
    result = execute_query(query, (user_id, shift_title), fetch=True)
    
    if result:
        points = result[0][0]
        name = result[0][1]
        return name,points
    else:
        points = 0
        name = ''
        return name, points
    
def get_all_ratings(user_id):
    query = """
    SELECT shift_title, user_points FROM points WHERE user_id = %s
    """
    result = execute_query(query, (user_id, ), fetch=True)

    return result
    

def add_shifts_to_database(file_path):
    with open (file_path, 'r') as f:
        turnus_data = json.load(f)
    
    for x in turnus_data:
        for name in x.keys():
            insert_shift = """
            INSERT INTO shifts (title)
            VALUES (%s)
            """
            execute_query(insert_shift, (name, ))
            
    
if __name__ == '__main__':
    #register_points(10)
    #create_new_user('test3', 'test3')       
    #add_points_to_user('test1', 10)
    #username, user_id = login('solve')
    #shift_title = 'OSL_03'
    #shift_title = get_shift_title(shift_title)
    
    
    set_user_points('4', 'OSL_01', 17)

    
    
    
    # result = execute_query(query, fetch=True)
    # print(result)
 

