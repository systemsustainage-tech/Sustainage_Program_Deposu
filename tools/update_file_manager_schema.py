
import sqlite3
import os
import sys

def update_schema():
    # Define database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend', 'data', 'sustainage.db')
    
    if not os.path.exists(db_path):
        # Try remote path structure if local not found (though this runs locally or remotely)
        # On remote: /var/www/sustainage/backend/data/sdg_desktop.sqlite (Wait, memory says sdg_desktop.sqlite)
        # Let's check the memory for correct DB path.
        # Memory says: "Remote Database Path: Correct path is '/var/www/sustainage/backend/data/sdg_desktop.sqlite'"
        # But locally it might be sustainage.db or sdg_desktop.sqlite.
        # I should check which one exists.
        pass

    # Let's handle the path dynamically or pass it as arg
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Updating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if unique index is correct
        cursor.execute("PRAGMA index_list(file_tags)")
        indexes = cursor.fetchall()
        needs_update = True
        
        # Check existing unique indexes
        for idx in indexes:
             # idx: (seq, name, unique, origin, partial)
             if idx[2] == 1: # Unique
                 cursor.execute(f"PRAGMA index_info({idx[1]})")
                 cols = cursor.fetchall()
                 col_names = [c[2] for c in cols]
                 # We want a unique index covering BOTH company_id and tag_name
                 if 'company_id' in col_names and 'tag_name' in col_names and len(col_names) == 2:
                     needs_update = False
                     print("Correct unique index found.")
                     break
        
        if needs_update:
            print("Updating file_tags table schema (missing correct unique constraint)...")
            
            # Rename existing table
            cursor.execute("ALTER TABLE file_tags RENAME TO file_tags_old")
            
            # Create new table
            cursor.execute("""
                CREATE TABLE file_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL DEFAULT 1,
                    tag_name TEXT NOT NULL,
                    tag_color TEXT DEFAULT '#3498db',
                    created_at TEXT,
                    UNIQUE(company_id, tag_name)
                )
            """)
            
            # Migrate data
            print("Migrating tags data...")
            # Check if old table has company_id
            cursor.execute("PRAGMA table_info(file_tags_old)")
            old_cols = [info[1] for info in cursor.fetchall()]
            has_company_id = 'company_id' in old_cols

            cursor.execute(f"SELECT id, tag_name, tag_color, created_at {', company_id' if has_company_id else ''} FROM file_tags_old")
            old_tags = cursor.fetchall()
            
            for row in old_tags:
                if has_company_id:
                    old_id, name, color, created, comp_id = row
                    # Insert directly
                    cursor.execute("""
                        INSERT OR IGNORE INTO file_tags (company_id, tag_name, tag_color, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (comp_id, name, color, created))
                    
                    # Update relations if needed (ids might change if we re-insert, but here we let autoincrement handle it)
                    # Wait, if we change IDs, we break relations.
                    # We should try to preserve IDs if possible, OR update relations.
                    # If we just insert, new IDs are generated.
                    # We must update relations.
                    
                    # Get new id
                    cursor.execute("SELECT id FROM file_tags WHERE company_id = ? AND tag_name = ?", (comp_id, name))
                    new_tag_id = cursor.fetchone()[0]
                    
                    # Update relations
                    cursor.execute("UPDATE file_tag_relations SET tag_id = ? WHERE tag_id = ?", (new_tag_id, old_id))
                    
                else:
                    # Old logic (infer company from relations)
                    old_id, name, color, created = row
                    
                    # Find which companies use this tag
                    cursor.execute("""
                        SELECT DISTINCT f.company_id 
                        FROM file_tag_relations ftr
                        JOIN files f ON ftr.file_id = f.id
                        WHERE ftr.tag_id = ?
                    """, (old_id,))
                    
                    companies = cursor.fetchall()
                    
                    if not companies:
                        # Default to company 1
                        cursor.execute("""
                            INSERT OR IGNORE INTO file_tags (company_id, tag_name, tag_color, created_at)
                            VALUES (?, ?, ?, ?)
                        """, (1, name, color, created))
                    else:
                        for (comp_id,) in companies:
                            # Insert tag for this company
                            cursor.execute("""
                                INSERT OR IGNORE INTO file_tags (company_id, tag_name, tag_color, created_at)
                                VALUES (?, ?, ?, ?)
                            """, (comp_id, name, color, created))
                            
                            # Get new id
                            cursor.execute("SELECT id FROM file_tags WHERE company_id = ? AND tag_name = ?", (comp_id, name))
                            new_tag_id = cursor.fetchone()[0]
                            
                            # Update relations for this company's files
                            cursor.execute("""
                                UPDATE file_tag_relations
                                SET tag_id = ?
                                WHERE tag_id = ? AND file_id IN (
                                    SELECT id FROM files WHERE company_id = ?
                                )
                            """, (new_tag_id, old_id, comp_id))
            
            # Drop old table
            cursor.execute("DROP TABLE file_tags_old")
            print("file_tags table updated successfully.")
            
        else:
            print("file_tags schema is already correct.")

        conn.commit()
        print("Schema update completed.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating schema: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
