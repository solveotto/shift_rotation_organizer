#!/usr/bin/env python3
"""
Simple script to populate R24 shifts in the database
"""

import sys
import os
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.utils.db_utils import get_db_session, Shifts, TurnusSet, add_shifts_to_turnus_set

def populate_r24_shifts():
    """Populate R24 shifts from existing JSON file"""
    
    # Get R24 turnus set
    session = get_db_session()
    try:
        r24_set = session.query(TurnusSet).filter_by(year_identifier='R24').first()
        if not r24_set:
            print("❌ R24 turnus set not found!")
            return False
        
        r24_id = r24_set.id
        print(f"✅ Found R24 turnus set with ID: {r24_id}")
        
        # Path to R24 JSON file
        json_path = '/home/solveottooren/mysite/app/static/turnusfiler/r24/turnuser_R24.json'
        
        if not os.path.exists(json_path):
            print(f"❌ JSON file not found: {json_path}")
            return False
        
        print(f"✅ Found JSON file: {json_path}")
        
        # Use the existing function to add shifts
        add_shifts_to_turnus_set(json_path, r24_id)
        print(f"✅ Successfully populated R24 shifts")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    populate_r24_shifts()