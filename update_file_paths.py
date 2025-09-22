#!/usr/bin/env python3
"""
Update database file paths after manual reorganization to turnusfiler
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.utils.db_utils import get_all_turnus_sets, update_turnus_set_paths
from config import conf

def update_paths():
    """Update database paths for manually moved files"""
    
    print("🔧 Updating database file paths for turnusfiler organization...")
    
    turnusfiler_dir = os.path.join(conf.static_dir, 'turnusfiler')
    
    # Check if migration was run
    try:
        turnus_sets = get_all_turnus_sets()
        print(f"Found {len(turnus_sets)} turnus sets in database")
    except Exception as e:
        print(f"❌ Error getting turnus sets. Did you run the migration? Error: {e}")
        return
    
    for turnus_set in turnus_sets:
        year_id = turnus_set['year_identifier']
        year_dir = os.path.join(turnusfiler_dir, year_id.lower())
        
        new_turnus_path = os.path.join(year_dir, f'turnuser_{year_id}.json')
        new_df_path = os.path.join(year_dir, f'turnus_df_{year_id}.json')
        
        print(f"\n📁 Checking {year_id}...")
        print(f"   Looking for: {new_turnus_path}")
        print(f"   Looking for: {new_df_path}")
        
        # Check if files exist in new location
        turnus_exists = os.path.exists(new_turnus_path)
        df_exists = os.path.exists(new_df_path)
        
        if turnus_exists and df_exists:
            success, message = update_turnus_set_paths(
                turnus_set['id'], 
                new_turnus_path, 
                new_df_path
            )
            
            if success:
                print(f"✅ Updated {year_id} database paths")
            else:
                print(f"❌ Failed to update {year_id}: {message}")
        else:
            print(f"⚠️  Missing files for {year_id}:")
            if not turnus_exists:
                print(f"   ❌ Missing: turnuser_{year_id}.json")
            else:
                print(f"   ✅ Found: turnuser_{year_id}.json")
            if not df_exists:
                print(f"   ❌ Missing: turnus_df_{year_id}.json")
            else:
                print(f"   ✅ Found: turnus_df_{year_id}.json")
    
    print("\n🎉 Database path update completed!")
    print("Now restart your app: python run.py")

if __name__ == "__main__":
    update_paths()