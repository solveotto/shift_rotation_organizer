#!/usr/bin/env python3
"""
Annual turnus creation script with flexible file organization
Usage: python create_new_turnus_year.py R26 "OSL Train Shifts 2026" path/to/turnuser_R26.pdf [--turnusfiler]
"""

import sys
import os
import time
import argparse

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now we can import from app
from app.utils.shiftscraper import ShiftScraper
from app.utils.db_utils import create_turnus_set, add_shifts_to_turnus_set, get_turnus_set_by_year, update_turnus_set_paths
from app.utils.shift_stats import Turnus
from config import conf

def create_new_turnus(year_id, name, pdf_path=None, use_turnusfiler=False):
    """Complete workflow for creating a new turnus year"""
    
    print(f"🚀 Creating new turnus set: {year_id}")
    
    if pdf_path and os.path.exists(pdf_path):
        # Determine where to save files
        if use_turnusfiler:
            # Save in organized turnusfiler directory
            output_dir = os.path.join(conf.static_dir, 'turnusfiler', year_id.lower())
            os.makedirs(output_dir, exist_ok=True)
            print(f"📂 Organized mode: Files will be saved in {output_dir}")
        else:
            # Save in same directory as PDF
            output_dir = os.path.dirname(os.path.abspath(pdf_path))
            print(f"📂 Same-directory mode: Files will be saved in {output_dir}")
        
        # Generate file paths
        turnus_json_path = os.path.join(output_dir, f'turnuser_{year_id}.json')
        df_json_path = os.path.join(output_dir, f'turnus_df_{year_id}.json')
        
        # 1. Create turnus set in database with file paths
        success, message = create_turnus_set(
            name, 
            year_id, 
            is_active=False,
            turnus_file_path=turnus_json_path,
            df_file_path=df_json_path
        )
        if not success:
            print(f"❌ Database error: {message}")
            return False
        print(f"✅ Created turnus set in database")
        
        # 2. Run scraper
        print(f"📄 Processing PDF: {pdf_path}")
        scraper = ShiftScraper()
        scraper.scrape_pdf(pdf_path)
        
        # 3. Generate JSON files
        scraper.create_json(turnus_json_path)
        print(f"✅ Created turnus JSON: {turnus_json_path}")
        
        # 4. Generate statistics
        print(f"📊 Generating statistics...")
        stats = Turnus(turnus_json_path)
        stats.stats_df.to_json(df_json_path)
        print(f"✅ Created statistics JSON: {df_json_path}")
        
        # 5. Clean up references
        del stats
        time.sleep(1)
        
        # 6. Add shifts to database
        turnus_set = get_turnus_set_by_year(year_id)
        if turnus_set:
            add_shifts_to_turnus_set(turnus_json_path, turnus_set['id'])
            print(f"✅ Added shifts to database")
        else:
            print(f"❌ Could not find turnus set {year_id} in database")
            return False
        
        print(f"🎉 Complete turnus set {year_id} created successfully!")
        print(f"📂 Files saved in: {output_dir}")
        print(f"💾 Database updated with turnus set ID: {turnus_set['id']}")
        
        # List the files created
        print(f"\n📋 Files created:")
        print(f"   📄 {turnus_json_path}")
        print(f"   📊 {df_json_path}")
        
        return True
    else:
        # Create database entry only
        success, message = create_turnus_set(name, year_id, is_active=False)
        if not success:
            print(f"❌ Database error: {message}")
            return False
        print(f"✅ Created turnus set in database (no files)")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create new turnus set')
    parser.add_argument('year_id', help='Year identifier (e.g., R26)')
    parser.add_argument('name', help='Turnus set name (e.g., "OSL Train Shifts 2026")')
    parser.add_argument('pdf_path', nargs='?', help='Path to PDF file')
    parser.add_argument('--turnusfiler', action='store_true', help='Save files in organized turnusfiler directory')
    
    args = parser.parse_args()
    
    create_new_turnus(
        args.year_id.upper(), 
        args.name, 
        args.pdf_path, 
        args.turnusfiler
    )