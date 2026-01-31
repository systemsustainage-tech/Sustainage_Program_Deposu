
import logging
import sqlite3
import datetime
from flask import session, request

class DBLogHandler(logging.Handler):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    module TEXT,
                    message TEXT,
                    user_id INTEGER,
                    company_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def emit(self, record):
        try:
            # Skip db logging for some logger names to avoid recursion or noise
            if record.name.startswith('werkzeug') or record.name.startswith('sqlalchemy'):
                return

            msg = self.format(record)
            level = record.levelname
            module = record.name
            
            # Try to get user_id from session if available (Flask context)
            user_id = None
            company_id = None
            try:
                if session:
                    user_id = session.get('user_id')
                    company_id = session.get('company_id')
            except Exception:
                pass # Not in request context or session unavailable

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (level, module, message, user_id, company_id, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (level, module, msg, user_id, company_id))
            conn.commit()
            conn.close()
        except Exception:
            self.handleError(record)
