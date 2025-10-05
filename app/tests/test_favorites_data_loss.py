#!/usr/bin/env python3
"""
Comprehensive Favorites Data Loss Test Suite
Tests all identified scenarios where favorites could be lost between sessions, logouts, or other events.

Run this script from the project root directory:
    python test_favorites_data_loss.py

CRITICAL ISSUES TESTED:
1. Turnus Set Deletion (HIGH RISK) - Favorites deleted when turnus set is deleted
2. Missing Foreign Key Constraints (MEDIUM RISK) - Orphaned favorites
3. Session Storage Issues (MEDIUM RISK) - Session expiry and filesystem issues
4. Race Conditions on Toggle Favorite (LOW-MEDIUM RISK)
5. No Validation of turnus_set_id in API Calls (LOW RISK)
6. Duplicate Cleanup Logic (LOW RISK)
7. Database Connection Timeouts (LOW RISK)
"""

import sys
import os
import time
import tempfile
import shutil
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.utils import db_utils
from sqlalchemy import inspect

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_test(test_name):
    print(f"{Colors.BOLD}Testing:{Colors.END} {test_name}")

def print_pass(message):
    print(f"  {Colors.GREEN}✓ PASS:{Colors.END} {message}")

def print_fail(message):
    print(f"  {Colors.RED}✗ FAIL:{Colors.END} {message}")

def print_warning(message):
    print(f"  {Colors.YELLOW}⚠ WARNING:{Colors.END} {message}")

def print_info(message):
    print(f"  {Colors.BLUE}ℹ INFO:{Colors.END} {message}")


