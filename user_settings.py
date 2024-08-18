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

def connect_to_database():
    try:
        conn = mysql.connector.connect(
                host = mysql_host,
                user = mysql_user,
                password = mysql_password,
                database = mysql_database
        )
        return conn
    except Error as e:
            print(f"Error connecting to database: {e}")
            return None
    
def execute_query(query, params=None):
    try:
        conn = connect_to_database()
        if conn and conn.is_connected():
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor
        else:
            print("Failed to connect to the database")
            return None
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            conn.close()

def create_new_user(username, password):
    try:
        conn = connect_to_database()

        if conn.is_connected():
            with conn.cursor() as cursor:
                insert_new_user = """
                INSERT INTO users (username, password)
                VALUES (%s, %s)
                """

                hashed_password = hash_password(password)

                cursor.execute(insert_new_user, (username, hashed_password))
                conn.commit()

                print(f'{username} created successfully.')
        else:
            print("Failed to connect to the database")

    except Error as e:
        print(f"Error creating new user: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

            
def login(username):
    try:
        conn = connect_to_database()
        if conn.is_connected():
            cursor = conn.cursor()
            login_user = """
            SELECT *
            FROM users
            WHERE username = %s
            """
            cursor.execute(login_user, (username, ))
            user_id = cursor.fetchone()[0]
            

            return username, user_id
            

    except Error as e:
        print(e)

def rate_shift(user_id, shift_id, amount):
    try:
        conn = connect_to_database()
        if conn.is_connected():
            cursor = conn.cursor()

            insert_rating_query = """
            INSERT INTO points (user_id, shift_id, points)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE points = %s, rated_at = CURRENT_TIMESTAMP
            """

            cursor.execute(insert_rating_query, (user_id, shift_id, amount, amount))
            conn.commit()
            print("Shift points adjusted.")

    except Error as e:
        print(e)

def get_shift_rating(user_id, shift_id):
    pass
        
    


def add_shifts_to_database(file_path):
    with open (file_path, 'r') as f:
        turnus_data = json.load(f)

    try:
        conn = connect_to_database()
        if conn.is_connected():
            cursor = conn.cursor()
            for x in turnus_data:
                for name in x.keys():

                    insert_shift = """
                    INSERT INTO shifts (title)
                    VALUES (%s)
                    """
                    cursor.execute(insert_shift, (name, ))
                    conn.commit()
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error adding to shifts table. Error: {e}")
    



if __name__ == '__main__':
    #register_points(10)
    #create_new_user('solve', 'solve')       
    #add_points_to_user('test1', 10)
    user = login('solve')
    rate_shift(user[1], 1, 14)
    



