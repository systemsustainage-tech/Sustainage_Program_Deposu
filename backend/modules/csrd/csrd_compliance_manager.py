import logging
import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from config.database import DB_PATH

class CSRDComplianceManager:
    """CSRD Compliance Manager"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db_tables()
        
    def _init_db_tables(self):
        """Initialize CSRD tables"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
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
            conn.commit()
        except Exception as e:
            logging.error(f"CSRD table init error: {e}")
        finally:
            conn.close()

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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        records = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM csrd_materiality 
                WHERE company_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (company_id, limit))
            records = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"CSRD records error: {e}")
        finally:
            conn.close()
        return records

    def add_materiality_assessment(self, company_id: int, code: str, name: str, 
                                 impact: int, financial: int, rationale: str) -> bool:
        """Add materiality assessment"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO csrd_materiality (company_id, topic_code, topic_name, impact_score, financial_score, rationale, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (company_id, code, name, impact, financial, rationale))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"CSRD add error: {e}")
            return False
        finally:
            conn.close()
