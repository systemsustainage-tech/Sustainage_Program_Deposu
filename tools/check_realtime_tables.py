import sqlite3
import os

DB_PATH = 'sustainage.db'

def check_and_create_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check iot_devices
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='iot_devices'")
    if not cursor.fetchone():
        print("Creating iot_devices table...")
        cursor.execute('''
            CREATE TABLE iot_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                device_type TEXT,
                unit TEXT,
                threshold_value REAL
            )
        ''')
    else:
        print("iot_devices table exists.")

    # Check iot_readings
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='iot_readings'")
    if not cursor.fetchone():
        print("Creating iot_readings table...")
        cursor.execute('''
            CREATE TABLE iot_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                timestamp TEXT,
                value REAL,
                FOREIGN KEY (device_id) REFERENCES iot_devices (id)
            )
        ''')
    else:
        print("iot_readings table exists.")

    # Check iot_alerts
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='iot_alerts'")
    if not cursor.fetchone():
        print("Creating iot_alerts table...")
        cursor.execute('''
            CREATE TABLE iot_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                timestamp TEXT,
                message TEXT,
                status TEXT DEFAULT 'unread',
                FOREIGN KEY (device_id) REFERENCES iot_devices (id)
            )
        ''')
    else:
        print("iot_alerts table exists.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    check_and_create_tables()
