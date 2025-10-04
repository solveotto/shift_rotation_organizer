# Favorites Hibernation Bug Fix

## Problem
Users were experiencing favorites disappearing after PC hibernation. Investigation revealed:
1. Duplicate entries in the favorites database table
2. Race conditions during hibernation causing duplicate API requests
3. Application not handling duplicates gracefully

## Root Cause
The hibernation bug was caused by:
1. **Race conditions**: When a PC hibernates during a favorite toggle request, the browser may retry or duplicate the request
2. **Duplicate database entries**: Despite having a unique constraint, duplicates existed in the database
3. **Poor duplicate handling**: The application didn't gracefully handle existing duplicates

## Solution Implemented

### 1. Database Cleanup Utility (`app/utils/cleanup_duplicates.py`)
- Identifies and removes duplicate favorites
- Keeps the entry with the lowest `order_index`
- Provides dry-run functionality for safety
- Reorders favorites to have sequential order_index values

### 2. Improved Database Functions (`app/utils/db_utils.py`)

#### `get_favorite_lst()` - Enhanced
- Now handles duplicates gracefully by deduplicating results
- Preserves order while removing duplicates
- Ensures consistent favorites display

#### `add_favorite()` - Enhanced  
- Detects existing favorites and cleans up duplicates automatically
- Returns success for already-existing favorites (idempotent)
- Better error handling and logging

#### `remove_favorite()` - Enhanced
- Removes ALL duplicates when removing a favorite
- Handles multiple entries for the same user/shift combination
- Better error handling

#### `cleanup_duplicate_favorites()` - New
- Internal function to clean up duplicates for specific user/shift combinations
- Called automatically when duplicates are detected

### 3. Improved API Endpoint (`app/routes/api.py`)

#### `toggle_favorite()` - Enhanced
- Better input validation
- Checks existing state before making changes (idempotent operations)
- Handles race conditions gracefully
- More descriptive error messages
- Prevents unnecessary database operations

### 4. Easy Cleanup Script (`run_cleanup.py`)
- Simple script to run the database cleanup
- Can be executed from the project root

## How to Apply the Fix

### Step 1: Clean Existing Duplicates
```bash
# From project root
python run_cleanup.py
```

Or run the full cleanup utility:
```bash
python app/utils/cleanup_duplicates.py
```

### Step 2: Deploy Code Changes
The improved code is already in place and will:
- Handle existing duplicates gracefully
- Prevent new duplicates from causing issues
- Make the favorites system more robust against hibernation

## Testing the Fix

### Test Cases
1. **Normal operation**: Add/remove favorites works as before
2. **Duplicate handling**: Existing duplicates are handled gracefully
3. **Hibernation simulation**: Rapid toggle requests don't create duplicates
4. **Race conditions**: Multiple simultaneous requests are handled safely

### Verification
- Check database for duplicate entries: `SELECT * FROM favorites WHERE turnus_set_id=4 GROUP BY user_id, shift_title, turnus_set_id HAVING COUNT(*) > 1;`
- Verify favorites display correctly in the application
- Test rapid favorite toggling

## Prevention
The fix prevents future hibernation issues by:
1. **Idempotent operations**: Multiple requests for the same action are safe
2. **Duplicate detection**: Automatic cleanup of duplicates
3. **Better error handling**: Graceful handling of edge cases
4. **Input validation**: Prevents invalid requests from causing issues

## Files Modified
- `app/utils/db_utils.py` - Enhanced favorites management
- `app/routes/api.py` - Improved API endpoint
- `app/utils/cleanup_duplicates.py` - New cleanup utility
- `run_cleanup.py` - Simple cleanup script

## Database Impact
- Removes duplicate entries
- Reorders favorites to have sequential order_index values
- No data loss (keeps the first occurrence of each favorite)
- Improves database integrity

The favorites system is now robust against hibernation-related issues and will maintain data integrity even under race conditions.
