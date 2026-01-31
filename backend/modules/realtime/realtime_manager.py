
import sqlite3
from datetime import datetime

class RealTimeMonitoringManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_device(self, company_id, name, device_type, unit, threshold_value=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO iot_devices (company_id, name, device_type, unit, threshold_value)
            VALUES (?, ?, ?, ?, ?)
        ''', (company_id, name, device_type, unit, threshold_value))
        conn.commit()
        device_id = cursor.lastrowid
        conn.close()
        return device_id

    def get_devices(self, company_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM iot_devices WHERE company_id = ? ORDER BY id DESC', (company_id,))
        devices = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        conn.close()
        return devices

    def get_device(self, device_id, company_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM iot_devices WHERE id = ? AND company_id = ?', (device_id, company_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(zip([column[0] for column in cursor.description], row))
        return None

    def add_reading(self, device_id, value, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert reading
        cursor.execute('''
            INSERT INTO iot_readings (device_id, timestamp, value)
            VALUES (?, ?, ?)
        ''', (device_id, timestamp, value))
        
        # Check threshold
        cursor.execute('SELECT threshold_value, name, company_id FROM iot_devices WHERE id = ?', (device_id,))
        device = cursor.fetchone()
        if device and device[0] is not None:
            threshold = device[0]
            if float(value) > float(threshold):
                message = f"Eşik Değeri Aşıldı: {value} > {threshold}"
                cursor.execute('''
                    INSERT INTO iot_alerts (device_id, timestamp, message, status)
                    VALUES (?, ?, ?, 'unread')
                ''', (device_id, timestamp, message))
        
        conn.commit()
        conn.close()

    def get_readings(self, device_id, limit=100):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM iot_readings 
            WHERE device_id = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (device_id, limit))
        readings = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        conn.close()
        return readings

    def get_alerts(self, company_id, limit=20):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, d.name as device_name 
            FROM iot_alerts a
            JOIN iot_devices d ON a.device_id = d.id
            WHERE d.company_id = ?
            ORDER BY a.timestamp DESC LIMIT ?
        ''', (company_id, limit))
        alerts = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        conn.close()
        return alerts
