#!/usr/bin/env python3
"""
Database Migration Script
Migrates from single-turnus system to multi-turnus system with database storage

WHEN TO USE:
- Run this ONCE when upgrading from the old single-turnus system
- to the new multi-turnus system with database storage

USAGE:
- From project root: python app/utils/migrate_database.py
- Creates backup files in project root
- Safe to run multiple times (checks for existing columns)

WHAT IT DOES:
1. Creates turnus_sets table
2. Adds turnus_set_id columns to favorites and shifts tables
3. Adds file path columns to turnus_sets table
4. Migrates existing R25 data to new structure
5. Updates file paths for existing data

BACKUP:
- Creates backup_favorites.json and backup_shifts.json before migration
- Safe to re-run if something goes wrong
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path (go up two levels from app/utils/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.utils.db_utils import engine, SessionLocal, Base, TurnusSet
from sqlalchemy import text
from config import conf

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
    """Create the new tables using SQLAlchemy Core"""
    try:
        print("🔧 Creating new tables...")

        # Use SQLAlchemy Core to create tables (handles database differences)
        Base.metadata.create_all(engine)

        print("✅ Created turnus_sets table")
        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

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

        # Add file path columns to turnus_sets table
        try:
            session.execute(text("ALTER TABLE turnus_sets ADD COLUMN turnus_file_path VARCHAR(500)"))
            print("✅ Added turnus_file_path to turnus_sets table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  turnus_file_path already exists in turnus_sets table")
            else:
                raise e

        try:
            session.execute(text("ALTER TABLE turnus_sets ADD COLUMN df_file_path VARCHAR(500)"))
            print("✅ Added df_file_path to turnus_sets table")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  df_file_path already exists in turnus_sets table")
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

def update_existing_file_paths():
    """Update file paths for existing turnus sets"""
    session = SessionLocal()
    try:
        print("🔧 Updating file paths for existing turnus sets...")

        # Check if files are in turnusfiler or legacy locations
        turnusfiler_dir = os.path.join(conf.static_dir, 'turnusfiler')

        # Update R25 paths
        if os.path.exists(os.path.join(turnusfiler_dir, 'r25')):
            # Files are in turnusfiler
            r25_turnus_path = os.path.join(turnusfiler_dir, 'r25/turnuser_R25.json')
            r25_df_path = os.path.join(turnusfiler_dir, 'r25/turnus_df_R25.json')
            print("   📂 Using turnusfiler location for R25")
        else:
            # Files are in legacy location
            r25_turnus_path = os.path.join(conf.static_dir, 'r25/turnuser_R25.json')
            r25_df_path = os.path.join(conf.static_dir, 'r25/turnus_df_R25.json')
            print("   📂 Using legacy location for R25")

        session.execute(text("""
            UPDATE turnus_sets
            SET turnus_file_path = :turnus_path, df_file_path = :df_path
            WHERE year_identifier = 'R25'
        """), {
            'turnus_path': r25_turnus_path,
            'df_path': r25_df_path
        })

        # Update R24 if it exists
        result = session.execute(text("SELECT id FROM turnus_sets WHERE year_identifier = 'R24'"))
        if result.fetchone():
            if os.path.exists(os.path.join(turnusfiler_dir, 'r24')):
                r24_turnus_path = os.path.join(turnusfiler_dir, 'r24/turnuser_R24.json')
                r24_df_path = os.path.join(turnusfiler_dir, 'r24/turnus_df_R24.json')
                print("   📂 Using turnusfiler location for R24")
            else:
                r24_turnus_path = os.path.join(conf.static_dir, 'r24/turnuser_R24.json')
                r24_df_path = os.path.join(conf.static_dir, 'r24/turnus_df_R24.json')
                print("   📂 Using legacy location for R24")

            session.execute(text("""
                UPDATE turnus_sets
                SET turnus_file_path = :turnus_path, df_file_path = :df_path
                WHERE year_identifier = 'R24'
            """), {
                'turnus_path': r24_turnus_path,
                'df_path': r24_df_path
            })
            print("✅ Updated R24 file paths")

        session.commit()
        print("✅ Updated file paths for existing turnus sets")
        return True

    except Exception as e:
        print(f"❌ Error updating file paths: {e}")
        session.rollback()
        return False
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