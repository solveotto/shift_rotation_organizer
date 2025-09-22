#!/usr/bin/env python3
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.utils.db_utils import get_db_session, Favorites, TurnusSet

def check_favorites():
    session = get_db_session()
    try:
        # Get all favorites with turnus set info
        results = session.query(
            Favorites.user_id, 
            Favorites.shift_title, 
            Favorites.turnus_set_id,
            TurnusSet.year_identifier
        ).join(TurnusSet, Favorites.turnus_set_id == TurnusSet.id).all()
        
        print("🔍 All favorites in database:")
        for user_id, shift_title, turnus_set_id, year_id in results:
            print(f"  User {user_id}: {shift_title} → {year_id} (turnus_set_id: {turnus_set_id})")
            
    finally:
        session.close()

if __name__ == "__main__":
    check_favorites()