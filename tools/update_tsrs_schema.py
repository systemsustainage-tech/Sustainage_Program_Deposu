
import sqlite3
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_tsrs_schema():
    # Database paths to check
    db_paths = [
        'c:\\SUSTAINAGESERVER\\backend\\sustainage.db',
        'c:\\SUSTAINAGESERVER\\sustainage.db',
        '/var/www/sustainage/backend/sustainage.db',
        'backend/sustainage.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database not found!")
        # Create new if not exists (for local dev)
        db_path = 'backend/sustainage.db'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Updating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'backend', 'modules', 'tsrs', 'tsrs_schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"Schema file not found at {schema_path}")
            return
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        # Execute schema script
        cursor.executescript(schema_sql)
        
        # Verify map_tsrs_esrs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='map_tsrs_esrs'")
        if cursor.fetchone():
            print("map_tsrs_esrs table verified.")
        else:
            print("Error: map_tsrs_esrs table not created.")
            
        conn.commit()
        conn.close()
        print("TSRS Schema update completed successfully.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_tsrs_schema()
