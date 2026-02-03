import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'sdg_desktop.sqlite')

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Updating 'users' table...")
    # Get current columns
    cursor.execute("PRAGMA table_info(users)")
    current_columns = [row[1] for row in cursor.fetchall()]

    # Columns to add
    new_columns = {
        'totp_secret_encrypted': 'TEXT',
        'totp_backup_codes': 'TEXT',
        'must_change_password': 'INTEGER DEFAULT 0',
        # Ensure failed_attempts and locked_until exist (they might already, but good to be safe)
        'failed_attempts': 'INTEGER DEFAULT 0',
        'locked_until': 'REAL'
    }

    for col, dtype in new_columns.items():
        if col not in current_columns:
            print(f"Adding column '{col}' to 'users' table.")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            except sqlite3.OperationalError as e:
                print(f"Error adding column {col}: {e}")
        else:
            print(f"Column '{col}' already exists in 'users' table.")

    print("\nCreating missing tables...")

    # password_reset_tokens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("Table 'password_reset_tokens' checked/created.")

    # temp_access_tokens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_access_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("Table 'temp_access_tokens' checked/created.")

    # report_templates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            template_name TEXT NOT NULL,
            template_type TEXT NOT NULL,
            template_content TEXT,
            template_variables TEXT,
            language_code TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Table 'report_templates' checked/created.")

    # report_sections (assuming relationship to report_templates or generic)
    # Based on name, it likely links sections to templates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            section_name TEXT NOT NULL,
            section_content TEXT,
            section_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES report_templates(id)
        )
    """)
    print("Table 'report_sections' checked/created.")

    # report_generation_log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_generation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            user_id INTEGER,
            template_id INTEGER,
            report_type TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            file_path TEXT,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (template_id) REFERENCES report_templates(id)
        )
    """)
    print("Table 'report_generation_log' checked/created.")

    # report_customizations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_customizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            template_id INTEGER,
            custom_settings TEXT, -- JSON storage for colors, fonts, logos etc.
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES report_templates(id)
        )
    """)
    print("Table 'report_customizations' checked/created.")

    conn.commit()
    conn.close()
    print("\nSchema update completed.")

if __name__ == "__main__":
    update_schema()
