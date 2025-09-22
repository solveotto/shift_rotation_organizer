#!/usr/bin/env python3
"""
Reorganize existing turnus files into turnusfiler directory
"""

import sys
import os
import shutil

# Add project root to path (go up two levels from app/utils/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.utils.db_utils import get_all_turnus_sets, update_turnus_set_paths
from config import conf


def reorganize_files():
    """Move existing turnus files to turnusfiler directory and update database"""
    
    print("🚀 Reorganizing turnus files into turnusfiler directory")
    print("=" * 60)
    
    turnusfiler_dir = os.path.join(conf.static_dir, 'turnusfiler')
    os.makedirs(turnusfiler_dir, exist_ok=True)
    
    # Get all existing turnus sets
    turnus_sets = get_all_turnus_sets()
    
    for turnus_set in turnus_sets:
        year_id = turnus_set['year_identifier']
        old_dir = os.path.join(conf.static_dir, year_id.lower())
        new_dir = os.path.join(turnusfiler_dir, year_id.lower())
        
        print(f"\n📁 Processing {year_id}...")
        
        if os.path.exists(old_dir):
            # Move the entire directory
            if os.path.exists(new_dir):
                print(f"⚠️  Target directory already exists: {new_dir}")
                print(f"   Merging files...")
                # Merge directories
                for item in os.listdir(old_dir):
                    old_path = os.path.join(old_dir, item)
                    new_path = os.path.join(new_dir, item)
                    if os.path.isfile(old_path):
                        shutil.copy2(old_path, new_path)
                        print(f"   📄 Copied: {item}")
                    elif os.path.isdir(old_path):
                        shutil.copytree(old_path, new_path, dirs_exist_ok=True)
                        print(f"   📂 Copied directory: {item}")
                
                # Remove old directory after successful copy
                shutil.rmtree(old_dir)
                print(f"   🗑️  Removed old directory: {old_dir}")
            else:
                # Move entire directory
                shutil.move(old_dir, new_dir)
                print(f"   ✅ Moved: {old_dir} → {new_dir}")
            
            # Update database with new file paths
            new_turnus_path = os.path.join(new_dir, f'turnuser_{year_id}.json')
            new_df_path = os.path.join(new_dir, f'turnus_df_{year_id}.json')
            
            success, message = update_turnus_set_paths(
                turnus_set['id'], 
                new_turnus_path, 
                new_df_path
            )
            
            if success:
                print(f"   💾 Updated database paths for {year_id}")
            else:
                print(f"   ❌ Failed to update database paths: {message}")
                
            # Verify files exist in new location
            if os.path.exists(new_turnus_path) and os.path.exists(new_df_path):
                print(f"   ✅ Files verified in new location")
            else:
                print(f"   ⚠️  Warning: Some files missing in new location")
                
        else:
            print(f"   ℹ️  Directory not found: {old_dir} (may already be moved)")
    
    print("\n" + "=" * 60)
    print("✅ File reorganization completed!")
    print(f"📂 All turnus files are now in: {turnusfiler_dir}")
    print("💡 You can now use the --turnusfiler flag for new turnus sets")

if __name__ == "__main__":
    reorganize_files()