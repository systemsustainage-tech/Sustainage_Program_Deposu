import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def migrate_system_settings():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
        if not cur.fetchone():
            logging.info("Table system_settings does not exist. Skipping migration.")
            return

        # Check current primary key
        cur.execute("PRAGMA table_info(system_settings)")
        columns = cur.fetchall()
        
        # columns format: (cid, name, type, notnull, dflt_value, pk)
        pk_cols = [col[1] for col in columns if col[5] > 0]
        has_company_id = any(col[1] == 'company_id' for col in columns)
        
        logging.info(f"Current PK: {pk_cols}")
        logging.info(f"Has company_id: {has_company_id}")

        # If PK is exactly ['key', 'company_id'] (order doesn't strict matter for set), we are good.
        if set(pk_cols) == {'key', 'company_id'}:
            logging.info("Schema is already correct (PK: key, company_id).")
            return

        logging.info("Migrating system_settings to use composite PRIMARY KEY (key, company_id)...")
        
        # 1. Rename existing table
        cur.execute("ALTER TABLE system_settings RENAME TO system_settings_old")
        
        # 2. Create new table with correct schema
        cur.execute("""
            CREATE TABLE system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER DEFAULT 1,
                PRIMARY KEY (key, company_id)
            )
        """)
        
        # 3. Copy data
        # If company_id existed in old table, preserve it. If not, default to 1.
        if has_company_id:
             cur.execute("""
                INSERT INTO system_settings (key, value, category, description, updated_at, company_id)
                SELECT key, value, category, description, updated_at, COALESCE(company_id, 1) FROM system_settings_old
            """)
        else:
            cur.execute("""
                INSERT INTO system_settings (key, value, category, description, updated_at, company_id)
                SELECT key, value, category, description, updated_at, 1 FROM system_settings_old
            """)
            
        # 4. Drop old table
        cur.execute("DROP TABLE system_settings_old")
        
        conn.commit()
        logging.info("Migration completed successfully.")
        
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_system_settings()
