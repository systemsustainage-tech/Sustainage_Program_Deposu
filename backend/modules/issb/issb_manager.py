import sqlite3
import logging
from typing import Dict, List, Optional, Union

class ISSBManager:
    """ISSB (International Sustainability Standards Board) Manager"""
    
    def __init__(self, db_path: str = "data/sustainability.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize ISSB tables"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
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
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"ISSB database initialization error: {e}")
        finally:
            conn.close()
            
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for ISSB dashboard"""
        conn = self.get_connection()
        stats = {
            'total_disclosures': 0,
            'standards_covered': 0,
            'completion_rate': 0
        }
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT standard FROM issb_data WHERE company_id = ?", (company_id,))
            rows = cursor.fetchall()
            
            stats['total_disclosures'] = len(rows)
            stats['standards_covered'] = len(set([r[0] for r in rows])) if rows else 0
            
            # Mock completion rate (assuming target is ~20 key disclosures)
            stats['completion_rate'] = min(100, int((stats['total_disclosures'] / 20) * 100))
            
        except Exception as e:
            logging.error(f"ISSB stats error: {e}")
        finally:
            conn.close()
            
        return stats
        
    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Get recent ISSB disclosures"""
        conn = self.get_connection()
        records = []
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM issb_data 
                WHERE company_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (company_id, limit))
            
            records = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"ISSB records error: {e}")
        finally:
            conn.close()
            
        return records
        
    def add_disclosure(self, company_id: int, year: int, standard: str, disclosure: str, metric: str) -> bool:
        """Add a new ISSB disclosure"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO issb_data (company_id, year, standard, disclosure, metric)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, standard, disclosure, metric))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding ISSB disclosure: {e}")
            return False
        finally:
            conn.close()
