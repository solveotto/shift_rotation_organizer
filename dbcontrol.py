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


def get_shift_id(shift_id):
    query = """
    SELECT id FROM shifts WHERE title = %s
    """
    result = execute_query(query, (shift_id, ), fetch=True)
    if result:
        shift_id = result[0][0]
        return shift_id
    else:
        print("Shift not found.")


def rate_shift(user_id, shift_id, shift_name, amount):
    insert_rating_query = """
    INSERT INTO points (user_id, shift_id, shift_name, points)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE points = %s, rated_at = CURRENT_TIMESTAMP
    """
    result = execute_query(insert_rating_query, (user_id, shift_id, shift_name, amount, amount))
    if result:
        print("Shift points adjusted.")


def get_shift_rating(user_id, shift_id):
    query = """
    SELECT points, shift_name FROM points WHERE user_id = %s AND shift_id = %s
    """
    result = execute_query(query, (user_id, shift_id), fetch=True)
    if result:
        points = result[0][0]
        name = result[0][1]
        print(f"Rating: {points}")
        return name,points
    
def get_all_ratings(user_id):
    query = """
    SELECT shift_name, points FROM points WHERE user_id = %s
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
    username, user_id = login('solve')
    shift_name = 'OSL_03'
    shift_id = get_shift_id(shift_name)
    
    
    rate_shift(user_id, shift_id, shift_name, 17)

    stored_shifts = get_all_ratings(user_id)
    stored_shifts_dict = {}

    for x in stored_shifts:
        stored_shifts_dict[x[0]] = x[1]



    print(stored_shifts_dict)