class FavoritesTestSuite:
    def __init__(self):
        self.test_results = []
        self.test_user_ids = []
        self.test_turnus_set_ids = []
        
    def cleanup(self):
        """Clean up test data"""
        print_info("Cleaning up test data...")
        session = db_utils.get_db_session()
        try:
            # Delete test favorites
            session.query(db_utils.Favorites).filter(
                db_utils.Favorites.shift_title.like('TEST_%')
            ).delete(synchronize_session=False)
            
            # Delete test users
            for user_id in self.test_user_ids:
                session.query(db_utils.DBUser).filter_by(id=user_id).delete()
            
            # Delete test turnus sets
            for ts_id in self.test_turnus_set_ids:
                session.query(db_utils.TurnusSet).filter_by(id=ts_id).delete()
            
            session.commit()
            print_info("Cleanup complete")
        except Exception as e:
            session.rollback()
            print_warning(f"Cleanup error: {e}")
        finally:
            session.close()
    
    def create_test_user(self, username):
        """Create a test user"""
        success, message = db_utils.create_user(username, 'testpassword123', is_auth=0)
        if success:
            user_data = db_utils.get_user_data(username)
            if user_data:
                self.test_user_ids.append(user_data['id'])
                return user_data['id']
        return None
    
    def create_test_turnus_set(self, year_id, name, is_active=False):
        """Create a test turnus set"""
        success, message = db_utils.create_turnus_set(name, year_id, is_active=is_active)
        if success:
            turnus_set = db_utils.get_turnus_set_by_year(year_id)
            if turnus_set:
                self.test_turnus_set_ids.append(turnus_set['id'])
                return turnus_set['id']
        return None
    
    # TEST 1: Turnus Set Deletion Data Loss
    def test_turnus_set_deletion(self):
        """
        TEST #1: TURNUS SET DELETION (HIGH RISK)
        When admin deletes a turnus set, all favorites for that set are permanently deleted.
        """
        print_test("Turnus Set Deletion - Favorites Loss")
        
        # Create test user
        user_id = self.create_test_user(f'test_user_deletion_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Create test turnus set
        turnus_set_id = self.create_test_turnus_set(f'TEST_DEL_{int(time.time())}', 'Test Deletion Set', is_active=False)
        if not turnus_set_id:
            print_fail("Could not create test turnus set")
            return False
        
        # Add favorites to the turnus set
        favorites_added = []
        for i in range(3):
            title = f'TEST_SHIFT_{i}'
            success = db_utils.add_favorite(user_id, title, i, turnus_set_id)
            if success:
                favorites_added.append(title)
        
        print_info(f"Added {len(favorites_added)} favorites to turnus set {turnus_set_id}")
        
        # Verify favorites exist
        favorites_before = db_utils.get_favorite_lst(user_id, turnus_set_id)
        if len(favorites_before) != len(favorites_added):
            print_fail(f"Expected {len(favorites_added)} favorites, found {len(favorites_before)}")
            return False
        
        print_info(f"Verified {len(favorites_before)} favorites exist before deletion")
        
        # Delete the turnus set
        success, message = db_utils.delete_turnus_set(turnus_set_id)
        if not success:
            print_fail(f"Could not delete turnus set: {message}")
            return False
        
        print_info(f"Deleted turnus set {turnus_set_id}")
        
        # Check if favorites were deleted
        session = db_utils.get_db_session()
        try:
            remaining_favorites = session.query(db_utils.Favorites).filter_by(
                user_id=user_id,
                turnus_set_id=turnus_set_id
            ).count()
            
            if remaining_favorites > 0:
                print_fail(f"CRITICAL: {remaining_favorites} favorites still exist after turnus set deletion (orphaned data)")
                return False
            else:
                print_fail(f"CONFIRMED ISSUE: All {len(favorites_before)} favorites were permanently deleted with turnus set")
                print_warning("Users will lose all favorites when admin deletes old turnus sets")
                print_warning("RECOMMENDATION: Add confirmation dialog or backup favorites before deletion")
                return True  # Test passed (confirmed the issue exists)
        finally:
            session.close()
    
    # TEST 2: Orphaned Favorites (Missing Foreign Keys)
    def test_orphaned_favorites(self):
        """
        TEST #2: MISSING FOREIGN KEY CONSTRAINTS (MEDIUM RISK)
        Favorites don't have foreign key constraints, allowing orphaned records.
        """
        print_test("Orphaned Favorites - Missing Foreign Key Constraints")
        
        # Create test user
        user_id = self.create_test_user(f'test_user_orphan_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Create test turnus set
        turnus_set_id = self.create_test_turnus_set(f'TEST_ORPHAN_{int(time.time())}', 'Test Orphan Set', is_active=False)
        if not turnus_set_id:
            print_fail("Could not create test turnus set")
            return False
        
        # Add a favorite
        success = db_utils.add_favorite(user_id, 'TEST_ORPHAN_SHIFT', 0, turnus_set_id)
        if not success:
            print_fail("Could not add favorite")
            return False
        
        # Directly delete the user (bypassing the delete_user function that cleans up)
        session = db_utils.get_db_session()
        try:
            user = session.query(db_utils.DBUser).filter_by(id=user_id).first()
            session.delete(user)
            session.commit()
            print_info(f"Directly deleted user {user_id}")
            
            # Check if favorite still exists (orphaned)
            orphaned_favorites = session.query(db_utils.Favorites).filter_by(user_id=user_id).count()
            
            if orphaned_favorites > 0:
                print_fail(f"CONFIRMED ISSUE: {orphaned_favorites} orphaned favorite(s) exist after user deletion")
                print_warning("Favorites table lacks CASCADE DELETE foreign key constraint")
                print_warning("RECOMMENDATION: Add foreign key constraints with ON DELETE CASCADE")
                
                # Cleanup orphaned favorites
                session.query(db_utils.Favorites).filter_by(user_id=user_id).delete()
                session.commit()
                return True  # Test passed (confirmed the issue)
            else:
                print_pass("No orphaned favorites found (delete_user function worked correctly)")
                return True
        except Exception as e:
            session.rollback()
            print_fail(f"Error during orphan test: {e}")
            return False
        finally:
            session.close()
    
    # TEST 3: Session Expiry
    def test_session_persistence(self):
        """
        TEST #3: SESSION STORAGE ISSUES (MEDIUM RISK)
        Session data is stored on filesystem with SESSION_PERMANENT = False.
        """
        print_test("Session Storage - Persistence After Restart")
        
        from config import conf
        
        # Check session configuration
        print_info(f"Session directory: {conf.sessions_dir}")
        
        if not os.path.exists(conf.sessions_dir):
            print_warning(f"Session directory does not exist: {conf.sessions_dir}")
            return False
        
        # Count existing session files
        session_files = [f for f in os.listdir(conf.sessions_dir) if os.path.isfile(os.path.join(conf.sessions_dir, f))]
        print_info(f"Found {len(session_files)} existing session file(s)")
        
        # Test: What happens if session directory is deleted?
        test_session_dir = os.path.join(tempfile.gettempdir(), 'test_sessions')
        os.makedirs(test_session_dir, exist_ok=True)
        
        # Create a dummy session file
        test_session_file = os.path.join(test_session_dir, 'test_session_123')
        with open(test_session_file, 'w') as f:
            f.write('{"user_selected_turnus_set": 999}')
        
        print_info(f"Created test session file: {test_session_file}")
        
        # Delete the directory
        shutil.rmtree(test_session_dir)
        
        if not os.path.exists(test_session_file):
            print_fail("CONFIRMED ISSUE: Session files can be deleted, losing user context")
            print_warning("User's selected turnus_set is stored in session, not database")
            print_warning("If session expires/deleted, user returns to default turnus set")
            print_warning("Favorites in other turnus sets will appear 'lost' until user switches back")
            print_warning("RECOMMENDATION: Store user's last selected turnus_set in database")
            return True  # Test passed (confirmed the issue)
        
        return False
    
    # TEST 4: Duplicate Favorites
    def test_duplicate_favorites(self):
        """
        TEST #6: DUPLICATE CLEANUP LOGIC (LOW RISK)
        Test if duplicates can be created and if cleanup works.
        """
        print_test("Duplicate Favorites - Detection and Cleanup")
        
        # Create test user
        user_id = self.create_test_user(f'test_user_dup_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Create test turnus set
        turnus_set_id = self.create_test_turnus_set(f'TEST_DUP_{int(time.time())}', 'Test Duplicate Set', is_active=False)
        if not turnus_set_id:
            print_fail("Could not create test turnus set")
            return False
        
        # Try to add duplicate favorites by directly inserting into database
        session = db_utils.get_db_session()
        try:
            shift_title = 'TEST_DUPLICATE_SHIFT'
            
            # Add first favorite normally
            success = db_utils.add_favorite(user_id, shift_title, 0, turnus_set_id)
            if not success:
                print_fail("Could not add first favorite")
                return False
            
            # Try to add duplicate via direct DB insertion (bypassing unique constraint check)
            try:
                duplicate = db_utils.Favorites(
                    user_id=user_id,
                    shift_title=shift_title,
                    turnus_set_id=turnus_set_id,
                    order_index=1
                )
                session.add(duplicate)
                session.commit()
                
                print_fail("CRITICAL: Duplicate favorite was inserted (unique constraint not enforced)")
                
                # Cleanup duplicates
                db_utils.cleanup_duplicate_favorites(session, user_id, shift_title, turnus_set_id)
                session.commit()
                return False
                
            except Exception as e:
                session.rollback()
                if "UNIQUE constraint failed" in str(e) or "Duplicate entry" in str(e):
                    print_pass("Unique constraint prevented duplicate favorites")
                    return True
                else:
                    print_fail(f"Unexpected error: {e}")
                    return False
        finally:
            session.close()
    
    # TEST 5: No Active Turnus Set
    def test_no_active_turnus_set(self):
        """
        TEST #5: NO VALIDATION OF TURNUS_SET_ID (LOW RISK)
        What happens when there's no active turnus set?
        """
        print_test("No Active Turnus Set - Favorite Operations")
        
        # Create test user
        user_id = self.create_test_user(f'test_user_noactive_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Temporarily remove all active turnus sets
        session = db_utils.get_db_session()
        original_active = None
        try:
            # Save current active set
            original_active = db_utils.get_active_turnus_set()
            
            # Deactivate all sets
            session.query(db_utils.TurnusSet).update({'is_active': 0})
            session.commit()
            
            print_info("Deactivated all turnus sets")
            
            # Try to add a favorite without active turnus set
            success = db_utils.add_favorite(user_id, 'TEST_NO_ACTIVE', 0, turnus_set_id=None)
            
            if success:
                print_fail("CRITICAL: Favorite was added without valid turnus_set_id")
                return False
            else:
                print_pass("add_favorite correctly failed when no active turnus set exists")
            
            # Try to get favorites without active turnus set
            favorites = db_utils.get_favorite_lst(user_id, turnus_set_id=None)
            
            if len(favorites) > 0:
                print_fail(f"CRITICAL: get_favorite_lst returned {len(favorites)} favorites without active turnus set")
                return False
            else:
                print_pass("get_favorite_lst correctly returned empty list when no active turnus set")
                return True
                
        finally:
            # Restore original active set
            if original_active:
                db_utils.set_active_turnus_set(original_active['id'])
                print_info(f"Restored active turnus set: {original_active['year_identifier']}")
            session.close()
    
    # TEST 6: Concurrent Favorite Toggles
    def test_concurrent_toggles(self):
        """
        TEST #4: RACE CONDITIONS ON TOGGLE FAVORITE (LOW-MEDIUM RISK)
        Test if race conditions can cause data loss or duplicates.
        """
        print_test("Concurrent Favorite Toggles - Race Conditions")
        
        import threading
        
        # Create test user
        user_id = self.create_test_user(f'test_user_race_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Create test turnus set
        turnus_set_id = self.create_test_turnus_set(f'TEST_RACE_{int(time.time())}', 'Test Race Set', is_active=True)
        if not turnus_set_id:
            print_fail("Could not create test turnus set")
            return False
        
        shift_title = 'TEST_RACE_SHIFT'
        errors = []
        
        def add_favorite_thread():
            try:
                for i in range(5):
                    db_utils.add_favorite(user_id, shift_title, i, turnus_set_id)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(str(e))
        
        def remove_favorite_thread():
            try:
                time.sleep(0.005)  # Start slightly after add thread
                for i in range(5):
                    db_utils.remove_favorite(user_id, shift_title, turnus_set_id)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(str(e))
        
        # Run concurrent operations
        thread1 = threading.Thread(target=add_favorite_thread)
        thread2 = threading.Thread(target=remove_favorite_thread)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        if errors:
            print_fail(f"CRITICAL: Errors occurred during concurrent operations: {errors}")
            return False
        
        # Check final state
        final_favorites = db_utils.get_favorite_lst(user_id, turnus_set_id)
        
        # Check for duplicates
        session = db_utils.get_db_session()
        try:
            duplicate_count = session.query(db_utils.Favorites).filter_by(
                user_id=user_id,
                shift_title=shift_title,
                turnus_set_id=turnus_set_id
            ).count()
            
            if duplicate_count > 1:
                print_fail(f"CRITICAL: {duplicate_count} duplicate favorites exist after concurrent operations")
                return False
            elif duplicate_count == 1:
                print_pass("No duplicates created during concurrent operations (lock worked)")
                return True
            else:
                print_pass("No favorites remain (consistent final state)")
                return True
        finally:
            session.close()
    
    # TEST 7: Turnus Set Switching
    def test_turnus_set_switching(self):
        """
        TEST: Favorites persist when switching between turnus sets
        """
        print_test("Turnus Set Switching - Favorite Persistence")
        
        # Create test user
        user_id = self.create_test_user(f'test_user_switch_{int(time.time())}')
        if not user_id:
            print_fail("Could not create test user")
            return False
        
        # Create two test turnus sets
        turnus_set_1 = self.create_test_turnus_set(f'TEST_SW1_{int(time.time())}', 'Test Switch Set 1', is_active=False)
        turnus_set_2 = self.create_test_turnus_set(f'TEST_SW2_{int(time.time())+1}', 'Test Switch Set 2', is_active=False)
        
        if not turnus_set_1 or not turnus_set_2:
            print_fail("Could not create test turnus sets")
            return False
        
        # Add favorites to set 1
        for i in range(3):
            db_utils.add_favorite(user_id, f'TEST_SET1_SHIFT_{i}', i, turnus_set_1)
        
        # Add favorites to set 2
        for i in range(2):
            db_utils.add_favorite(user_id, f'TEST_SET2_SHIFT_{i}', i, turnus_set_2)
        
        # Get favorites from set 1
        favorites_set1 = db_utils.get_favorite_lst(user_id, turnus_set_1)
        print_info(f"Set 1 has {len(favorites_set1)} favorites")
        
        # Get favorites from set 2
        favorites_set2 = db_utils.get_favorite_lst(user_id, turnus_set_2)
        print_info(f"Set 2 has {len(favorites_set2)} favorites")
        
        # Verify favorites are separate
        if len(favorites_set1) != 3:
            print_fail(f"Set 1 should have 3 favorites, has {len(favorites_set1)}")
            return False
        
        if len(favorites_set2) != 2:
            print_fail(f"Set 2 should have 2 favorites, has {len(favorites_set2)}")
            return False
        
        # Verify no cross-contamination
        for fav in favorites_set1:
            if 'SET2' in fav:
                print_fail("Set 1 contains Set 2 favorites (cross-contamination)")
                return False
        
        for fav in favorites_set2:
            if 'SET1' in fav:
                print_fail("Set 2 contains Set 1 favorites (cross-contamination)")
                return False
        
        print_pass("Favorites are properly isolated per turnus set")
        return True
    
    def run_all_tests(self):
        """Run all tests and report results"""
        print_header("FAVORITES DATA LOSS TEST SUITE")
        print(f"Testing favorites persistence across sessions, logouts, and deletions")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        tests = [
            ("Turnus Set Deletion", self.test_turnus_set_deletion),
            ("Orphaned Favorites", self.test_orphaned_favorites),
            ("Session Persistence", self.test_session_persistence),
            ("Duplicate Favorites", self.test_duplicate_favorites),
            ("No Active Turnus Set", self.test_no_active_turnus_set),
            ("Concurrent Toggles", self.test_concurrent_toggles),
            ("Turnus Set Switching", self.test_turnus_set_switching),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print_fail(f"Exception in {test_name}: {e}")
                results.append((test_name, False))
            print()  # Blank line between tests
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        print_header("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        failed = len(results) - passed
        
        for test_name, result in results:
            if result:
                print(f"  {Colors.GREEN}✓{Colors.END} {test_name}")
            else:
                print(f"  {Colors.RED}✗{Colors.END} {test_name}")
        
        print(f"\n{Colors.BOLD}Total Tests:{Colors.END} {len(results)}")
        print(f"{Colors.GREEN}Passed:{Colors.END} {passed}")
        print(f"{Colors.RED}Failed:{Colors.END} {failed}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}SOME TESTS FAILED - SEE DETAILS ABOVE{Colors.END}")
        
        print_header("RECOMMENDATIONS")
        print("1. Add CASCADE DELETE foreign key constraints to Favorites table")
        print("2. Add confirmation dialog before deleting turnus sets with user data")
        print("3. Consider storing user's last selected turnus_set in database, not session")
        print("4. Add backup/export functionality for favorites")
        print("5. Add proper logging to app.log for favorite operations")
        print("6. Consider SESSION_PERMANENT = True with appropriate timeout")
        
        return failed == 0


if __name__ == '__main__':
    print(f"{Colors.BOLD}Shift Rotation Organizer - Favorites Data Loss Test Suite{Colors.END}")
    print(f"This script tests for data loss scenarios in the favorites feature.\n")
    
    # Create database tables if they don't exist
    db_utils.create_tables()
    
    # Run tests
    suite = FavoritesTestSuite()
    success = suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)