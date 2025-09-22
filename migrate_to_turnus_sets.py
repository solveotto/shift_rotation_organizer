#!/usr/bin/env python3
"""
Migration script to add TurnusSet support to existing database
This script will:
1. Create new tables (turnus_sets)
2. Add new columns to existing tables
3. Migrate existing data to new structure
4. Create initial R25 turnus set from existing data
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.db_utils import engine, SessionLocal, Base
from sqlalchemy import text

def backup_existing_data():
    """Backup existing favorites and shifts data"""
    session = SessionLocal()
    try:
        print("📁 Backing up existing data...")
        
        # Backup favorites
        favorites_result = session.execute(text("SELECT * FROM favorites"))
        favorites_backup = [dict(row._mapping) for row in favorites_result]
        
        # Backup shifts
        shifts_result = session.execute(text("SELECT * FROM shifts"))
        shifts_backup = [dict(row._mapping) for row in shifts_result]
        
        # Save to files
        with open('backup_favorites.json', 'w') as f:
            json.dump(favorites_backup, f, default=str, indent=2)
        
        with open('backup_shifts.json', 'w') as f:
            json.dump(shifts_backup, f, default=str, indent=2)
        
        print(f"✅ Backed up {len(favorites_backup)} favorites and {len(shifts_backup)} shifts")
        return favorites_backup, shifts_backup
        
    except Exception as e:
        print(f"❌ Error backing up data: {e}")
        return [], []
    finally:
        session.close()

def create_new_tables():
    """Create the new tables"""
    session = SessionLocal()
    try:
        print("🔧 Creating new tables...")
        
        # Create turnus_sets table
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS turnus_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                year_identifier VARCHAR(10) NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        print("✅ Created turnus_sets table")
        session.commit()
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

def add_columns_to_existing_tables():
    """Add turnus_set_id columns to existing tables"""
    session = SessionLocal()
    try:
        print("🔧 Adding columns to existing tables...")
        
        # Add turnus_set_id to favorites table
        try:
            session.execute(text("ALTER TABLE favorites ADD COLUMN turnus_set_id INTEGER DEFAULT 1"))
            print("✅ Added turnus_set_id to favorites table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  turnus_set_id already exists in favorites table")
            else:
                raise e
        
        # Add turnus_set_id to shifts table
        try:
            session.execute(text("ALTER TABLE shifts ADD COLUMN turnus_set_id INTEGER DEFAULT 1"))
            print("✅ Added turnus_set_id to shifts table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  turnus_set_id already exists in shifts table")
            else:
                raise e
        
        session.commit()
        
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        session.rollback()
        return False
    finally:
        session.close()
    
    return True

def create_initial_turnus_set():
    """Create initial R25 turnus set and link existing data"""
    session = SessionLocal()
    try:
        print("🔧 Creating initial R25 turnus set...")
        
        # Check if R25 turnus set already exists
        result = session.execute(text("SELECT id FROM turnus_sets WHERE year_identifier = 'R25'"))
        existing = result.fetchone()
        
        if existing:
            turnus_set_id = existing[0]
            print(f"ℹ️  R25 turnus set already exists with ID {turnus_set_id}")
        else:
            # Create R25 turnus set - fix the parameter binding
            session.execute(text("""
                INSERT INTO turnus_sets (name, year_identifier, is_active, created_at)
                VALUES (:name, :year_id, :is_active, :created_at)
            """), {
                'name': 'OSL Train Shifts R25',
                'year_id': 'R25',
                'is_active': 1,
                'created_at': datetime.now()
            })
            
            # Get the ID of the created turnus set
            result = session.execute(text("SELECT id FROM turnus_sets WHERE year_identifier = 'R25'"))
            turnus_set_id = result.fetchone()[0]
            print(f"✅ Created R25 turnus set with ID {turnus_set_id}")
        
        # Update existing favorites to link to R25 turnus set
        favorites_result = session.execute(
            text("UPDATE favorites SET turnus_set_id = :turnus_set_id WHERE turnus_set_id IS NULL OR turnus_set_id = 1"),
            {'turnus_set_id': turnus_set_id}
        )
        print(f"✅ Updated {favorites_result.rowcount} favorites to link to R25")
        
        # Update existing shifts to link to R25 turnus set
        shifts_result = session.execute(
            text("UPDATE shifts SET turnus_set_id = :turnus_set_id WHERE turnus_set_id IS NULL OR turnus_set_id = 1"),
            {'turnus_set_id': turnus_set_id}
        )
        print(f"✅ Updated {shifts_result.rowcount} shifts to link to R25")
        
        session.commit()
        return turnus_set_id
        
    except Exception as e:
        print(f"❌ Error creating initial turnus set: {e}")
        session.rollback()
        return None
    finally:
        session.close()

def verify_migration():
    """Verify the migration was successful"""
    session = SessionLocal()
    try:
        print("🔍 Verifying migration...")
        
        # Check turnus_sets table
        result = session.execute(text("SELECT COUNT(*) FROM turnus_sets"))
        turnus_count = result.fetchone()[0]
        print(f"✅ Found {turnus_count} turnus set(s)")
        
        # Check favorites
        result = session.execute(text("SELECT COUNT(*) FROM favorites WHERE turnus_set_id IS NOT NULL"))
        favorites_count = result.fetchone()[0]
        print(f"✅ {favorites_count} favorites linked to turnus sets")
        
        # Check shifts
        result = session.execute(text("SELECT COUNT(*) FROM shifts WHERE turnus_set_id IS NOT NULL"))
        shifts_count = result.fetchone()[0]
        print(f"✅ {shifts_count} shifts linked to turnus sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False
    finally:
        session.close()

def main():
    print("🚀 Starting TurnusSet Migration")
    print("=" * 50)
    
    # Step 1: Backup existing data
    favorites_backup, shifts_backup = backup_existing_data()
    
    # Step 2: Create new tables
    if not create_new_tables():
        print("❌ Failed to create new tables. Aborting migration.")
        return False
    
    # Step 3: Add columns to existing tables
    if not add_columns_to_existing_tables():
        print("❌ Failed to add columns. Aborting migration.")
        return False
    
    # Step 4: Create initial turnus set and migrate data
    turnus_set_id = create_initial_turnus_set()
    if not turnus_set_id:
        print("❌ Failed to create initial turnus set. Aborting migration.")
        return False
    
    # Step 5: Verify migration
    if not verify_migration():
        print("❌ Migration verification failed.")
        return False
    
    print("=" * 50)
    print("✅ Migration completed successfully!")
    print(f"📊 Your existing data has been migrated to R25 turnus set (ID: {turnus_set_id})")
    print("📁 Backup files created: backup_favorites.json, backup_shifts.json")
    print("🎯 You can now create additional turnus sets through the admin interface")
    
    return True

if __name__ == "__main__":
    main()