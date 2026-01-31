import sqlite3
import os
import sys

# Hardcoded DB path for remote
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def cleanup():
    print(f"Cleaning up DB at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Find templates with 0 questions
        cursor.execute("""
            SELECT t.id, t.name, count(q.id) as q_count 
            FROM survey_templates t 
            LEFT JOIN survey_template_questions q ON t.id = q.template_id 
            GROUP BY t.id 
            HAVING q_count = 0
        """)
        empty_templates = cursor.fetchall()
        
        print(f"Found {len(empty_templates)} empty templates.")
        
        if empty_templates:
            ids_to_delete = [str(t[0]) for t in empty_templates]
            id_str = ",".join(ids_to_delete)
            
            # Delete them
            cursor.execute(f"DELETE FROM survey_templates WHERE id IN ({id_str})")
            print(f"Deleted {cursor.rowcount} empty templates.")
            
        # 2. Find duplicates (same name) and keep only the latest one with questions
        cursor.execute("""
            SELECT name, count(*) as c 
            FROM survey_templates 
            GROUP BY name 
            HAVING c > 1
        """)
        duplicates = cursor.fetchall()
        
        for dup in duplicates:
            name = dup[0]
            print(f"Processing duplicate: {name}")
            
            # Get all IDs for this name, ordered by ID desc
            cursor.execute("SELECT id FROM survey_templates WHERE name=? ORDER BY id DESC", (name,))
            ids = [row[0] for row in cursor.fetchall()]
            
            # Keep the first one (latest), delete others
            if len(ids) > 1:
                keep_id = ids[0]
                delete_ids = ids[1:]
                del_str = ",".join([str(i) for i in delete_ids])
                
                cursor.execute(f"DELETE FROM survey_templates WHERE id IN ({del_str})")
                print(f"Kept ID {keep_id}, deleted IDs {del_str}")
                
                # Also clean up any questions associated with deleted templates (cascade should handle this but just in case)
                cursor.execute(f"DELETE FROM survey_template_questions WHERE template_id IN ({del_str})")
                
        conn.commit()
        print("Cleanup complete.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
            
    conn.close()

if __name__ == "__main__":
    cleanup()
