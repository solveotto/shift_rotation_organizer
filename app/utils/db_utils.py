import sys
import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, UniqueConstraint, func, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
import json
import bcrypt
from flask import flash
from datetime import datetime, timedelta
import secrets

logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)
from config import AppConfig, get_database_uri

# SQLAlchemy Models
Base = declarative_base()



class DBUser(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rullenummer: Mapped[int] = mapped_column(String(10), nullable=True)
    name = Column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_auth: Mapped[int] = mapped_column(Integer, default=0)
    email = Column(String(255), nullable=True)
    email_verified: Mapped[int] = mapped_column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    verification_sent_at = Column(DateTime, nullable=True)

class AuthorizedEmails(Base):
    __tablename__ = 'authorized_emails'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    rullenummer = Column(String(50), nullable=True)
    added_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    added_at = Column(DateTime, default=func.now())
    notes = Column(String(500))
    __table_args__ = (UniqueConstraint('email', 'rullenummer', name='unique_email_rullenummer'),)

class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    used: Mapped[int] = mapped_column(Integer, default=0)
    token_type = Column(String(50), default='verification')  # 'verification' or 'password_reset'

class TurnusSet(Base):
    __tablename__ = 'turnus_sets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Human-readable name like "OSL Train Shifts 2025"
    year_identifier = Column(String(10), nullable=False)  # Short identifier like "R25", "R26"
    is_active: Mapped[int] = mapped_column(Integer, default=0)  # 1 = currently active set, 0 = inactive
    created_at = Column(DateTime, default=func.now())
    turnus_file_path = Column(String(500), nullable=True)  # Path to turnuser_XX.json
    df_file_path = Column(String(500), nullable=True)      # Path to turnus_df_XX.json
    __table_args__ = (UniqueConstraint('year_identifier'),)  # Prevent duplicate year IDs

class Favorites(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    user_id = Column(Integer, nullable=False) 
    shift_title = Column(String(255), nullable=False)  # Title of the shift
    turnus_set_id = Column(Integer, nullable=False)  # Links to specific turnus set
    order_index: Mapped[int ]= mapped_column(Integer, default=0)  # Order index for the shift in the turnus set
    __table_args__ = (UniqueConstraint('user_id', 'shift_title', 'turnus_set_id'),)  # Prevent duplicate favorites for the same user and shift

class Shifts(Base):
    __tablename__ = 'shifts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), unique=True, nullable=False)
    turnus_set_id = Column(Integer, nullable=False) # Links to specific turnus set
    __table_args__ = (UniqueConstraint('title', 'turnus_set_id'),)  # Same shift name can exist in different sets




DATABASE_URL = get_database_uri()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        'connect_timeout': 20,
        'read_timeout': 20,
        'write_timeout': 20,
    } if AppConfig.db_type == 'mysql' else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

## TURNUS SETS ##
def create_turnus_set(name, year_identifier, is_active=False, turnus_file_path=None, df_file_path=None):
    """Create a new turnus set with optional file paths"""
    session = get_db_session()
    try:
        existing = session.query(TurnusSet).filter_by(year_identifier=year_identifier).first()
        if existing:
            return False, f"Turnus set with identifier {year_identifier} already exists"
        
        if is_active:
            session.query(TurnusSet).update({'is_active': 0})
        
        new_set = TurnusSet(
            name=name,
            year_identifier=year_identifier,
            is_active=1 if is_active else 0,
            turnus_file_path=turnus_file_path,
            df_file_path=df_file_path
        )
        session.add(new_set)
        session.commit()
        return True, f"Turnus set {year_identifier} created successfully"
    except Exception as e:
        session.rollback()
        return False, f"Error creating turnus set: {e}"
    finally:
        session.close()


def get_all_turnus_sets():
    """Get a list of all turnus sets"""
    session = get_db_session()
    try:
        sets = session.query(TurnusSet).order_by(TurnusSet.year_identifier.desc()).all()
        return [
            {
                'id': ts.id,
                'name': ts.name,
                'year_identifier': ts.year_identifier,
                'is_active': ts.is_active,
                'created_at': ts.created_at,
                'turnus_file_path': ts.turnus_file_path,  # Add this
                'df_file_path': ts.df_file_path           # Add this
            }
            for ts in sets
        ]
    finally:
        session.close()

def get_turnus_set_by_year(year_identifier):
    """Get turnus set by year identifier (e.g., 'R25', 'R26')"""
    session = get_db_session()
    try:
        turnus_set = session.query(TurnusSet).filter_by(year_identifier=year_identifier).first()
        if turnus_set:
            return {
                'id': turnus_set.id,
                'name': turnus_set.name,
                'year_identifier': turnus_set.year_identifier,
                'is_active': turnus_set.is_active,
                'created_at': turnus_set.created_at,
                'turnus_file_path': turnus_set.turnus_file_path,  # Add this
                'df_file_path': turnus_set.df_file_path           # Add this
            }
        return None
    finally:
        session.close()

def get_turnus_set_by_id(turnus_set_id):
    """Get turnus set by ID"""
    session = get_db_session()
    try:
        turnus_set = session.query(TurnusSet).filter_by(id=turnus_set_id).first()
        if turnus_set:
            return {
                'id': turnus_set.id,
                'name': turnus_set.name,
                'year_identifier': turnus_set.year_identifier,
                'is_active': turnus_set.is_active,
                'created_at': turnus_set.created_at,
                'turnus_file_path': turnus_set.turnus_file_path,
                'df_file_path': turnus_set.df_file_path
            }
        return None
    finally:
        session.close()


def set_active_turnus_set(turnus_set_id):
    """Switch which turnus set is currently active"""
    session = get_db_session()
    try:
        # First, make all sets inactive
        session.query(TurnusSet).update({'is_active': 0})
        
        # Then activate the specified set
        turnus_set = session.query(TurnusSet).filter_by(id=turnus_set_id).first()
        if not turnus_set:
            return False, "Turnussett ikke funnet"

        turnus_set.is_active = 1
        session.commit()
        return True, f"Turnussett {turnus_set.year_identifier} er nå aktivt"
    except Exception as e:
        session.rollback()
        return False, f"Error setting active turnus set: {e}"
    finally:
        session.close()       

def get_active_turnus_set():
    """Get the currently active turnus set"""
    session = get_db_session()
    try:
        active_set = session.query(TurnusSet).filter_by(is_active=1).first()
        if active_set:
            return {
                'id': active_set.id,
                'name': active_set.name,
                'year_identifier': active_set.year_identifier,
                'is_active': active_set.is_active,
                'created_at': active_set.created_at,
                'turnus_file_path': active_set.turnus_file_path,
                'df_file_path': active_set.df_file_path
            }
        return None
    finally:
        session.close()

def add_shifts_to_turnus_set(file_path, turnus_set_id):
    """Load shifts from a JSON file into a specific turnus set"""
    session = get_db_session()
    try:
        with open(file_path, 'r') as f:
            turnus_data = json.load(f)
        
        # Extract shift names from the JSON structure
        for x in turnus_data:
            for name in x.keys():
                # Check if this shift already exists in this turnus set
                existing = session.query(Shifts).filter_by(
                    title=name, 
                    turnus_set_id=turnus_set_id
                ).first()
                if not existing:
                    new_shift = Shifts(title=name, turnus_set_id=turnus_set_id)
                    session.add(new_shift)
        
        session.commit()
        logger.info("Shifts added to turnus set %s successfully", turnus_set_id)
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error adding shifts to turnus set: %s", e)
        return False
    finally:
        session.close()

def get_shifts_by_turnus_set(turnus_set_id):
    """Get all shift names for a specific turnus set"""
    session = get_db_session()
    try:
        shifts = session.query(Shifts).filter_by(turnus_set_id=turnus_set_id).all()
        return [shift.title for shift in shifts]
    finally:
        session.close()

def delete_turnus_set(turnus_set_id):
    """Delete a turnus set and all its associated data"""
    session = get_db_session()
    try:
        turnus_set = session.query(TurnusSet).filter_by(id=turnus_set_id).first()
        if not turnus_set:
            return False, "Turnussett ikke funnet"

        # Delete all shifts belonging to this turnus set
        session.query(Shifts).filter_by(turnus_set_id=turnus_set_id).delete()

        # Delete all favorites belonging to this turnus set
        session.query(Favorites).filter_by(turnus_set_id=turnus_set_id).delete()

        # Delete the turnus set itself
        session.delete(turnus_set)
        session.commit()
        return True, f"Turnussett {turnus_set.year_identifier} slettet"
    except Exception as e:
        session.rollback()
        return False, f"Error deleting turnus set: {e}"
    finally:
        session.close()


def update_turnus_set_paths(turnus_set_id, turnus_file_path, df_file_path):
    """Update file paths for an existing turnus set"""
    session = get_db_session()
    try:
        turnus_set = session.query(TurnusSet).filter_by(id=turnus_set_id).first()
        if not turnus_set:
            return False, "Turnussett ikke funnet"

        turnus_set.turnus_file_path = turnus_file_path
        turnus_set.df_file_path = df_file_path
        session.commit()
        return True, "Filstier oppdatert"
    except Exception as e:
        session.rollback()
        return False, f"Error updating file paths: {e}"
    finally:
        session.close()

def refresh_turnus_set_shifts(turnus_set_id, json_file_path):
    """Re-sync shift names from a new JSON file into the database.

    Matches old names to new names by prefix to preserve favorites.
    Returns a summary dict: {renamed: [...], added: [...], removed: [...], unchanged: [...]}
    """
    session = get_db_session()
    try:
        # Load old shift names from DB
        old_shifts = session.query(Shifts).filter_by(turnus_set_id=turnus_set_id).all()
        old_names = set(s.title for s in old_shifts)

        # Load new shift names from JSON
        with open(json_file_path, 'r') as f:
            turnus_data = json.load(f)
        new_names = set()
        for entry in turnus_data:
            for name in entry.keys():
                new_names.add(name)

        # Find exact matches (unchanged)
        unchanged = old_names & new_names
        unmatched_old = old_names - unchanged
        unmatched_new = new_names - unchanged

        # Build rename map by prefix matching
        rename_map = {}
        matched_new = set()
        for old_name in list(unmatched_old):
            candidates = [n for n in unmatched_new if n.startswith(old_name) or old_name.startswith(n)]
            if len(candidates) == 1:
                rename_map[old_name] = candidates[0]
                matched_new.add(candidates[0])

        # Names not matched at all
        removed = unmatched_old - set(rename_map.keys())
        added = unmatched_new - matched_new

        # Apply changes in a single transaction
        # 1. Renames
        for old_name, new_name in rename_map.items():
            # Update shifts table
            session.query(Shifts).filter_by(
                title=old_name, turnus_set_id=turnus_set_id
            ).update({'title': new_name})
            # Update favorites table
            session.query(Favorites).filter_by(
                shift_title=old_name, turnus_set_id=turnus_set_id
            ).update({'shift_title': new_name})

        # 2. Delete orphaned shifts
        for name in removed:
            session.query(Shifts).filter_by(
                title=name, turnus_set_id=turnus_set_id
            ).delete()

        # 3. Add new shifts
        for name in added:
            session.add(Shifts(title=name, turnus_set_id=turnus_set_id))

        session.commit()

        return {
            'renamed': [{'old': k, 'new': v} for k, v in rename_map.items()],
            'added': sorted(added),
            'removed': sorted(removed),
            'unchanged': sorted(unchanged)
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

## TURNUSSET END ##


#### USER LOGIN AND REG ####
def hash_password(password):
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_pw.decode('utf-8')


def create_new_user(username, password, is_auth):
    session = get_db_session()
    try:
        new_user = DBUser(username=username, password=hash_password(password), is_auth=is_auth)
        session.add(new_user)
        session.commit()
        logger.info("User created")
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error creating user: %s", e)
        return False
    finally:
        session.close()

            
def get_user_data(username_or_email):
    """Get user data by username or email"""
    session = get_db_session()
    try:
        # Try to find by username first
        result = session.query(DBUser).filter_by(username=username_or_email).first()

        # If not found, try by email
        if not result:
            result = session.query(DBUser).filter_by(email=username_or_email.lower()).first()

        if result:
            data = {
                'id': result.id,
                'username': result.username,
                'password': result.password,
                'is_auth': result.is_auth,
                'email': result.email,
                'email_verified': result.email_verified
            }
            return data
        else:
            logger.warning("User not found: %s", username_or_email)
            return None
    finally:
        session.close()

def get_user_password(username):
    session = get_db_session()
    try:
        result = session.query(DBUser.password).filter_by(username=username).first()
        return result.password if result else None
    finally:
        session.close()



### FAVORITES ###

def get_favorite_lst(user_id, turnus_set_id=None):
    session = get_db_session()
    try:
        query = session.query(Favorites.shift_title).filter_by(user_id=user_id)
        
        if turnus_set_id:
            query = query.filter_by(turnus_set_id=turnus_set_id)
        else:
            active_set = get_active_turnus_set()
            if active_set:
                query = query.filter_by(turnus_set_id=active_set['id'])
            else:
                return []
        
        results = query.order_by(Favorites.order_index).all()
        
        # Handle duplicates by using set to get unique titles, then preserve order
        seen = set()
        shift_titles = []
        for result in results:
            if result.shift_title not in seen:
                seen.add(result.shift_title)
                shift_titles.append(result.shift_title)
        
        return shift_titles
    finally:
        session.close()


def user_has_favorites_in_other_sets(user_id, exclude_turnus_set_id):
    """Check if user has favorites in any turnus set other than the specified one."""
    session = get_db_session()
    try:
        return session.query(
            session.query(Favorites)
            .filter(Favorites.user_id == user_id)
            .filter(Favorites.turnus_set_id != exclude_turnus_set_id)
            .exists()
        ).scalar()
    finally:
        session.close()


def update_favorite_order(user_id, turnus_set_id=None):
    session = get_db_session()
    try:
        if not turnus_set_id:
            # Use active turnus set if none specified
            active_set = get_active_turnus_set()
            if not active_set:
                return False
            turnus_set_id = active_set['id']
        
        # Fetch the current order of the favorites FOR THE SPECIFIC TURNUS SET
        current_favorites = session.query(Favorites).filter_by(
            user_id=user_id, 
            turnus_set_id=turnus_set_id
        ).all()
        current_shift_titles = [favorite.shift_title for favorite in current_favorites]

        # Update current favorites order in database FOR THE SPECIFIC TURNUS SET
        for index, shift_title in enumerate(current_shift_titles):
            favorite = session.query(Favorites).filter_by(
                user_id=user_id, 
                shift_title=shift_title,
                turnus_set_id=turnus_set_id
            ).first()
            if favorite:
                favorite.order_index = index
        
        session.commit()
        logger.debug("Favorite order updated successfully")
        return True
    except Exception as e:
        session.rollback()
        logger.error("Failed to modify database. Changes only stored locally. Error = %s", e)
        return False
    finally:
        session.close()


def get_max_ordered_index(user_id, turnus_set_id=None):
    """Get the maximum order index for a user's favorites in a specific turnus set"""
    session = get_db_session()
    try:
        query = session.query(func.max(Favorites.order_index)).filter_by(user_id=user_id)
        
        if turnus_set_id:
            query = query.filter_by(turnus_set_id=turnus_set_id)
        else:
            # Use active turnus set if none specified
            active_set = get_active_turnus_set()
            if active_set:
                query = query.filter_by(turnus_set_id=active_set['id'])
        
        result = query.scalar()
        return result if result is not None else 0
    finally:
        session.close()

def cleanup_duplicate_favorites(session, user_id, shift_title, turnus_set_id):
    """Clean up duplicate favorites for a specific user/shift/turnus_set combination"""
    try:
        # Find all duplicates for this combination
        duplicates = session.query(Favorites).filter_by(
            user_id=user_id,
            shift_title=shift_title,
            turnus_set_id=turnus_set_id
        ).order_by(Favorites.order_index).all()
        
        if len(duplicates) > 1:
            # Keep the first one (lowest order_index), delete the rest
            keep_entry = duplicates[0]
            delete_entries = duplicates[1:]
            
            for entry in delete_entries:
                session.delete(entry)
            
            logger.info("Cleaned up %d duplicate favorites for user %s, shift '%s'", len(delete_entries), user_id, shift_title)
            
    except Exception as e:
        logger.error("Error cleaning up duplicates: %s", e)
        raise

def add_favorite(user_id, title, order_index, turnus_set_id=None):
    """Add a shift to user's favorites for a specific turnus set"""
    session = get_db_session()
    try:
        if not turnus_set_id:
            # Use active turnus set if none specified
            active_set = get_active_turnus_set()
            if not active_set:
                return False
            turnus_set_id = active_set['id']
        
        # Check if favorite already exists - handle multiple duplicates
        existing = session.query(Favorites).filter_by(
            user_id=user_id, 
            shift_title=title,
            turnus_set_id=turnus_set_id
        ).first()
        
        if existing:
            # If it already exists, clean up any duplicates and return success
            cleanup_duplicate_favorites(session, user_id, title, turnus_set_id)
            return True
        
        new_favorite = Favorites(
            user_id=user_id, 
            shift_title=title, 
            order_index=order_index,
            turnus_set_id=turnus_set_id
        )
        session.add(new_favorite)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error adding favorite: %s", e)
        return False
    finally:
        session.close()

def remove_favorite(user_id, title, turnus_set_id=None):
    """Remove a shift from user's favorites for a specific turnus set"""
    session = get_db_session()
    try:
        if not turnus_set_id:
            # Use active turnus set if none specified
            active_set = get_active_turnus_set()
            if not active_set:
                return False
            turnus_set_id = active_set['id']
        
        # Find ALL favorites for this combination (handle duplicates)
        favorites = session.query(Favorites).filter_by(
            user_id=user_id, 
            shift_title=title,
            turnus_set_id=turnus_set_id
        ).all()
        
        if favorites:
            # Delete all duplicates
            deleted_count = 0
            for favorite in favorites:
                session.delete(favorite)
                deleted_count += 1
            
            session.commit()
            if deleted_count > 1:
                logger.info("Removed %d duplicate favorites for user %s, shift '%s'", deleted_count, user_id, title)
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error("Error removing favorite: %s", e)
        return False
    finally:
        session.close()



### ADMIN FUNCTIONS ###
def get_all_users():
    """Get all users from the database"""
    session = get_db_session()
    try:
        users = session.query(DBUser).all()
        return [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'rullenummer': user.rullenummer,
                'is_auth': user.is_auth,
                'email_verified': user.email_verified,
                'created_at': user.created_at
            }
            for user in users
        ]
    finally:
        session.close()

def get_user_by_id(user_id):
    """Get a specific user by ID"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'rullenummer': user.rullenummer,
                'is_auth': user.is_auth
            }
        return None
    finally:
        session.close()

def create_user(username, password, is_auth=0):
    """Create a new user (admin-created users are auto-verified)"""
    session = get_db_session()
    try:
        # Check if username already exists
        existing_user = session.query(DBUser).filter_by(username=username).first()
        if existing_user:
            return False, "Brukernavnet finnes allerede"

        new_user = DBUser(
            username=username,
            email=username,  # Set email same as username
            password=hash_password(password),
            is_auth=is_auth,
            email_verified=1,  # Admin-created users are auto-verified
            created_at=func.now()
        )
        session.add(new_user)
        session.commit()
        return True, "Bruker opprettet"
    except Exception as e:
        session.rollback()
        return False, f"Error creating user: {e}"
    finally:
        session.close()

def update_user(user_id, username, email=None, rullenummer=None, password=None, is_auth=None):
    """Update an existing user"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "Bruker ikke funnet"

        # Check if new username conflicts with existing user
        if username != user.username:
            existing_user = session.query(DBUser).filter_by(username=username).first()
            if existing_user:
                return False, "Brukernavnet finnes allerede"

        # Check if new email conflicts with existing user
        if email and email != user.email:
            existing_email = session.query(DBUser).filter_by(email=email.lower()).first()
            if existing_email:
                return False, "E-postadressen finnes allerede"

        user.username = username
        if email is not None:
            user.email = email.lower()
        if rullenummer is not None:
            user.rullenummer = rullenummer
        if password:
            user.password = hash_password(password)
        if is_auth is not None:
            user.is_auth = is_auth

        session.commit()
        return True, "Bruker oppdatert"
    except Exception as e:
        session.rollback()
        return False, f"Error updating user: {e}"
    finally:
        session.close()

def delete_user(user_id):
    """Delete a user and all associated data"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "Bruker ikke funnet"

        # Delete associated favorites
        session.query(Favorites).filter_by(user_id=user_id).delete()

        # Delete the user
        session.delete(user)
        session.commit()
        return True, "Bruker slettet"
    except Exception as e:
        session.rollback()
        return False, f"Error deleting user: {e}"
    finally:
        session.close()

def toggle_user_auth(user_id):
    """Toggle user authentication status"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "Bruker ikke funnet"

        user.is_auth = 1 if user.is_auth == 0 else 0
        session.commit()
        return True, f"Administratorrettigheter {'aktivert' if user.is_auth == 1 else 'deaktivert'}"
    except Exception as e:
        session.rollback()
        return False, f"Error toggling user auth: {e}"
    finally:
        session.close()

def update_user_password(user_id, current_password, new_password):
    """Update user password with current password verification"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "Bruker ikke funnet"

        # Verify current password
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
            return False, "Nåværende passord er feil"

        # Update password
        user.password = hash_password(new_password)
        session.commit()
        return True, "Passord oppdatert"
    except Exception as e:
        session.rollback()
        return False, f"Error updating password: {e}"
    finally:
        session.close()

#### EMAIL VERIFICATION FUNCTIONS ####

def is_email_authorized(email, rullenummer=None):
    """Check if email and rullenummer combination is in authorized list"""
    session = get_db_session()
    try:
        if rullenummer:
            result = session.query(AuthorizedEmails).filter_by(
                email=email.lower(),
                rullenummer=rullenummer
            ).first()
        else:
            # For backwards compatibility if rullenummer not provided
            result = session.query(AuthorizedEmails).filter_by(email=email.lower()).first()
        return result is not None
    finally:
        session.close()

def add_authorized_email(email, added_by, notes='', rullenummer=None):
    """Add email and rullenummer to authorized list"""
    session = get_db_session()
    try:
        # Check if already exists (email + rullenummer combination)
        if rullenummer:
            existing = session.query(AuthorizedEmails).filter_by(
                email=email.lower(),
                rullenummer=rullenummer
            ).first()
        else:
            existing = session.query(AuthorizedEmails).filter_by(email=email.lower()).first()

        if existing:
            return False, "E-post og rullenummer-kombinasjonen finnes allerede i autorisert liste"

        new_email = AuthorizedEmails(
            email=email.lower(),
            rullenummer=rullenummer,
            added_by=added_by,
            notes=notes
        )
        session.add(new_email)
        session.commit()
        return True, "E-post lagt til i autorisert liste"
    except Exception as e:
        session.rollback()
        return False, f"Error adding email: {e}"
    finally:
        session.close()

def get_all_authorized_emails():
    """Get all authorized emails with additional info"""
    session = get_db_session()
    try:
        emails = session.query(AuthorizedEmails).order_by(AuthorizedEmails.added_at.desc()).all()
        result = []
        for email in emails:
            # Check if this email has registered
            user = session.query(DBUser).filter_by(email=email.email).first()

            # Get admin username who added this
            admin = session.query(DBUser).filter_by(id=email.added_by).first()

            result.append({
                'id': email.id,
                'email': email.email,
                'rullenummer': email.rullenummer,
                'added_by': email.added_by,
                'added_by_username': admin.username if admin else None,
                'added_at': email.added_at,
                'notes': email.notes,
                'is_registered': user is not None
            })
        return result
    finally:
        session.close()

def delete_authorized_email(email_id):
    """Remove email from authorized list"""
    session = get_db_session()
    try:
        email = session.query(AuthorizedEmails).filter_by(id=email_id).first()
        if not email:
            return False, "E-post ikke funnet"

        session.delete(email)
        session.commit()
        return True, "E-post fjernet fra autorisert liste"
    except Exception as e:
        session.rollback()
        return False, f"Error removing email: {e}"
    finally:
        session.close()

def create_user_with_email(email, username, password, verified=False, rullenummer=None):
    """Create user account with email (for self-registration)

    Args:
        email: User's email address (used for login)
        username: User's chosen display name
        password: User's password
        verified: Whether email is pre-verified
        rullenummer: User's work ID
    """
    session = get_db_session()
    try:
        # Check if email already exists
        existing_email = session.query(DBUser).filter_by(email=email.lower()).first()
        if existing_email:
            return False, "E-postadressen er allerede registrert", None

        # Check if username already taken
        existing_username = session.query(DBUser).filter_by(username=username).first()
        if existing_username:
            return False, "Brukernavnet er allerede tatt", None

        new_user = DBUser(
            username=username,
            email=email.lower(),
            password=hash_password(password),
            rullenummer=rullenummer,
            is_auth=0,
            email_verified=1 if verified else 0,
            created_at=func.now()
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return True, "Bruker opprettet", new_user.id
    except Exception as e:
        session.rollback()
        return False, f"Error creating user: {e}", None
    finally:
        session.close()

def get_user_by_email(email):
    """Get user by email address"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(email=email.lower()).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'email_verified': user.email_verified,
                'is_auth': user.is_auth,
                'created_at': user.created_at,
                'password': user.password
            }
        return None
    finally:
        session.close()

