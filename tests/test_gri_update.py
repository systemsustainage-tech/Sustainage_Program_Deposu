
import sys
import os
import sqlite3
import json
from flask import Flask, g, session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import get_db_path

def test_gri_api():
    print("Testing GRI API and Database Updates...")
    db_path = get_db_path()
    
    # 1. Check if sector column exists in gri_standards
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT sector FROM gri_standards LIMIT 1")
        print("✅ 'sector' column exists in gri_standards.")
    except Exception as e:
        print(f"❌ 'sector' column MISSING: {e}")
        return

    # 2. Check if new sectors are present
    cursor.execute("SELECT DISTINCT sector FROM gri_standards")
    sectors = [r[0] for r in cursor.fetchall()]
    print(f"Found sectors: {sectors}")
    expected_sectors = ['Mining', 'Energy', 'Oil & Gas', 'Coal']
    for s in expected_sectors:
        if s in sectors:
            print(f"✅ Sector '{s}' found.")
        else:
            print(f"⚠️ Sector '{s}' NOT found (might need data update).")

    # 3. Test API Logic (Simulated)
    # We can't easily invoke the Flask route without running the app, 
    # but we can simulate the DB query used in the API.
    
    # Pick a standard code, e.g., GRI 14
    std_code = 'GRI 14'
    cursor.execute("SELECT id FROM gri_standards WHERE code = ?", (std_code,))
    std = cursor.fetchone()
    if std:
        std_id = std[0]
        cursor.execute("SELECT code, title FROM gri_indicators WHERE standard_id = ?", (std_id,))
        indicators = cursor.fetchall()
        print(f"\nIndicators for {std_code}: {len(indicators)}")
        if len(indicators) > 0:
             print(f"✅ {std_code} has indicators (Example: {indicators[0]})")
        else:
             print(f"❌ {std_code} has NO indicators!")
    else:
        print(f"❌ Standard {std_code} not found in DB!")

    conn.close()

if __name__ == "__main__":
    test_gri_api()
