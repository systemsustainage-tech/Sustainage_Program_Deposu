import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager

class RealTimeMonitoringManager(BaseTenantManager):
    """Real-time monitoring manager for IoT devices and readings."""

    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self.create_tables()

    def create_tables(self) -> None:
        """Create necessary tables for real-time monitoring."""
        try:
            # IoT Devices table
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS iot_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    threshold_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)
            
            # IoT Readings table
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS iot_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    value REAL NOT NULL,
                    FOREIGN KEY(device_id) REFERENCES iot_devices(id) ON DELETE CASCADE
                )
            """)
            
            # IoT Alerts table
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS iot_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'unread',
                    FOREIGN KEY(device_id) REFERENCES iot_devices(id) ON DELETE CASCADE
                )
            """)
        except Exception as e:
            logging.error(f"Error creating RealTimeMonitoring tables: {e}")

    def add_device(self, company_id: int, name: str, device_type: str, unit: str, threshold_value: Optional[float] = None) -> Optional[int]:
        """Add a new IoT device."""
        try:
            self._ensure_context(company_id)
            query = """
                INSERT INTO iot_devices (company_id, name, device_type, unit, threshold_value)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = self.execute_update(query, (company_id, name, device_type, unit, threshold_value))
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error adding device: {e}")
            return None

    def get_devices(self, company_id: int) -> List[Dict[str, Any]]:
        """Get all devices for a company."""
        try:
            self._ensure_context(company_id)
            query = "SELECT * FROM iot_devices WHERE company_id = ? ORDER BY id DESC"
            return self.execute_query(query, (company_id,))
        except Exception as e:
            logging.error(f"Error getting devices: {e}")
            return []

    def get_device(self, device_id: int, company_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific device."""
        try:
            self._ensure_context(company_id)
            query = "SELECT * FROM iot_devices WHERE id = ? AND company_id = ?"
            rows = self.execute_query(query, (device_id, company_id))
            return rows[0] if rows else None
        except Exception as e:
            logging.error(f"Error getting device: {e}")
            return None

    def add_reading(self, device_id: int, value: float, timestamp: Optional[str] = None) -> None:
        """Add a new reading for a device and check for alerts."""
        try:
            if timestamp is None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # First, fetch the device to get threshold and company_id
            # We skip tenant filter here because we might not have the context yet, 
            # but we need to find the device first.
            device_query = "SELECT threshold_value, name, company_id FROM iot_devices WHERE id = ?"
            device_rows = self.execute_query(device_query, (device_id,), skip_tenant_filter=True)
            
            if not device_rows:
                logging.warning(f"Device {device_id} not found for reading insertion")
                return

            device = device_rows[0]
            # Set context for consistency, though we'll use skip_tenant_filter for readings table 
            # since it doesn't have company_id
            self._ensure_context(device['company_id'])

            # Insert reading
            insert_query = """
                INSERT INTO iot_readings (device_id, timestamp, value)
                VALUES (?, ?, ?)
            """
            self.execute_update(insert_query, (device_id, timestamp, value), skip_tenant_filter=True)
            
            # Check threshold
            if device['threshold_value'] is not None:
                threshold = float(device['threshold_value'])
                if float(value) > threshold:
                    message = f"Eşik Değeri Aşıldı: {value} > {threshold}"
                    alert_query = """
                        INSERT INTO iot_alerts (device_id, timestamp, message, status)
                        VALUES (?, ?, ?, 'unread')
                    """
                    self.execute_update(alert_query, (device_id, timestamp, message), skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"Error adding reading: {e}")

    def get_readings(self, device_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get readings for a specific device."""
        try:
            # We don't strictly enforce company_id here as the user likely already has access to the device
            # or this is called internally. To be safe, we skip filter as readings table has no company_id.
            query = """
                SELECT * FROM iot_readings 
                WHERE device_id = ? 
                ORDER BY timestamp DESC LIMIT ?
            """
            return self.execute_query(query, (device_id, limit), skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"Error getting readings: {e}")
            return []

    def get_alerts(self, company_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get alerts for a company."""
        try:
            self._ensure_context(company_id)
            # Join with iot_devices to filter by company_id safely
            query = """
                SELECT a.*, d.name as device_name 
                FROM iot_alerts a
                JOIN iot_devices d ON a.device_id = d.id
                WHERE d.company_id = ?
                ORDER BY a.timestamp DESC LIMIT ?
            """
            # We can use skip_tenant_filter=True because we manually handle company_id in the WHERE clause
            # via the join, and iot_alerts doesn't have company_id column for automatic injection.
            return self.execute_query(query, (company_id, limit), skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"Error getting alerts: {e}")
            return []
