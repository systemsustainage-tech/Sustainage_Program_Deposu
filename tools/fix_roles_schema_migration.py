import sqlite3
import os
import sys

# Try multiple possible paths for the DB
possible_paths = [
    '../backend/data/sdg_desktop.sqlite',
    'backend/data/sdg_desktop.sqlite',
    r'C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
]

db_path = None
for p in possible_paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("Database file not found!")
    sys.exit(1)

print(f"Migrating DB at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("BEGIN TRANSACTION")

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
    if not cursor.fetchone():
        print("Table 'roles' does not exist. Skipping.")
        sys.exit(0)

    # 1. Rename existing table
    print("Renaming 'roles' to 'roles_old'...")
    cursor.execute("ALTER TABLE roles RENAME TO roles_old")

    # 2. Create new table with updated constraints
    print("Creating new 'roles' table...")
    create_table_sql = """
    CREATE TABLE roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        display_name VARCHAR(100) NOT NULL,
        description TEXT,
        is_system_role BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        updated_by INTEGER,
        company_id INTEGER DEFAULT 1,
        FOREIGN KEY (created_by) REFERENCES users(id),
        FOREIGN KEY (updated_by) REFERENCES users(id),
        UNIQUE(name, company_id)
    )
    """
    cursor.execute(create_table_sql)

    # 3. Copy data
    print("Copying data...")
    # Get columns from old table to ensure we map correctly
    cursor.execute("PRAGMA table_info(roles_old)")
    columns = [row[1] for row in cursor.fetchall()]
    columns_str = ", ".join(columns)
    
    insert_sql = f"INSERT INTO roles ({columns_str}) SELECT {columns_str} FROM roles_old"
    cursor.execute(insert_sql)

    # 4. Drop old table
    print("Dropping 'roles_old'...")
    cursor.execute("DROP TABLE roles_old")

    conn.commit()
    print("Migration successful!")

    # Verify
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='roles'")
    print("New Schema:", cursor.fetchone()[0])

except Exception as e:
    conn.rollback()
    print(f"Migration failed: {e}")
    sys.exit(1)

finally:
    conn.close()
