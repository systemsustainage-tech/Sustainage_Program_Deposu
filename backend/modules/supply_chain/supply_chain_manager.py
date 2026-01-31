
import sqlite3
import logging
import json
from typing import List, Dict, Optional, Any
from config.database import DB_PATH

class SupplyChainManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # --- Supplier Profiles ---

    def add_supplier(self, company_id: int, name: str, sector: str, region: str, contact_info: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO supplier_profiles (company_id, name, sector, region, contact_info)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, name, sector, region, contact_info))
            supplier_id = cursor.lastrowid
            conn.commit()
            return supplier_id
        except Exception as e:
            self.logger.error(f"Error adding supplier: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_suppliers(self, company_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_profiles 
            WHERE company_id = ? 
            ORDER BY name ASC
        """, (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_supplier(self, supplier_id: int, company_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_profiles 
            WHERE id = ? AND company_id = ?
        """, (supplier_id, company_id))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_supplier_risk_score(self, supplier_id: int, company_id: int):
        """Calculates average risk score from assessments and updates profile."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate average score
        cursor.execute("""
            SELECT AVG(score) as avg_score 
            FROM supplier_assessments 
            WHERE supplier_id = ? AND company_id = ?
        """, (supplier_id, company_id))
        result = cursor.fetchone()
        avg_score = result['avg_score'] if result and result['avg_score'] is not None else 0
        
        # Update profile
        cursor.execute("""
            UPDATE supplier_profiles 
            SET risk_score = ? 
            WHERE id = ?
        """, (avg_score, supplier_id))
        conn.commit()
        conn.close()

    # --- Supplier Assessments ---

    def add_assessment(self, supplier_id: int, company_id: int, assessment_date: str, score: float, risk_level: str, details: Dict) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO supplier_assessments (supplier_id, company_id, assessment_date, score, risk_level, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (supplier_id, company_id, assessment_date, score, risk_level, json.dumps(details)))
            assessment_id = cursor.lastrowid
            conn.commit()
            
            # Update main profile risk score
            self.update_supplier_risk_score(supplier_id, company_id)
            
            return assessment_id
        except Exception as e:
            self.logger.error(f"Error adding assessment: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_assessments(self, supplier_id: int, company_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_assessments 
            WHERE supplier_id = ? AND company_id = ? 
            ORDER BY assessment_date DESC
        """, (supplier_id, company_id))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            d = dict(row)
            if d['details']:
                try:
                    d['details'] = json.loads(d['details'])
                except:
                    d['details'] = {}
            results.append(d)
        return results

    def get_assessment(self, assessment_id: int, company_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_assessments 
            WHERE id = ? AND company_id = ?
        """, (assessment_id, company_id))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            d = dict(row)
            if d['details']:
                try:
                    d['details'] = json.loads(d['details'])
                except:
                    d['details'] = {}
            return d
        return None
