import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SupportManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Support Tickets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    company_id INTEGER,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium',
                    category TEXT DEFAULT 'general',
                    status TEXT DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ticket Replies Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS support_replies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER,
                    user_id INTEGER,
                    message TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id)
                )
            """)
            
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Support tables init error: {e}")

    def create_ticket(self, user_id: int, company_id: int, subject: str, message: str, priority: str, category: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO support_tickets (user_id, company_id, subject, message, priority, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, company_id, subject, message, priority, category))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Create ticket error: {e}")
            return False

    def get_user_tickets(self, company_id: int, user_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM support_tickets WHERE company_id = ?"
            params = [company_id]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Get user tickets error: {e}")
            return []

    def get_user_tickets_count(self, company_id: int, user_id: Optional[int] = None) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM support_tickets WHERE company_id = ?"
            params = [company_id]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logging.error(f"Get user tickets count error: {e}")
            return 0

    def get_all_tickets(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Admin use only"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.*, c.name as company_name, u.username as user_name 
                FROM support_tickets t
                LEFT JOIN companies c ON t.company_id = c.id
                LEFT JOIN users u ON t.user_id = u.id
                ORDER BY t.created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Get all tickets error: {e}")
            return []

    def get_all_tickets_count(self) -> int:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM support_tickets")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logging.error(f"Get all tickets count error: {e}")
            return 0

    def get_ticket_details(self, ticket_id: int) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM support_tickets WHERE id = ?", (ticket_id,))
            ticket = cursor.fetchone()
            
            if not ticket:
                conn.close()
                return None
                
            result = dict(ticket)
            
            # Get replies
            cursor.execute("""
                SELECT r.*, u.username 
                FROM support_replies r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.ticket_id = ? 
                ORDER BY r.created_at ASC
            """, (ticket_id,))
            replies = cursor.fetchall()
            result['replies'] = [dict(r) for r in replies]
            
            conn.close()
            return result
        except Exception as e:
            logging.error(f"Get ticket details error: {e}")
            return None

    def add_reply(self, ticket_id: int, user_id: int, message: str, is_admin: bool = False) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO support_replies (ticket_id, user_id, message, is_admin)
                VALUES (?, ?, ?, ?)
            """, (ticket_id, user_id, message, 1 if is_admin else 0))
            
            # Update ticket updated_at
            status_update = ", status = 'answered'" if is_admin else ", status = 'customer_reply'"
            cursor.execute(f"UPDATE support_tickets SET updated_at = CURRENT_TIMESTAMP {status_update} WHERE id = ?", (ticket_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Add reply error: {e}")
            return False
