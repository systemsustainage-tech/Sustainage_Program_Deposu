import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def migrate_file_manager_isolation(db_path):
    print(f"Migrating database at {db_path}...")
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. file_metadata
        print("Checking file_metadata...")
        cursor.execute("PRAGMA table_info(file_metadata)")
        cols = [c[1] for c in cursor.fetchall()]
        
        if cols and 'company_id' not in cols:
            print("Adding company_id to file_metadata...")
            cursor.execute("ALTER TABLE file_metadata ADD COLUMN company_id INTEGER")
            
            print("Populating company_id in file_metadata from files table...")
            cursor.execute("""
                UPDATE file_metadata
                SET company_id = (
                    SELECT company_id 
                    FROM files 
                    WHERE files.id = file_metadata.file_id
                )
            """)
            
            # Handle orphans or nulls (default to 1)
            cursor.execute("UPDATE file_metadata SET company_id = 1 WHERE company_id IS NULL")
            conn.commit()
            print("file_metadata migration complete.")
        else:
            print("file_metadata already has company_id.")

        # 2. file_tag_relations
        print("Checking file_tag_relations...")
        cursor.execute("PRAGMA table_info(file_tag_relations)")
        cols = [c[1] for c in cursor.fetchall()]
        
        if cols and 'company_id' not in cols:
            print("Adding company_id to file_tag_relations...")
            cursor.execute("ALTER TABLE file_tag_relations ADD COLUMN company_id INTEGER")
            
            print("Populating company_id in file_tag_relations from files table...")
            cursor.execute("""
                UPDATE file_tag_relations
                SET company_id = (
                    SELECT company_id 
                    FROM files 
                    WHERE files.id = file_tag_relations.file_id
                )
            """)
            
            # Handle orphans or nulls
            cursor.execute("UPDATE file_tag_relations SET company_id = 1 WHERE company_id IS NULL")
            conn.commit()
            print("file_tag_relations migration complete.")
        else:
            print("file_tag_relations already has company_id.")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    # Local path
    local_db = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
    
    # Remote path check (argument based)
    if len(sys.argv) > 1:
        target_db = sys.argv[1]
    else:
        target_db = local_db
        
    migrate_file_manager_isolation(target_db)
