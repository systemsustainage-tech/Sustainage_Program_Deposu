from typing import Dict, List, Optional, Any
import logging
from backend.core.base_manager import BaseTenantManager

class VisualizationManager(BaseTenantManager):
    """Görselleştirme Modülü Yöneticisi"""

    def __init__(self, db_path: str, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self):
        """Gerekli tabloları oluşturur"""
        try:
            self.execute_query("""
                CREATE TABLE IF NOT EXISTS visualizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    chart_type TEXT NOT NULL, -- bar, line, pie, etc.
                    config TEXT, -- JSON config
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception as e:
            logging.error(f"VisualizationManager tables error: {e}")

    def get_stats(self, company_id: int) -> Dict[str, Any]:
        """İstatistikleri döner"""
        try:
            total_charts = self.execute_query(
                "SELECT COUNT(*) as count FROM visualizations WHERE company_id = ?", 
                (company_id,), company_id=company_id
            )[0]['count']
            
            return {
                'total_charts': total_charts,
                'dashboards': 1 # Default dashboard
            }
        except Exception as e:
            logging.error(f"VisualizationManager stats error: {e}")
            return {'total_charts': 0, 'dashboards': 0}

    def get_records(self, company_id: int) -> List[Dict[str, Any]]:
        """Kayıtları listeler"""
        try:
            return self.execute_query(
                "SELECT * FROM visualizations WHERE company_id = ? ORDER BY created_at DESC",
                (company_id,), company_id=company_id
            )
        except Exception as e:
            logging.error(f"VisualizationManager records error: {e}")
            return []

    def add_visualization(self, company_id: int, title: str, chart_type: str, config: str = '{}') -> bool:
        """Yeni görselleştirme ekler"""
        try:
            self.execute_update(
                "INSERT INTO visualizations (company_id, title, chart_type, config) VALUES (?, ?, ?, ?)",
                (company_id, title, chart_type, config),
                company_id=company_id
            )
            return True
        except Exception as e:
            logging.error(f"VisualizationManager add_visualization error: {e}")
            return False
