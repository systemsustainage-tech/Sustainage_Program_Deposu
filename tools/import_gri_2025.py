import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from config.database import DB_PATH

def import_gri_2025():
    print(f"Importing GRI 2025-2026 Standards into {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 2025-2026 Updates (Key Changes)
    # - Biodiversity (GRI 101: 2024)
    # - Climate Change (Expected new standard)
    # - Sector Standards (Mining, Energy, etc.)
    
    new_standards = [
        ("GRI 101", "Biodiversity 2024", "Updated biodiversity standard focusing on supply chain and location-specific impacts.", "Topic"),
        ("GRI 14", "Mining Sector 2024", "Standard for the mining sector impacts.", "Sector"),
        ("GRI 102", "Climate Change (Draft)", "Upcoming climate change reporting standard aligned with ISSB.", "Topic"),
        ("GRI 201", "Economic Performance 2025", "Updated economic performance indicators.", "Topic"),
        ("GRI 305", "Emissions 2025", "Enhanced emissions reporting requirements.", "Topic")
    ]
    
    try:
        count = 0
        for code, name, desc, cat in new_standards:
            # Check if exists
            cursor.execute("SELECT id FROM gri_standards WHERE code = ?", (code,))
            existing = cursor.fetchone()
            
            if existing:
                # Update
                cursor.execute("""
                    UPDATE gri_standards 
                    SET title = ?, description = ?, category = ?, created_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (name, desc, cat, existing[0]))
                print(f"Updated {code}: {name}")
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO gri_standards (code, title, description, category) 
                    VALUES (?, ?, ?, ?)
                """, (code, name, desc, cat))
                print(f"Inserted {code}: {name}")
            count += 1
            
        conn.commit()
        print(f"Successfully processed {count} GRI standards.")
        
    except Exception as e:
        print(f"Error importing GRI data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import_gri_2025()
