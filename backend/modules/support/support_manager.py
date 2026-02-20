import logging
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager

class SupportManager(BaseTenantManager):
    def __init__(self, db_path: str, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._init_tables()

    def _init_tables(self):
        try:
            # Support Tickets Table
            self.execute_update("""
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
            self.execute_update("""
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
        except Exception as e:
            logging.error(f"Support tables init error: {e}")

    def create_ticket(self, user_id: int, company_id: int, subject: str, message: str, priority: str, category: str) -> bool:
        try:
            self.execute_update("""
                INSERT INTO support_tickets (user_id, company_id, subject, message, priority, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, company_id, subject, message, priority, category), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Create ticket error: {e}")
            return False

    def get_user_tickets(self, company_id: int, user_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict]:
        try:
            query = "SELECT * FROM support_tickets WHERE company_id = ?"
            params = [company_id]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            return self.execute_query(query, tuple(params), company_id=company_id)
        except Exception as e:
            logging.error(f"Get user tickets error: {e}")
            return []

    def get_user_tickets_count(self, company_id: int, user_id: Optional[int] = None) -> int:
        try:
            query = "SELECT COUNT(*) as count FROM support_tickets WHERE company_id = ?"
            params = [company_id]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            rows = self.execute_query(query, tuple(params), company_id=company_id)
            return rows[0]['count'] if rows else 0
        except Exception as e:
            logging.error(f"Get user tickets count error: {e}")
            return 0
