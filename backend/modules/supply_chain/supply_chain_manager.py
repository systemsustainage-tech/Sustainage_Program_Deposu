import sqlite3
import logging
import json
from typing import List, Dict, Optional, Any
from config.database import DB_PATH

class SupplyChainManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.ensure_tables()

    def ensure_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Audits Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                audit_date TEXT NOT NULL,
                auditor_name TEXT,
                audit_type TEXT,
                findings TEXT,
                non_conformities INTEGER DEFAULT 0,
                audit_score REAL,
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES supplier_profiles(id)
            )
        """)
        
        # Risks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplier_risks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                risk_category TEXT NOT NULL,
                risk_description TEXT,
                probability INTEGER CHECK(probability BETWEEN 1 AND 5),
                impact INTEGER CHECK(impact BETWEEN 1 AND 5),
                risk_score INTEGER,
                mitigation_plan TEXT,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES supplier_profiles(id)
            )
        """)
        
        conn.commit()
        conn.close()

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

    # --- Bulk Import & Alerts ---

    def import_risks_from_excel(self, company_id: int, file_path: str) -> Dict[str, int]:
        """
        Imports supplier risks from an Excel file.
        Expected columns: 'Tedarikçi Adı', 'Risk Kategorisi', 'Risk Açıklaması', 'Olasılık', 'Etki', 'Azaltma Planı'
        """
        import pandas as pd
        
        results = {"success": 0, "errors": 0, "details": []}
        
        try:
            df = pd.read_excel(file_path)
            # Normalize columns
            df.columns = [c.strip() for c in df.columns]
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    supplier_name = row.get('Tedarikçi Adı')
                    if not supplier_name:
                        continue
                        
                    # Find supplier ID
                    cursor.execute("SELECT id FROM supplier_profiles WHERE name = ? AND company_id = ?", (supplier_name, company_id))
                    supplier_row = cursor.fetchone()
                    
                    if not supplier_row:
                        results["errors"] += 1
                        results["details"].append(f"Row {index+2}: Supplier '{supplier_name}' not found.")
                        continue
                        
                    supplier_id = supplier_row[0]
                    
                    risk_category = row.get('Risk Kategorisi', 'General')
                    risk_desc = row.get('Risk Açıklaması', '')
                    probability = int(row.get('Olasılık', 1))
                    impact = int(row.get('Etki', 1))
                    mitigation = row.get('Azaltma Planı', '')
                    
                    # Validate probability and impact
                    probability = max(1, min(5, probability))
                    impact = max(1, min(5, impact))
                    risk_score = probability * impact
                    
                    cursor.execute("""
                        INSERT INTO supplier_risks (supplier_id, company_id, risk_category, risk_description, probability, impact, risk_score, mitigation_plan)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (supplier_id, company_id, risk_category, risk_desc, probability, impact, risk_score, mitigation))
                    
                    results["success"] += 1
                    
                except Exception as row_error:
                    results["errors"] += 1
                    results["details"].append(f"Row {index+2}: {str(row_error)}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Bulk import error: {e}")
            results["errors"] += 1
            results["details"].append(f"File Error: {str(e)}")
            
        return results

    def get_high_risk_alerts(self, company_id: int) -> List[Dict]:
        """
        Returns a list of high-risk suppliers (Score < 50) or those with recent high-risk incidents.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get suppliers with low overall risk score (calculated elsewhere, but assuming we store it or calculate it)
        # For now, let's use the 'risk_score' column in supplier_profiles if it exists, or aggregate from risks
        
        # Check if risk_score column exists in supplier_profiles (it should based on templates)
        # Assuming it is updated via triggers or manual updates.
        # Let's fallback to calculating from supplier_risks if needed.
        
        alerts = []
        
        # 1. High Risk Suppliers (Score < 50)
        cursor.execute("""
            SELECT id, name, risk_score FROM supplier_profiles
            WHERE company_id = ? AND risk_score < 50
            ORDER BY risk_score ASC
        """, (company_id,))
        
        high_risk_suppliers = cursor.fetchall()
        for s in high_risk_suppliers:
            alerts.append({
                "type": "High Risk Supplier",
                "message": f"Supplier '{s['name']}' has a CRITICAL risk score of {s['risk_score']}.",
                "link": f"/supply_chain/profile/{s['id']}",
                "level": "danger"
            })
            
        # 2. Recent High Impact Risks (Impact >= 4)
        cursor.execute("""
            SELECT r.id, s.name, r.risk_category, r.created_at
            FROM supplier_risks r
            JOIN supplier_profiles s ON r.supplier_id = s.id
            WHERE r.company_id = ? AND r.impact >= 4 AND r.status = 'Active'
            ORDER BY r.created_at DESC
            LIMIT 5
        """, (company_id,))
        
        recent_risks = cursor.fetchall()
        for r in recent_risks:
            alerts.append({
                "type": "Critical Risk Detected",
                "message": f"New critical risk '{r['risk_category']}' detected for {r['name']}.",
                "link": f"/supply_chain/profile/{s['id']}#risks",
                "level": "warning"
            })
            
        conn.close()
        return alerts

    def get_supplier_scorecard(self, supplier_id: int, company_id: int) -> Dict:
        """Aggregates data for a supplier scorecard."""
        profile = self.get_supplier(supplier_id, company_id)
        if not profile:
            return {}
            
        # Get latest assessment
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_assessments 
            WHERE supplier_id = ? AND company_id = ? 
            ORDER BY assessment_date DESC LIMIT 1
        """, (supplier_id, company_id))
        latest_assessment = cursor.fetchone()
        
        # Get audits stats
        cursor.execute("""
            SELECT COUNT(*) as audit_count, AVG(audit_score) as avg_audit_score, SUM(non_conformities) as total_nc
            FROM supplier_audits 
            WHERE supplier_id = ? AND company_id = ?
        """, (supplier_id, company_id))
        audit_stats = cursor.fetchone()
        
        # Get high risks
        cursor.execute("""
            SELECT * FROM supplier_risks 
            WHERE supplier_id = ? AND company_id = ? AND risk_score >= 12
            ORDER BY risk_score DESC
        """, (supplier_id, company_id))
        high_risks = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'profile': profile,
            'latest_assessment': dict(latest_assessment) if latest_assessment else None,
            'audit_stats': dict(audit_stats) if audit_stats else None,
            'high_risks': high_risks
        }

    def update_supplier_risk_score(self, supplier_id: int, company_id: int):
        """Calculates average risk score from assessments and updates profile."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate average score
        cursor.execute("""
            SELECT AVG(total_score) as avg_score 
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

    def add_assessment(self, supplier_id: int, company_id: int, assessment_date: str, total_score: float, risk_level: str, responses_json: Dict, environmental_score: float = 0, social_score: float = 0, governance_score: float = 0) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO supplier_assessments (
                    supplier_id, company_id, assessment_date, total_score, risk_level, responses_json,
                    environmental_score, social_score, governance_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_id, company_id, assessment_date, total_score, risk_level, json.dumps(responses_json),
                environmental_score, social_score, governance_score
            ))
            assessment_id = cursor.lastrowid
            conn.commit()
            # Update average risk score
            self.update_supplier_risk_score(supplier_id, company_id)
            return assessment_id
        except Exception as e:
            self.logger.error(f"Error adding assessment: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    # --- Supplier Audits ---

    def add_audit(self, supplier_id: int, company_id: int, data: Dict) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO supplier_audits (
                    supplier_id, company_id, audit_date, auditor_name, audit_type, 
                    findings, non_conformities, audit_score, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_id, company_id, data.get('audit_date'), data.get('auditor_name'), 
                data.get('audit_type'), data.get('findings'), data.get('non_conformities', 0), 
                data.get('audit_score'), data.get('status', 'Open')
            ))
            audit_id = cursor.lastrowid
            conn.commit()
            return audit_id
        except Exception as e:
            self.logger.error(f"Error adding audit: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_audits(self, supplier_id: int, company_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_audits 
            WHERE supplier_id = ? AND company_id = ?
            ORDER BY audit_date DESC
        """, (supplier_id, company_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # --- Supplier Risks ---

    def add_risk(self, supplier_id: int, company_id: int, data: Dict) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            prob = int(data.get('probability', 1))
            impact = int(data.get('impact', 1))
            risk_score = prob * impact
            
            cursor.execute("""
                INSERT INTO supplier_risks (
                    supplier_id, company_id, risk_category, risk_description, 
                    probability, impact, risk_score, mitigation_plan, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_id, company_id, data.get('risk_category'), data.get('risk_description'), 
                prob, impact, risk_score, data.get('mitigation_plan'), data.get('status', 'Active')
            ))
            risk_id = cursor.lastrowid
            conn.commit()
            return risk_id
        except Exception as e:
            self.logger.error(f"Error adding risk: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_risks(self, supplier_id: int, company_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM supplier_risks 
            WHERE supplier_id = ? AND company_id = ?
            ORDER BY risk_score DESC
        """, (supplier_id, company_id))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
