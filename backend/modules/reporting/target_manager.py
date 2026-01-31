import sqlite3
import os
import json
import logging
from datetime import datetime
from config.database import DB_PATH

class TargetManager:
    def __init__(self, db_path=None):
        self.db_path = db_path if db_path else DB_PATH
        self._ensure_table()
    
    def _get_conn(self):
        return sqlite3.connect(self.db_path)
    
    def _ensure_table(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def get_targets(self, company_id):
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM company_targets WHERE company_id = ?", (company_id,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_target(self, company_id, data):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO company_targets (company_id, name, metric_type, baseline_year, baseline_value, target_year, target_value, current_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (company_id, data['name'], data['metric_type'], data['baseline_year'], data['baseline_value'], data['target_year'], data['target_value']))
        conn.commit()
        conn.close()
        self.update_progress(company_id)

    def update_progress(self, company_id):
        """
        Recalculates current values and status for all targets of a company.
        This should be called when new data is entered.
        """
        try:
            targets = self.get_targets(company_id)
            if not targets:
                return

            conn = self._get_conn()
            cursor = conn.cursor()
            
            for target in targets:
                try:
                    metric = target['metric_type']
                    current_val = 0
                    
                    # Fetch latest actual data (simplified logic)
                    if metric == 'carbon':
                        # Check table existence first or handle error
                        row = cursor.execute("SELECT SUM(total_emissions) FROM carbon_emissions WHERE company_id = ? AND year = ?", (company_id, datetime.now().year)).fetchone()
                        current_val = row[0] if row and row[0] else 0
                    elif metric == 'energy':
                        row = cursor.execute("SELECT SUM(consumption_amount) FROM energy_consumption WHERE company_id = ? AND year = ?", (company_id, datetime.now().year)).fetchone()
                        current_val = row[0] if row and row[0] else 0
                    elif metric == 'water':
                        row = cursor.execute("SELECT SUM(consumption_amount) FROM water_consumption WHERE company_id = ? AND year = ?", (company_id, datetime.now().year)).fetchone()
                        current_val = row[0] if row and row[0] else 0
                    elif metric == 'waste':
                        row = cursor.execute("SELECT SUM(amount) FROM waste_generation WHERE company_id = ? AND year = ?", (company_id, datetime.now().year)).fetchone()
                        current_val = row[0] if row and row[0] else 0

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
                    cursor.execute("UPDATE company_targets SET current_value = ?, status = ? WHERE id = ?", (current_val, status, target['id']))
                except Exception as e:
                    logging.error(f"Error updating target {target.get('id')}: {e}")
                    continue

            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Target update_progress error: {e}")