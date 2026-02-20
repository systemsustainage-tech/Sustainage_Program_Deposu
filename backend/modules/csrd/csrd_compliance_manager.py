import logging
import os
from typing import Dict, List, Optional, Tuple
from backend.core.base_manager import BaseTenantManager

class CSRDComplianceManager(BaseTenantManager):
    """CSRD Compliance Manager"""
    
    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._init_db_tables()
        
    def _init_db_tables(self):
        """Initialize CSRD tables"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS csrd_materiality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_code TEXT,
                    topic_name TEXT,
                    impact_score INTEGER,
                    financial_score INTEGER,
                    rationale TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
        except Exception as e:
            logging.error(f"CSRD table init error: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for CSRD dashboard"""
        return {
            'compliance_score': 0,
            'completed_standards': 0,
            'total_standards': 12,
            'pending_actions': 0
        }
        
    def get_history(self, company_id: int) -> List[Dict]:
        """Get compliance history"""
        return []

    def get_recent_records(self, company_id: int, limit: int = 50) -> List[Dict]:
        """Get recent materiality assessments"""
        try:
            return self.select(
                'csrd_materiality',
                company_id=company_id,
                order_by='created_at DESC',
                limit=limit
            )
        except Exception as e:
            logging.error(f"CSRD records error: {e}")
            return []

    def add_materiality_assessment(self, company_id: int, code: str, name: str, 
                                 impact: int, financial: int, rationale: str) -> bool:
        """Add materiality assessment"""
        try:
            self.execute_update("""
                INSERT INTO csrd_materiality (company_id, topic_code, topic_name, impact_score, financial_score, rationale, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (company_id, code, name, impact, financial, rationale), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"CSRD add error: {e}")
            return False
