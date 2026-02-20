import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from backend.core.base_manager import BaseTenantManager

class NotificationManager(BaseTenantManager):
    """
    Manages user notifications with multi-tenant support.
    """
    
    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        if db_path is None:
            # Default to standard path if not provided
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
            
        super().__init__(db_path, company_id)
        self._ensure_table()
        
    def _ensure_table(self):
        """Ensure notifications table exists and has correct schema."""
        try:
            # We use skip_tenant_filter=True for DDL
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL DEFAULT 1,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT DEFAULT 'info', -- info, success, warning, error
                    link TEXT,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)
            
            # Check if company_id column exists (migration support)
            try:
                # Use raw connection for PRAGMA
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA table_info(notifications)")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    if 'company_id' not in columns:
                        logging.info("Migrating notifications table: Adding company_id column")
                        cursor.execute("ALTER TABLE notifications ADD COLUMN company_id INTEGER NOT NULL DEFAULT 1")
                        conn.commit()
            except Exception as e:
                logging.error(f"Error migrating notifications table: {e}")

            # Create index for performance
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_notifications_company_user ON notifications(company_id, user_id)", skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Error ensuring notifications table: {e}")
        
    def create_notification(self, user_id: int, title: str, message: str, type: str = 'info', link: str = None, company_id: int = None) -> int:
        """Create a new notification."""
        try:
            # Determine company_id: passed arg > self.company_id > default 1
            cid = company_id if company_id is not None else (self.company_id if self.company_id else 1)
            
            # Use execute_update which handles connection and returns lastrowid
            # We manually specify company_id in INSERT, so we might not need auto-injection if we use skip_tenant_filter=True
            # But BaseTenantManager is designed for WHERE clauses. For INSERT, we usually write the SQL explicitly.
            
            return self.execute_update("""
                INSERT INTO notifications (company_id, user_id, title, message, type, link, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, datetime('now'))
            """, (cid, user_id, title, message, type, link), skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Error creating notification: {e}")
            return -1
            
    def get_unread_notifications(self, user_id: int, limit: int = 10, company_id: int = None) -> List[Dict[str, Any]]:
        """Get unread notifications for a user."""
        try:
            # If company_id is not passed, use self.company_id. 
            # If both are None (e.g. system context), we might fetch for all companies (admin) or fallback to 1.
            # But strictly we should filter by company.
            
            # If self.company_id is set, execute_query will automatically add "AND company_id = ?" if we don't skip.
            # But we need to be careful about WHERE clause structure injection.
            # BaseTenantManager typically expects "SELECT ... FROM ... WHERE ..." and appends " AND company_id = ?"
            
            # Let's rely on manual parameter passing for clarity and safety here, 
            # using skip_tenant_filter=True but manually adding the check.
            
            cid = company_id if company_id is not None else self.company_id
            
            if cid:
                return self.execute_query("""
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND company_id = ? AND is_read = 0
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, cid, limit), skip_tenant_filter=True)
            else:
                # Fallback for when no company context is available (should be rare)
                return self.execute_query("""
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND is_read = 0
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit), skip_tenant_filter=True)
                
        except Exception as e:
            logging.error(f"Error fetching notifications: {e}")
            return []
            
    def get_all_notifications(self, user_id: int, limit: int = 50, company_id: int = None) -> List[Dict[str, Any]]:
        """Get all notifications for a user."""
        try:
            cid = company_id if company_id is not None else self.company_id
            
            if cid:
                return self.execute_query("""
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND company_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, cid, limit), skip_tenant_filter=True)
            else:
                return self.execute_query("""
                    SELECT * FROM notifications 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (user_id, limit), skip_tenant_filter=True)
                
        except Exception as e:
            logging.error(f"Error fetching notifications: {e}")
            return []
            
    def mark_as_read(self, notification_id: int, company_id: int = None) -> bool:
        """Mark a notification as read."""
        try:
            cid = company_id if company_id is not None else self.company_id
            
            if cid:
                rows = self.execute_update("""
                    UPDATE notifications SET is_read = 1 
                    WHERE id = ? AND company_id = ?
                """, (notification_id, cid), skip_tenant_filter=True)
            else:
                rows = self.execute_update("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,), skip_tenant_filter=True)
                
            return rows > 0
        except Exception as e:
            logging.error(f"Error marking notification as read: {e}")
            return False
            
    def mark_all_as_read(self, user_id: int, company_id: int = None) -> bool:
        """Mark all notifications for a user as read."""
        try:
            cid = company_id if company_id is not None else self.company_id
            
            if cid:
                rows = self.execute_update("""
                    UPDATE notifications SET is_read = 1 
                    WHERE user_id = ? AND company_id = ?
                """, (user_id, cid), skip_tenant_filter=True)
            else:
                rows = self.execute_update("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,), skip_tenant_filter=True)
                
            return rows > 0
        except Exception as e:
            logging.error(f"Error marking all notifications as read: {e}")
            return False
            
    def get_unread_count(self, user_id: int, company_id: int = None) -> int:
        """Get count of unread notifications."""
        try:
            cid = company_id if company_id is not None else self.company_id
            
            if cid:
                result = self.execute_query("""
                    SELECT COUNT(*) as count FROM notifications 
                    WHERE user_id = ? AND company_id = ? AND is_read = 0
                """, (user_id, cid), skip_tenant_filter=True)
            else:
                result = self.execute_query("""
                    SELECT COUNT(*) as count FROM notifications 
                    WHERE user_id = ? AND is_read = 0
                """, (user_id,), skip_tenant_filter=True)
                
            return result[0]['count'] if result else 0
        except Exception as e:
            logging.error(f"Error counting notifications: {e}")
            return 0
