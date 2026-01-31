
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.database import DB_PATH

# FORCE DB_PATH for remote environment to ensure correct DB is used
if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def migrate():
    print(f"Migrating Real-Time Monitoring tables to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # iot_devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            device_type TEXT, -- energy, water, waste, other
            unit TEXT,
            threshold_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # iot_readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            value REAL NOT NULL,
            FOREIGN KEY (device_id) REFERENCES iot_devices (id)
        )
    ''')
    
    # iot_alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS iot_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            status TEXT DEFAULT 'unread', -- unread, read, resolved
            FOREIGN KEY (device_id) REFERENCES iot_devices (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Real-Time Monitoring migration completed successfully.")

if __name__ == '__main__':
    migrate()
