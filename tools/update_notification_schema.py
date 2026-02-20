import sqlite3
import os
import sys

def update_schema():
    # Define database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sdg_desktop.sqlite')
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"Updating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check if company_id column exists in notifications
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column to notifications...")
            
            # Since SQLite doesn't support adding column with foreign key constraint easily in one go with data migration,
            # we'll do the rename-create-copy dance or just ADD COLUMN if we don't strictly enforce FK constraint at DB level right now
            # (SQLite supports ADD COLUMN but not generic constraints easily).
            # But let's try the safer approach: ADD COLUMN (nullable/default) then UPDATE.
            
            cursor.execute("ALTER TABLE notifications ADD COLUMN company_id INTEGER DEFAULT 1")
            
            # Now try to update company_id from users table
            print("Migrating company_id from users table...")
            cursor.execute("""
                UPDATE notifications 
                SET company_id = (
                    SELECT company_id FROM users WHERE users.id = notifications.user_id
                )
                WHERE user_id IN (SELECT id FROM users)
            """)
            
            # If any are still NULL (e.g. deleted users), set to default 1
            cursor.execute("UPDATE notifications SET company_id = 1 WHERE company_id IS NULL")
            
            # Create index for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_company_user ON notifications(company_id, user_id)")
            
            print("notifications table updated successfully.")
        
        else:
            print("notifications table already has company_id.")
        
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
