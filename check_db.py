#!/usr/bin/env python3

from app.utils.db_utils import create_tables, get_db_session
from app.utils.db_utils import DBUser, Favorites, Shifts

def check_database():
    try:
        # This will create tables if they don't exist
        create_tables()
        print("✓ Database tables created/verified successfully")
        
        # Check if we can connect and query
        session = get_db_session()
        try:
            # Try to query each table to make sure they exist
            user_count = session.query(DBUser).count()
            favorites_count = session.query(Favorites).count()
            shifts_count = session.query(Shifts).count()
            
            print(f"✓ Database connection successful")
            print(f"  - Users: {user_count}")
            print(f"  - Favorites: {favorites_count}")
            print(f"  - Shifts: {shifts_count}")
            
        finally:
            session.close()
            
    except Exception as e:
        print(f"✗ Database error: {e}")

if __name__ == "__main__":
    check_database() 