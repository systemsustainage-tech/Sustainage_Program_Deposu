import sys
import os
import sqlite3

# Add path to find config
sys.path.insert(0, '/var/www/sustainage')

try:
    from config.database import DB_PATH
    print(f"Imported DB_PATH: {DB_PATH}")
except ImportError as e:
    print(f"Failed to import config.database: {e}")
    # Fallback
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    print(f"Using fallback DB_PATH: {DB_PATH}")

def diagnose():
    print(f"Diagnosing DB at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("ERROR: DB file does not exist!")
        return

    print(f"File permissions: {oct(os.stat(DB_PATH).st_mode)[-3:]}")
    print(f"File owner: {os.stat(DB_PATH).st_uid}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Listing tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found {len(tables)} tables.")
        
        if 'report_registry' in tables:
            print("SUCCESS: report_registry table found.")
            
            # Try to insert
            try:
                print("Attempting test insert...")
                cursor.execute("""
                    INSERT INTO report_registry 
                    (company_id, module_code, report_name, report_type, file_path, file_size, reporting_period, description, created_by, created_at)
                    VALUES (999, 'test', 'Test Report', 'TEST', '/tmp/test', 0, '2024', 'Test', 1, CURRENT_TIMESTAMP)
                """)
                conn.commit()
                print("Insert successful.")
                
                # Clean up
                cursor.execute("DELETE FROM report_registry WHERE company_id=999")
                conn.commit()
                print("Cleanup successful.")
            except Exception as e:
                print(f"Insert failed: {e}")
        else:
            print("ERROR: report_registry table NOT found.")
            
        conn.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    diagnose()
