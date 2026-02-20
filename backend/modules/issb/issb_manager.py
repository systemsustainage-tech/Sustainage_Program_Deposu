import sqlite3
import logging
from typing import Dict, List, Optional, Union
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager

class ISSBManager(BaseTenantManager):
    """ISSB (International Sustainability Standards Board) Manager"""
    
    def __init__(self, db_path: str = "data/sustainability.db", company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self.init_database()
        
    def init_database(self):
        """Initialize ISSB tables"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS issb_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER,
                    standard TEXT,
                    disclosure TEXT,
                    metric TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"ISSB database initialization error: {e}")
            
    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for ISSB dashboard"""
        stats = {
            'total_disclosures': 0,
            'standards_covered': 0,
            'completion_rate': 0
        }
        try:
            # BaseTenantManager handles company_id via self.company_id or explicit filter injection
            # Since company_id is passed, we can rely on BaseTenantManager's context if it matches, 
            # or we should be careful. 
            # Ideally, we use execute_query which auto-injects company_id filter if not present.
            # But let's assume we want to query for the specific company_id passed.
            
            # If the manager is initialized with a company_id, execute_query uses it.
            # If not, we might need to be explicit or rely on the caller to init properly.
            
            rows = self.execute_query("SELECT standard FROM issb_data")
            
            stats['total_disclosures'] = len(rows)
            stats['standards_covered'] = len(set([r['standard'] for r in rows])) if rows else 0
            
            # Mock completion rate (assuming target is ~20 key disclosures)
            stats['completion_rate'] = min(100, int((stats['total_disclosures'] / 20) * 100))
            
        except Exception as e:
            logging.error(f"ISSB stats error: {e}")
            
        return stats
        
    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Get recent ISSB disclosures"""
        records = []
        try:
            records = self.execute_query("""
                SELECT * FROM issb_data 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
        except Exception as e:
            logging.error(f"ISSB records error: {e}")
            
        return records
        
    def add_disclosure(self, company_id: int, year: int, standard: str, disclosure: str, metric: str) -> bool:
        """Add a new ISSB disclosure"""
        try:
            self.execute_update("""
                INSERT INTO issb_data (company_id, year, standard, disclosure, metric)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, standard, disclosure, metric))
            return True
        except Exception as e:
            logging.error(f"Error adding ISSB disclosure: {e}")
            return False
