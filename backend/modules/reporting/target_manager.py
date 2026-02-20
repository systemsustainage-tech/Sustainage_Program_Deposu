import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager

class TargetManager(BaseTenantManager):
    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self._ensure_table()
    
    def _ensure_table(self):
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS company_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                metric_type TEXT NOT NULL, -- carbon, energy, water, waste
                baseline_year INTEGER,
                baseline_value REAL,
                target_year INTEGER,
                target_value REAL,
                current_value REAL,
                status TEXT DEFAULT 'pending', -- on_track, behind, achieved, pending
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
    
    def get_targets(self, company_id: int) -> List[Dict[str, Any]]:
        rows = self.execute_query("SELECT * FROM company_targets WHERE company_id = ?", (company_id,), company_id=company_id)
        return [dict(row) for row in rows]
    
    def add_target(self, company_id: int, data: Dict[str, Any]):
        self.execute_update("""
            INSERT INTO company_targets (company_id, name, metric_type, baseline_year, baseline_value, target_year, target_value, current_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            company_id, 
            data['name'], 
            data['metric_type'], 
            data['baseline_year'], 
            data['baseline_value'], 
            data['target_year'], 
            data['target_value']
        ), company_id=company_id)
        
        self.update_progress(company_id)

    def update_progress(self, company_id: int):
        """
        Recalculates current values and status for all targets of a company.
        This should be called when new data is entered.
        """
        try:
            targets = self.get_targets(company_id)
            if not targets:
                return

            current_year = datetime.now().year
            
            for target in targets:
                try:
                    metric = target['metric_type']
                    current_val = 0
                    
                    # Fetch latest actual data (simplified logic)
                    row = None
                    if metric == 'carbon':
                        # Check table existence first or handle error via try/except in query execution if needed
                        # But BaseTenantManager catches exceptions.
                        # We should check if tables exist or assume they do.
                        # Using execute_query safely.
                        try:
                            rows = self.execute_query("SELECT SUM(total_emissions) as val FROM carbon_emissions WHERE company_id = ? AND year = ?", (company_id, current_year), company_id=company_id)
                            row = rows[0] if rows else None
                        except Exception:
                            pass
                    elif metric == 'energy':
                        try:
                            rows = self.execute_query("SELECT SUM(consumption_amount) as val FROM energy_consumption WHERE company_id = ? AND year = ?", (company_id, current_year), company_id=company_id)
                            row = rows[0] if rows else None
                        except Exception:
                            pass
                    elif metric == 'water':
                        try:
                            rows = self.execute_query("SELECT SUM(consumption_amount) as val FROM water_consumption WHERE company_id = ? AND year = ?", (company_id, current_year), company_id=company_id)
                            row = rows[0] if rows else None
                        except Exception:
                            pass
                    elif metric == 'waste':
                        try:
                            rows = self.execute_query("SELECT SUM(amount) as val FROM waste_generation WHERE company_id = ? AND year = ?", (company_id, current_year), company_id=company_id)
                            row = rows[0] if rows else None
                        except Exception:
                            pass

                    if row and row['val']:
                        current_val = row['val']

                    # Determine status
                    status = 'pending'
                    if target['baseline_value'] and target['target_value']:
                        if current_val <= target['target_value']:
                            status = 'achieved'
                        elif current_val < target['baseline_value']:
                            status = 'on_track'
                        else:
                            status = 'behind'
                    
                    # Update DB
                    self.execute_update("UPDATE company_targets SET current_value = ?, status = ? WHERE id = ?", (current_val, status, target['id']), company_id=company_id)
                    
                except Exception as e:
                    logging.error(f"Error updating target {target.get('id')}: {e}")
                    
        except Exception as e:
            logging.error(f"Error in update_progress: {e}")
