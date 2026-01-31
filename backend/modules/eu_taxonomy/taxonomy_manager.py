import logging
import sqlite3
import os
from typing import Dict, List, Optional, Any
from config.database import DB_PATH

class EUTaxonomyManager:
    """EU Taxonomy Manager"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db_tables()
        
    def _init_db_tables(self):
        """Initialize Taxonomy tables"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS taxonomy_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER,
                    activity_name TEXT,
                    nace_code TEXT,
                    environmental_objective TEXT,
                    turnover_amount REAL,
                    turnover_aligned REAL,
                    capex_amount REAL,
                    capex_aligned REAL,
                    opex_amount REAL,
                    opex_aligned REAL,
                    substantial_contribution BOOLEAN DEFAULT 0,
                    dnsh_compliance BOOLEAN DEFAULT 0,
                    minimum_safeguards BOOLEAN DEFAULT 0,
                    documentation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"Taxonomy table init error: {e}")
        finally:
            conn.close()

    def add_activity(self, company_id: int, activity_data: Dict[str, Any]) -> bool:
        """Add a new taxonomy activity"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            
            # Calculate aligned amounts based on percentage
            aligned_pct = float(activity_data.get('aligned', 0))
            turnover = float(activity_data.get('turnover', 0))
            capex = float(activity_data.get('capex', 0))
            opex = float(activity_data.get('opex', 0))
            
            turnover_aligned = turnover * (aligned_pct / 100.0)
            capex_aligned = capex * (aligned_pct / 100.0)
            opex_aligned = opex * (aligned_pct / 100.0)
            
            cursor.execute("""
                INSERT INTO taxonomy_activities (
                    company_id, year, activity_name, nace_code, environmental_objective,
                    turnover_amount, turnover_aligned,
                    capex_amount, capex_aligned,
                    opex_amount, opex_aligned,
                    substantial_contribution, dnsh_compliance, minimum_safeguards,
                    documentation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                activity_data.get('year'),
                activity_data.get('activity_name'),
                activity_data.get('nace_code'),
                activity_data.get('env_objective'),
                turnover, turnover_aligned,
                capex, capex_aligned,
                opex, opex_aligned,
                1 if activity_data.get('substantial') else 0,
                1 if activity_data.get('dnsh') else 0,
                1 if activity_data.get('minimum') else 0,
                activity_data.get('documentation')
            ))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Taxonomy add activity error: {e}")
            return False
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Get summary statistics for Taxonomy dashboard"""
        return self.get_taxonomy_stats(company_id)
        
    def get_history(self, company_id: int) -> List[Dict]:
        """Get history"""
        return []

    def get_taxonomy_stats(self, company_id: int) -> Dict:
        """Get taxonomy statistics"""
        conn = sqlite3.connect(self.db_path)
        stats = {
            'turnover': 0, 'turnover_aligned': 0, 'turnover_pct': 0,
            'capex': 0, 'capex_aligned': 0, 'capex_pct': 0,
            'opex': 0, 'opex_aligned': 0, 'opex_pct': 0
        }
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    SUM(turnover_amount), SUM(turnover_aligned),
                    SUM(capex_amount), SUM(capex_aligned),
                    SUM(opex_amount), SUM(opex_aligned)
                FROM taxonomy_activities 
                WHERE company_id = ?
            """, (company_id,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                stats['turnover'] = row[0]
                stats['turnover_aligned'] = row[1] or 0
                stats['capex'] = row[2] or 0
                stats['capex_aligned'] = row[3] or 0
                stats['opex'] = row[4] or 0
                stats['opex_aligned'] = row[5] or 0
                
                if stats['turnover'] > 0:
                    stats['turnover_pct'] = int((stats['turnover_aligned'] / stats['turnover']) * 100)
                if stats['capex'] > 0:
                    stats['capex_pct'] = int((stats['capex_aligned'] / stats['capex']) * 100)
                if stats['opex'] > 0:
                    stats['opex_pct'] = int((stats['opex_aligned'] / stats['opex']) * 100)
                    
        except Exception as e:
            logging.error(f"Taxonomy stats error: {e}")
        finally:
            conn.close()
        return stats

    def get_taxonomy_activities(self, company_id: int) -> List[Dict]:
        """Get taxonomy activities"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        activities = []
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM taxonomy_activities 
                WHERE company_id = ? 
                ORDER BY created_at DESC
            """, (company_id,))
            activities = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Taxonomy activities error: {e}")
        finally:
            conn.close()
        return activities

    def get_framework_mappings(self) -> List[Dict]:
        """Get framework mappings (Mock for now)"""
        return [
            {'source': 'EU Taxonomy', 'target': 'SDG 13', 'description': 'Climate Change Mitigation'},
            {'source': 'EU Taxonomy', 'target': 'SDG 15', 'description': 'Protection of Ecosystems'}
        ]
