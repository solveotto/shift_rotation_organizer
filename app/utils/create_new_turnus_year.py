#!/usr/bin/env python3
"""
Annual turnus creation script
Usage: python create_new_turnus_year.py R26 "OSL Train Shifts 2026"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.shiftscraper import ShiftScraper
from app.utils.db_utils import create_turnus_set, add_shifts_to_turnus_set, get_turnus_set_by_year
from app.utils.shift_stats import Turnus
from config import conf

def create_new_turnus(year_id, name, pdf_path=None):
    """Complete workflow for creating a new turnus year"""
    
    print(f"🚀 Creating new turnus set: {year_id}")
    
    # 1. Create turnus set in database
    success, message = create_turnus_set(name, year_id, is_active=False)
    if not success:
        print(f"❌ Database error: {message}")
        return False
    print(f"✅ Created turnus set in database")
    
    # 2. Setup directories
    year_dir = os.path.join(conf.static_dir, year_id.lower())
    os.makedirs(year_dir, exist_ok=True)
    print(f"✅ Created directory: {year_dir}")
    
    if pdf_path and os.path.exists(pdf_path):
        # 3. Run scraper
        print(f"📄 Processing PDF: {pdf_path}")
        scraper = ShiftScraper()
        scraper.scrape_pdf(pdf_path)
        
        # 4. Generate JSON files
        turnus_json_path = os.path.join(year_dir, f'turnuser_{year_id}.json')
        scraper.create_json(turnus_json_path)
        print(f"✅ Created turnus JSON: {turnus_json_path}")
        
        # 5. Generate statistics
        stats = Turnus(turnus_json_path)
        df_json_path = os.path.join(year_dir, f'turnus_df_{year_id}.json')
        stats.stats_df.to_json(df_json_path)
        print(f"✅ Created statistics JSON: {df_json_path}")
        
        # 6. Add shifts to database
        turnus_set = get_turnus_set_by_year(year_id)
        if turnus_set:
            add_shifts_to_turnus_set(turnus_json_path, turnus_set['id'])
            print(f"✅ Added shifts to database")
        else:
            print(f"❌ Could not find turnus set {year_id} in database")
            return False
        
        print(f"🎉 Complete turnus set {year_id} created successfully!")
        print(f"📂 Files created in: {year_dir}")
        print(f"💾 Database updated with turnus set ID: {turnus_set['id']}")
        return True
    else:
        print(f"⚠️  Turnus set created in database only. Add JSON files manually to {year_dir}")
        if pdf_path:
            print(f"❌ PDF file not found: {pdf_path}")
        print(f"💡 You can manually place files in {year_dir} and run:")
        print(f"   - turnuser_{year_id}.json")
        print(f"   - turnus_df_{year_id}.json")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_new_turnus_year.py <YEAR_ID> <NAME> [PDF_PATH]")
        print("Example: python create_new_turnus_year.py R26 'OSL Train Shifts 2026' turnuser_R26.pdf")
        sys.exit(1)
    
    year_id = sys.argv[1].upper()  # Ensure uppercase
    name = sys.argv[2]
    pdf_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_new_turnus(year_id, name, pdf_path)