def get_user_by_username(username):
    """Get user by username"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(username=username).first()
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'email_verified': user.email_verified,
                'is_auth': user.is_auth
            }
        return None
    finally:
        session.close()

def create_verification_token(user_id, token):
    """Create email verification token"""
    session = get_db_session()
    try:
        expiry_hours = AppConfig.CONFIG.getint('verification', 'token_expiry_hours', fallback=48)
        expires_at = datetime.now() + timedelta(hours=expiry_hours)

        # Invalidate old tokens
        session.query(EmailVerificationToken).filter_by(
            user_id=user_id,
            used=0
        ).update({'used': 1})

        new_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        session.add(new_token)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error creating token: %s", e)
        return False
    finally:
        session.close()

def verify_token(token):
    """Verify email verification token and mark user as verified"""
    session = get_db_session()
    try:
        token_record = session.query(EmailVerificationToken).filter_by(
            token=token,
            used=0
        ).first()

        if not token_record:
            return {'success': False, 'message': 'Ugyldig eller allerede brukt verifiseringslenke'}

        # Check expiration
        if token_record.expires_at < datetime.now():
            return {'success': False, 'message': 'Verifiseringslenken har utløpt. Vennligst be om en ny.'}

        # Mark token as used
        token_record.used = 1

        # Mark user as verified
        user = session.query(DBUser).filter_by(id=token_record.user_id).first()
        if user:
            user.email_verified = 1
            session.commit()

            return {'success': True, 'message': 'E-post verifisert', 'email': user.email}
        else:
            return {'success': False, 'message': 'Bruker ikke funnet'}

    except Exception as e:
        session.rollback()
        logger.error("Error verifying token: %s", e)
        return {'success': False, 'message': 'En feil oppstod under verifisering'}
    finally:
        session.close()

def can_send_verification_email(user_id):
    """Check rate limiting for verification emails"""
    session = get_db_session()
    try:
        max_per_day = AppConfig.CONFIG.getint('verification', 'max_verification_emails_per_day', fallback=3)

        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False

        # Check last sent time (minimum 1 hour between sends)
        if user.verification_sent_at:
            time_since_last = datetime.now() - user.verification_sent_at
            if time_since_last < timedelta(hours=1):
                return False

        # Check count in last 24 hours
        count = session.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.created_at >= datetime.now() - timedelta(days=1)
        ).count()

        return count < max_per_day
    finally:
        session.close()

def update_verification_sent_time(email):
    """Update timestamp when verification email was sent"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(email=email.lower()).first()
        if user:
            user.verification_sent_at = datetime.now()
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Error updating verification sent time: %s", e)
    finally:
        session.close()


