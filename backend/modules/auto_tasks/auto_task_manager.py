from typing import Dict, List, Optional, Any
import logging
from backend.core.base_manager import BaseTenantManager

class AutoTaskManager(BaseTenantManager):
    """Otomatik Görevler Modülü Yöneticisi"""

    def __init__(self, db_path: str, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self):
        """Gerekli tabloları oluşturur"""
        try:
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS auto_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    schedule TEXT, -- cron format or description
                    status TEXT DEFAULT 'active', -- active, paused, completed
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if company_id column exists (for backward compatibility if table existed)
            # Since this is new, we assume it's fine, but good practice to verify in existing systems.
            # Here we just create if not exists.
            
        except Exception as e:
            logging.error(f"AutoTaskManager tables error: {e}")

    def get_stats(self, company_id: int) -> Dict[str, Any]:
        """İstatistikleri döner"""
        try:
            total_tasks = self.execute_query(
                "SELECT COUNT(*) as count FROM auto_tasks WHERE company_id = ?", 
                (company_id,), company_id=company_id
            )[0]['count']
            
            active_tasks = self.execute_query(
                "SELECT COUNT(*) as count FROM auto_tasks WHERE company_id = ? AND status = 'active'", 
                (company_id,), company_id=company_id
            )[0]['count']
            
            return {
                'total_tasks': total_tasks,
                'active_tasks': active_tasks,
                'completed_tasks': total_tasks - active_tasks
            }
        except Exception as e:
            logging.error(f"AutoTaskManager stats error: {e}")
            return {'total_tasks': 0, 'active_tasks': 0, 'completed_tasks': 0}

    def get_records(self, company_id: int) -> List[Dict[str, Any]]:
        """Kayıtları listeler"""
        try:
            return self.execute_query(
                "SELECT * FROM auto_tasks WHERE company_id = ? ORDER BY created_at DESC",
                (company_id,), company_id=company_id
            )
        except Exception as e:
            logging.error(f"AutoTaskManager records error: {e}")
            return []

    def add_task(self, company_id: int, title: str, description: str, schedule: str = 'daily') -> bool:
        """Yeni görev ekler"""
        try:
            self.execute_update(
                "INSERT INTO auto_tasks (company_id, title, description, schedule) VALUES (?, ?, ?, ?)",
                (company_id, title, description, schedule),
                company_id=company_id
            )
            return True
        except Exception as e:
            logging.error(f"AutoTaskManager add_task error: {e}")
            return False
