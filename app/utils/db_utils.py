import mysql.connector
from mysql.connector import Error
import configparser
import json
import bcrypt
from flask import flash



config = configparser.ConfigParser()
config.read('config.ini')
mysql_host = config['mysql']['host']
mysql_user = config['mysql']['user']
mysql_password = config['mysql']['password']
mysql_database = config['mysql']['database']

   
def execute_query(query, params=None, fetch=False):
    conn = None
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
                elif fetch == "fetchone":
                    result = cursor.fetchone()
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
    login_user_query = """
            SELECT *
            FROM users
            WHERE username = %s
            """
    result = execute_query(login_user_query, (username, ), fetch=True)
    if result:
        data = {'username': result[0][1], 'id': result[0][0], 'password': result[0][2], 'is_auth': result[0][5]}
        return data
    else:
        print("Failed to execute login query!")

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
    query_max_index = """
        SELECT MAX(order_index) FROM favorites WHERE user_id = %s
    """
    result = execute_query(query_max_index, (user_id, ), fetch='fetchone')
    print('get_max_index', result[0][0])
    return result[0][0] if result[0][0] is not None else 0


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

    update_favorite_order(user_id)


if __name__ == '__main__':
    create_new_user('bård', 'førsterad')
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
 