#### PASSWORD RESET FUNCTIONS ####

def create_password_reset_token(user_id, token):
    """Create password reset token with 1 hour expiry"""
    session = get_db_session()
    try:
        expires_at = datetime.now() + timedelta(hours=1)

        # Invalidate old password reset tokens for this user
        session.query(EmailVerificationToken).filter_by(
            user_id=user_id,
            token_type='password_reset',
            used=0
        ).update({'used': 1})

        new_token = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            token_type='password_reset'
        )
        session.add(new_token)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error("Error creating password reset token: %s", e)
        return False
    finally:
        session.close()


def verify_password_reset_token(token):
    """Verify password reset token and return user info if valid"""
    session = get_db_session()
    try:
        token_record = session.query(EmailVerificationToken).filter_by(
            token=token,
            token_type='password_reset',
            used=0
        ).first()

        if not token_record:
            return {'success': False, 'message': 'Ugyldig eller allerede brukt tilbakestillingslenke'}

        # Check expiration
        if token_record.expires_at < datetime.now():
            return {'success': False, 'message': 'Tilbakestillingslenken har utløpt. Vennligst be om en ny.'}

        # Get user info
        user = session.query(DBUser).filter_by(id=token_record.user_id).first()
        if user:
            return {
                'success': True,
                'user_id': user.id,
                'email': user.email,
                'username': user.username
            }
        else:
            return {'success': False, 'message': 'Bruker ikke funnet'}

    except Exception as e:
        logger.error("Error verifying password reset token: %s", e)
        return {'success': False, 'message': 'En feil oppstod under verifisering'}
    finally:
        session.close()


def reset_user_password(user_id, new_password):
    """Update user password and mark reset token as used"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(id=user_id).first()
        if not user:
            return False, "Bruker ikke funnet"

        # Update password
        user.password = hash_password(new_password)

        # Mark all password reset tokens for this user as used
        session.query(EmailVerificationToken).filter_by(
            user_id=user_id,
            token_type='password_reset',
            used=0
        ).update({'used': 1})

        session.commit()
        return True, "Passord oppdatert"
    except Exception as e:
        session.rollback()
        return False, f"Error updating password: {e}"
    finally:
        session.close()


def can_send_password_reset_email(email):
    """Check rate limiting for password reset emails (1 per hour per email)"""
    session = get_db_session()
    try:
        user = session.query(DBUser).filter_by(email=email.lower()).first()
        if not user:
            # Return True to avoid email enumeration
            # (caller will show generic success message)
            return True

        # Check if a password reset token was created in the last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_token = session.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.token_type == 'password_reset',
            EmailVerificationToken.created_at >= one_hour_ago
        ).first()

        return recent_token is None
    finally:
        session.close()


if __name__ == '__main__':
    create_new_user('testuser', 'testuser', 0)
 

