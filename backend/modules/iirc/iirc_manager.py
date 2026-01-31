import sqlite3
import logging
import os
from typing import Dict, List, Optional, Union
from config.database import DB_PATH

class IIRCManager:
    """IIRC (International Integrated Reporting Council) Manager"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = DB_PATH
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
        self.init_database()
        
    def init_database(self):
        """Initialize IIRC tables"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
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
            cursor.execute("PRAGMA table_info(integrated_reports)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'report_description' not in columns:
                try:
                    cursor.execute("ALTER TABLE integrated_reports ADD COLUMN report_description TEXT")
                except Exception as e:
                    logging.error(f"Migration error (adding report_description): {e}")

            conn.commit()
        except Exception as e:
            logging.error(f"IIRC database initialization error: {e}")
        finally:
            conn.close()
            
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for IIRC dashboard"""
        conn = self.get_connection()
        stats = {'total_reports': 0, 'latest_year': '-'}
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT year FROM integrated_reports WHERE company_id = ? ORDER BY year DESC LIMIT 1", (company_id,))
            row = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) FROM integrated_reports WHERE company_id = ?", (company_id,))
            count = cursor.fetchone()[0]
            
            stats['total_reports'] = count
            if row:
                stats['latest_year'] = row['year']
                
        except Exception as e:
            logging.error(f"IIRC stats error: {e}")
        finally:
            conn.close()
            
        return stats
        
    def get_recent_reports(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Get recent integrated reports"""
        conn = self.get_connection()
        reports = []
        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM integrated_reports 
                WHERE company_id = ? 
                ORDER BY year DESC 
                LIMIT ?
            """, (company_id, limit))
            
            reports = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"IIRC reports error: {e}")
        finally:
            conn.close()
            
        return reports
        
    def add_report(self, company_id: int, year: int, report_name: str, report_description: str = "", capitals: Dict = None) -> bool:
        """Add a new integrated report"""
        conn = self.get_connection()
        try:
            if capitals is None:
                capitals = {}
            
            # Debug logging
            with open(r'c:\SUSTAINAGESERVER\error_log.txt', 'a') as f:
                f.write(f"IIRC Save Attempt: cid={company_id}, year={year}, name={report_name}\n")

            cursor = conn.cursor()
            cursor.execute("""
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
            ))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding IIRC report: {e}")
            with open(r'c:\SUSTAINAGESERVER\error_log.txt', 'a') as f:
                f.write(f"IIRC Save Error: {e}\n")
            return False
        finally:
            conn.close()
