import sqlite3
import os
import sys

# DB Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "sdg_desktop.sqlite")

def fix_system_settings_pk():
    print("Fixing system_settings PK...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Check current PK
        cur.execute("PRAGMA table_info(system_settings)")
        cols = cur.fetchall()
        # cols: (cid, name, type, notnull, dflt_value, pk)
        # If pk > 1 for multiple columns, it's composite.
        pk_cols = [c[1] for c in cols if c[5] > 0]
        if 'company_id' in pk_cols and 'key' in pk_cols:
            print("system_settings already has composite PK (key, company_id). Skipping.")
            return

        # Rename
        cur.execute("DROP TABLE IF EXISTS system_settings_old")
        cur.execute("ALTER TABLE system_settings RENAME TO system_settings_old")
        
        # Create new
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
        
        # Copy data
        # We need to map old columns to new.
        # Old columns: key, value, category, description, updated_at, company_id (might exist)
        # Check old columns
        old_col_names = [c[1] for c in cols]
        
        cols_to_select = "key, value, category, description, updated_at"
        if 'company_id' in old_col_names:
            cols_to_select += ", company_id"
            cols_to_insert = "key, value, category, description, updated_at, company_id"
        else:
            cols_to_insert = "key, value, category, description, updated_at"
            # company_id will use default 1
            
        sql = f"INSERT INTO system_settings ({cols_to_insert}) SELECT {cols_to_select} FROM system_settings_old"
        print(f"Copying data: {sql}")
        cur.execute(sql)
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM system_settings")
        count = cur.fetchone()[0]
        print(f"Copied {count} rows.")
        
        # Drop old
        cur.execute("DROP TABLE system_settings_old")
        conn.commit()
        print("system_settings fixed.")
        
    except Exception as e:
        print(f"Error fixing system_settings: {e}")
        conn.rollback()
    finally:
        conn.close()

def fix_sdg_goals_pk():
    print("Fixing sdg_goals PK...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # Check current PK
        cur.execute("PRAGMA table_info(sdg_goals)")
        cols = cur.fetchall()
        pk_cols = [c[1] for c in cols if c[5] > 0]
        if 'company_id' in pk_cols and 'id' in pk_cols:
            print("sdg_goals already has composite PK (id, company_id). Skipping.")
            return

        # Rename
        cur.execute("DROP TABLE IF EXISTS sdg_goals_old")
        cur.execute("ALTER TABLE sdg_goals RENAME TO sdg_goals_old")
        
        # Create new
        # Check if description exists in old
        old_col_names = [c[1] for c in cols]
        has_desc = 'description' in old_col_names
        
        cur.execute(f"""
            CREATE TABLE sdg_goals (
                id INTEGER,
                code INTEGER,
                title_tr TEXT,
                {'description TEXT,' if has_desc else 'description TEXT,'} 
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER DEFAULT 1,
                PRIMARY KEY (id, company_id)
            )
        """)
        # Note: I added description even if old didn't have it (it will be NULL if not copied, but I should copy if exists)
        
        # Copy data
        cols_select = []
        if 'id' in old_col_names: cols_select.append('id')
        if 'code' in old_col_names: cols_select.append('code')
        if 'title_tr' in old_col_names: cols_select.append('title_tr')
        if 'description' in old_col_names: cols_select.append('description')
        if 'created_at' in old_col_names: cols_select.append('created_at')
        if 'company_id' in old_col_names: cols_select.append('company_id')
        
        cols_str = ", ".join(cols_select)
        
        sql = f"INSERT INTO sdg_goals ({cols_str}) SELECT {cols_str} FROM sdg_goals_old"
        print(f"Copying data: {sql}")
        cur.execute(sql)
        
        cur.execute("SELECT COUNT(*) FROM sdg_goals")
        count = cur.fetchone()[0]
        print(f"Copied {count} rows.")
        
        cur.execute("DROP TABLE sdg_goals_old")
        conn.commit()
        print("sdg_goals fixed.")
        
    except Exception as e:
        print(f"Error fixing sdg_goals: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_system_settings_pk()
    fix_sdg_goals_pk()
