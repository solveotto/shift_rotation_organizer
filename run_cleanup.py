#!/usr/bin/env python3
"""
Simple script to run the favorites cleanup utility
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.utils.cleanup_duplicates import cleanup_duplicates, find_duplicates

if __name__ == "__main__":
    print("Running favorites cleanup...")
    
    # Run the cleanup
    duplicates = find_duplicates()
    if duplicates:
        print(f"Found {len(duplicates)} sets of duplicates")
        cleanup_duplicates(dry_run=False)
    else:
        print("No duplicates found!")
