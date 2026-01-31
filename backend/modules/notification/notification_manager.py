import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

class NotificationManager:
    """
    Manages user notifications.
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to standard path if not provided
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        else:
            self.db_path = db_path
            
        self._ensure_table()
        
    def _ensure_table(self):
        """Ensure notifications table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info', -- info, success, warning, error
                link TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
    def create_notification(self, user_id: int, title: str, message: str, type: str = 'info', link: str = None) -> int:
        """Create a new notification."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (user_id, title, message, type, link, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, 0, datetime('now'))
            """, (user_id, title, message, type, link))
            conn.commit()
            notification_id = cursor.lastrowid
            conn.close()
            return notification_id
        except Exception as e:
            logging.error(f"Error creating notification: {e}")
            return -1
            
    def get_unread_notifications(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get unread notifications for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error fetching notifications: {e}")
            return []
            
    def get_all_notifications(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all notifications for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notifications 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error fetching notifications: {e}")
            return []
            
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error marking notification as read: {e}")
            return False
            
    def mark_all_as_read(self, user_id: int) -> bool:
        """Mark all notifications for a user as read."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error marking all notifications as read: {e}")
            return False
            
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logging.error(f"Error counting notifications: {e}")
            return 0
