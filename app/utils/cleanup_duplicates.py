#!/usr/bin/env python3
"""
Database cleanup utility to remove duplicate favorites
Run this script to clean up existing duplicate entries in the favorites table
"""

import sys
import os
from collections import defaultdict

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from app.utils import db_utils
from sqlalchemy import func

def find_duplicates():
    """Find all duplicate favorites in the database"""
    session = db_utils.get_db_session()
    try:
        # Find duplicates by grouping user_id, shift_title, turnus_set_id
        duplicates = session.query(
            db_utils.Favorites.user_id,
            db_utils.Favorites.shift_title,
            db_utils.Favorites.turnus_set_id,
            func.count(db_utils.Favorites.id).label('count')
        ).group_by(
            db_utils.Favorites.user_id,
            db_utils.Favorites.shift_title,
            db_utils.Favorites.turnus_set_id
        ).having(func.count(db_utils.Favorites.id) > 1).all()
        
        return duplicates
    finally:
        session.close()

def cleanup_duplicates(dry_run=True):
    """
    Remove duplicate favorites, keeping only the one with the lowest order_index
    If dry_run=True, just report what would be deleted without actually deleting
    """
    session = db_utils.get_db_session()
    try:
        duplicates = find_duplicates()
        
        if not duplicates:
            print("No duplicates found!")
            return
        
        print(f"Found {len(duplicates)} sets of duplicates:")
        
        total_deleted = 0
        
        for user_id, shift_title, turnus_set_id, count in duplicates:
            print(f"\nUser {user_id}, Shift '{shift_title}', Turnus Set {turnus_set_id}: {count} duplicates")
            
            # Get all duplicates for this combination
            all_entries = session.query(db_utils.Favorites).filter_by(
                user_id=user_id,
                shift_title=shift_title,
                turnus_set_id=turnus_set_id
            ).order_by(db_utils.Favorites.order_index).all()
            
            # Keep the first one (lowest order_index), delete the rest
            keep_entry = all_entries[0]
            delete_entries = all_entries[1:]
            
            print(f"  Keeping: ID {keep_entry.id} (order_index: {keep_entry.order_index})")
            
            for entry in delete_entries:
                print(f"  {'Would delete' if dry_run else 'Deleting'}: ID {entry.id} (order_index: {entry.order_index})")
                if not dry_run:
                    session.delete(entry)
                    total_deleted += 1
        
        if not dry_run and total_deleted > 0:
            session.commit()
            print(f"\n✓ Cleaned up {total_deleted} duplicate entries")
        elif dry_run:
            print(f"\nThis was a dry run. To actually delete, run with dry_run=False")
        
    except Exception as e:
        session.rollback()
        print(f"Error during cleanup: {e}")
        raise
    finally:
        session.close()

def reorder_favorites(user_id, turnus_set_id):
    """Reorder favorites for a user to have sequential order_index values"""
    session = db_utils.get_db_session()
    try:
        favorites = session.query(db_utils.Favorites).filter_by(
            user_id=user_id,
            turnus_set_id=turnus_set_id
        ).order_by(db_utils.Favorites.order_index).all()
        
        for i, favorite in enumerate(favorites):
            favorite.order_index = i + 1
        
        session.commit()
        print(f"Reordered {len(favorites)} favorites for user {user_id} in turnus set {turnus_set_id}")
        
    except Exception as e:
        session.rollback()
        print(f"Error reordering favorites: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=== Favorites Database Cleanup Utility ===\n")
    
    # First, show what duplicates exist
    duplicates = find_duplicates()
    if duplicates:
        print("Current duplicates:")
        for user_id, shift_title, turnus_set_id, count in duplicates:
            print(f"  User {user_id}: '{shift_title}' in turnus set {turnus_set_id} ({count} copies)")
        
        print("\nRunning dry run cleanup...")
        cleanup_duplicates(dry_run=True)
        
        response = input("\nDo you want to proceed with actual cleanup? (y/N): ")
        if response.lower() == 'y':
            print("\nRunning actual cleanup...")
            cleanup_duplicates(dry_run=False)
            
            # Reorder favorites for affected users
            affected_users = set((user_id, turnus_set_id) for user_id, shift_title, turnus_set_id, count in duplicates)
            for user_id, turnus_set_id in affected_users:
                reorder_favorites(user_id, turnus_set_id)
        else:
            print("Cleanup cancelled.")
    else:
        print("No duplicates found in the database!")
