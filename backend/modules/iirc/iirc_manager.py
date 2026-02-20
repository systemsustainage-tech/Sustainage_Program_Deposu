import logging
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager

class IIRCManager(BaseTenantManager):
    """IIRC (International Integrated Reporting Council) Manager"""
    
    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self.init_database()
        
    def init_database(self):
        """Initialize IIRC tables"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS integrated_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    report_name TEXT,
                    report_description TEXT,
                    financial_capital TEXT,
                    manufactured_capital TEXT,
                    intellectual_capital TEXT,
                    human_capital TEXT,
                    social_capital TEXT,
                    natural_capital TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Schema migration: check if report_description exists
            # Use skip_tenant_filter=True for PRAGMA queries to avoid any parsing issues, though base manager usually skips PRAGMA
            rows = self.execute_query("PRAGMA table_info(integrated_reports)", skip_tenant_filter=True)
            columns = [row['name'] for row in rows]
            if 'report_description' not in columns:
                try:
                    self.execute_update("ALTER TABLE integrated_reports ADD COLUMN report_description TEXT", skip_tenant_filter=True)
                except Exception as e:
                    logging.error(f"Migration error (adding report_description): {e}")

        except Exception as e:
            logging.error(f"IIRC database initialization error: {e}")
            
    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for IIRC dashboard"""
        stats = {'total_reports': 0, 'latest_year': '-'}
        try:
            rows = self.execute_query("SELECT year FROM integrated_reports WHERE company_id = ? ORDER BY year DESC LIMIT 1", (company_id,), skip_tenant_filter=True)
            if rows:
                stats['latest_year'] = rows[0]['year']
            
            rows_count = self.execute_query("SELECT COUNT(*) as count FROM integrated_reports WHERE company_id = ?", (company_id,), skip_tenant_filter=True)
            stats['total_reports'] = rows_count[0]['count'] if rows_count else 0
                
        except Exception as e:
            logging.error(f"IIRC stats error: {e}")
            
        return stats
        
    def get_recent_reports(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Get recent integrated reports"""
        try:
            rows = self.execute_query("""
                SELECT * FROM integrated_reports 
                WHERE company_id = ? 
                ORDER BY year DESC 
                LIMIT ?
            """, (company_id, limit), skip_tenant_filter=True)
            
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"IIRC reports error: {e}")
            return []
        
    def add_report(self, company_id: int, year: int, report_name: str, report_description: str = "", capitals: Dict = None) -> bool:
        """Add a new integrated report"""
        try:
            if capitals is None:
                capitals = {}
            
            self.execute_update("""
                INSERT INTO integrated_reports (
                    company_id, year, report_name, report_description,
                    financial_capital, manufactured_capital, intellectual_capital,
                    human_capital, social_capital, natural_capital
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, year, report_name, report_description,
                capitals.get('financial', ''),
                capitals.get('manufactured', ''),
                capitals.get('intellectual', ''),
                capitals.get('human', ''),
                capitals.get('social', ''),
                capitals.get('natural', '')
            ), skip_tenant_filter=True)
            return True
        except Exception as e:
            logging.error(f"Error adding IIRC report: {e}")
            return False
