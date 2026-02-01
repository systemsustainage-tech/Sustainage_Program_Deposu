
import sqlite3
import json
import os
import re
from datetime import datetime

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')
JSON_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'gri_2026_update.json')

def get_year_from_text(text):
    if not text:
        return None
    match = re.search(r'20\d{2}', text)
    if match:
        return match.group(0)
    return None

def populate_dates():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Load JSON data for reference
    gri_updates = {}
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get('standards', []):
                    gri_updates[item['code']] = item
            print(f"Loaded {len(gri_updates)} standards from JSON.")
        except Exception as e:
            print(f"Error loading JSON: {e}")
    
    # Get all standards
    cursor.execute("SELECT id, code, title, effective_date, version FROM gri_standards")
    standards = cursor.fetchall()
    
    updated_count = 0
    
    for std in standards:
        std_id, code, title, effective_date, version = std
        
        new_effective_date = effective_date
        new_version = version
        
        # Determine year
        year = None
        
        # 1. Check JSON match
        if code in gri_updates:
            json_item = gri_updates[code]
            year = get_year_from_text(json_item.get('title_en')) or get_year_from_text(json_item.get('title_tr'))
        
        # 2. Check DB title
        if not year and title:
            year = get_year_from_text(title)
            
        # 3. Default to 2021 if not found (GRI Universal Standards 2021)
        if not year:
            year = '2021'
            
        # Set values if missing
        if not new_effective_date:
            new_effective_date = f"{year}-01-01"
            
        if not new_version:
            new_version = year
            
        # Update if changed
        if new_effective_date != effective_date or new_version != version:
            cursor.execute("""
                UPDATE gri_standards 
                SET effective_date = ?, version = ? 
                WHERE id = ?
            """, (new_effective_date, new_version, std_id))
            updated_count += 1
            print(f"Updated {code}: Date={new_effective_date}, Version={new_version}")
            
    conn.commit()
    conn.close()
    print(f"Total records updated: {updated_count}")

if __name__ == "__main__":
    populate_dates()
