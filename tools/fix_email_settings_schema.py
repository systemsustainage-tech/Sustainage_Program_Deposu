
import sys
import os
import sqlite3
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config.database import get_db_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_system_settings_schema():
    db_path = get_db_path()
    logger.info(f"Checking system_settings schema in {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
        if not cursor.fetchone():
            logger.info("system_settings table does not exist. Creating it...")
            cursor.execute("""
                CREATE TABLE system_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT DEFAULT 'general',
                    key TEXT NOT NULL UNIQUE,
                    value TEXT,
                    description TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("system_settings table created.")
        else:
            # Check if category column exists
            cursor.execute("PRAGMA table_info(system_settings)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'category' not in columns:
                logger.info("Adding 'category' column to system_settings...")
                cursor.execute("ALTER TABLE system_settings ADD COLUMN category TEXT DEFAULT 'general'")
                logger.info("'category' column added.")
            else:
                logger.info("'category' column already exists.")
                
            # Ensure other columns exist (just in case)
            if 'description' not in columns:
                logger.info("Adding 'description' column to system_settings...")
                cursor.execute("ALTER TABLE system_settings ADD COLUMN description TEXT")
                
        # Insert default email settings if not present
        email_settings = [
            ('email', 'smtp_server', 'smtp.digage.tr', 'SMTP Sunucu Adresi'),
            ('email', 'smtp_port', '587', 'SMTP Portu'),
            ('email', 'use_tls', 'false', 'TLS Kullanımı'),
            ('email', 'sender_email', 'system@digage.tr', 'Gönderen E-posta'),
            ('email', 'sender_name', 'Sustainage SDG Platform', 'Gönderen Adı'),
            ('email', 'enabled', 'true', 'E-posta Gönderimi Aktif')
        ]
        
        for category, key, value, description in email_settings:
            cursor.execute("""
                INSERT OR IGNORE INTO system_settings (category, key, value, description)
                VALUES (?, ?, ?, ?)
            """, (category, key, value, description))
            
            # Update category if key exists but category might be null/default
            cursor.execute("UPDATE system_settings SET category = ? WHERE key = ?", (category, key))
            
        conn.commit()
        logger.info("System settings schema fixed and default email settings verified.")
        
    except Exception as e:
        logger.error(f"Error fixing system_settings schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_system_settings_schema()
