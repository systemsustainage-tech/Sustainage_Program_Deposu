import sqlite3
import os
import sys

# Remote database path
# DB_PATH = '/var/www/sustainage/sustainage.db'
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def update_schema():
    target_db_path = DB_PATH
    if not os.path.exists(target_db_path):
        print(f"Database not found at {target_db_path}")
        # Try alternate path
        if os.path.exists('/var/www/sustainage/sustainage.db'):
            target_db_path = '/var/www/sustainage/sustainage.db'
        elif os.path.exists('sustainage.db'):
            target_db_path = 'sustainage.db'
        elif os.path.exists(r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'):
            target_db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
        else:
            print("Could not find database file.")
            return

    print(f"Updating database at {target_db_path}...")
    conn = sqlite3.connect(target_db_path)
    cursor = conn.cursor()

    # Create companies table if not exists (Dependency for users/licenses)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sector TEXT,
            employee_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Table 'companies' checked/created.")

    # Create users table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone VARCHAR(20),
            department VARCHAR(100),
            position VARCHAR(100),
            avatar_path VARCHAR(255),
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            last_login TIMESTAMP,
            login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            failed_attempts INTEGER DEFAULT 0,
            totp_secret_encrypted TEXT,
            totp_backup_codes TEXT,
            must_change_password INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)
    print("Table 'users' checked/created.")

    # Create user_companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_id INTEGER NOT NULL,
            is_primary BOOLEAN DEFAULT 0,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            UNIQUE(user_id, company_id)
        )
    """)
    print("Table 'user_companies' checked/created.")

    # Create audit_logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(50) NOT NULL,
            resource_type VARCHAR(50) NOT NULL,
            resource_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            session_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    print("Table 'audit_logs' checked/created.")

    print("Updating 'users' table columns...")
    # Get current columns
    cursor.execute("PRAGMA table_info(users)")
    current_columns = [row[1] for row in cursor.fetchall()]

    # Columns to add
    new_columns = {
        'totp_secret_encrypted': 'TEXT',
        'totp_backup_codes': 'TEXT',
        'must_change_password': 'INTEGER DEFAULT 0',
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

    # report_sections
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
    
    # Licenses table check
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            license_key TEXT UNIQUE NOT NULL,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            max_users INTEGER DEFAULT 5,
            status VARCHAR(20) DEFAULT 'active',
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)
    print("Table 'licenses' checked/created.")

    conn.commit()
    conn.close()
    print("\nRemote schema update completed.")

if __name__ == "__main__":
    update_schema()
