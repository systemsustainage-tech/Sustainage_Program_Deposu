import logging
import json
from typing import List, Dict, Optional, Any
from backend.core.base_manager import BaseTenantManager
try:
    from config.database import DB_PATH
except ImportError:
    from backend.config.database import DB_PATH

class SupplyChainManager(BaseTenantManager):
    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        self.logger = logging.getLogger(__name__)
        self.ensure_tables()

    def ensure_tables(self):
        # Audits Table
        self.db.execute_update("""
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
        self.db.execute_update("""
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
        
    # --- Supplier Profiles ---

    def add_supplier(self, company_id: int, name: str, sector: str, region: str, contact_info: str) -> int:
        sql = """
            INSERT INTO supplier_profiles (company_id, name, sector, region, contact_info)
            VALUES (?, ?, ?, ?, ?)
        """
        try:
            return self.execute_update(sql, (company_id, name, sector, region, contact_info), company_id=company_id)
        except Exception as e:
            self.logger.error(f"Error adding supplier: {e}")
            raise

    def get_suppliers(self, company_id: int) -> List[Dict]:
        sql = """
            SELECT * FROM supplier_profiles 
            WHERE company_id = ? 
            ORDER BY name ASC
        """
        rows = self.execute_query(sql, (company_id,), company_id=company_id)
        return [dict(row) for row in rows]

    def get_supplier(self, supplier_id: int, company_id: int) -> Optional[Dict]:
        sql = """
            SELECT * FROM supplier_profiles 
            WHERE id = ? AND company_id = ?
        """
        rows = self.execute_query(sql, (supplier_id, company_id), company_id=company_id)
        return dict(rows[0]) if rows else None

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
            
            for index, row in df.iterrows():
                try:
                    supplier_name = row.get('Tedarikçi Adı')
                    if not supplier_name:
                        continue
                        
                    # Find supplier ID
                    rows = self.execute_query(
                        "SELECT id FROM supplier_profiles WHERE name = ? AND company_id = ?", 
                        (supplier_name, company_id),
                        company_id=company_id
                    )
                    
                    if not rows:
                        results["errors"] += 1
                        results["details"].append(f"Row {index+2}: Supplier '{supplier_name}' not found.")
                        continue
                        
                    supplier_id = rows[0]['id']
                    
                    risk_category = row.get('Risk Kategorisi', 'General')
                    risk_desc = row.get('Risk Açıklaması', '')
                    probability = int(row.get('Olasılık', 1))
                    impact = int(row.get('Etki', 1))
                    mitigation = row.get('Azaltma Planı', '')
                    
                    # Validate probability and impact
                    probability = max(1, min(5, probability))
                    impact = max(1, min(5, impact))
                    risk_score = probability * impact
                    
                    self.execute_update("""
                        INSERT INTO supplier_risks (supplier_id, company_id, risk_category, risk_description, probability, impact, risk_score, mitigation_plan)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (supplier_id, company_id, risk_category, risk_desc, probability, impact, risk_score, mitigation), company_id=company_id)
                    
                    results["success"] += 1
                    
                except Exception as row_error:
                    results["errors"] += 1
                    results["details"].append(f"Row {index+2}: {str(row_error)}")
            
        except Exception as e:
            self.logger.error(f"Bulk import error: {e}")
            results["errors"] += 1
            results["details"].append(f"File Error: {str(e)}")
            
        return results

    def get_high_risk_alerts(self, company_id: int) -> List[Dict]:
        """
        Returns a list of high-risk suppliers (Score < 50) or those with recent high-risk incidents.
        """
        alerts = []
        
        # 1. High Risk Suppliers (Score < 50)
        sql_high_risk = """
            SELECT id, name, risk_score FROM supplier_profiles
            WHERE company_id = ? AND risk_score < 50
            ORDER BY risk_score ASC
        """
        high_risk_suppliers = self.execute_query(sql_high_risk, (company_id,), company_id=company_id)
        
        for s in high_risk_suppliers:
            alerts.append({
                "type": "High Risk Supplier",
                "message": f"Supplier '{s['name']}' has a CRITICAL risk score of {s['risk_score']}.",
                "link": f"/supply_chain/profile/{s['id']}",
                "level": "danger"
            })
            
        # 2. Recent High Impact Risks (Impact >= 4)
        sql_recent = """
            SELECT r.id, s.name, r.risk_category, r.created_at, s.id as supplier_id
            FROM supplier_risks r
            JOIN supplier_profiles s ON r.supplier_id = s.id
            WHERE r.company_id = ? AND r.impact >= 4 AND r.status = 'Active'
            ORDER BY r.created_at DESC
            LIMIT 5
        """
        recent_risks = self.execute_query(sql_recent, (company_id,), company_id=company_id)
        
        for r in recent_risks:
            alerts.append({
                "type": "Critical Risk Detected",
                "message": f"New critical risk '{r['risk_category']}' detected for {r['name']}.",
                "link": f"/supply_chain/profile/{r['supplier_id']}#risks",
                "level": "warning"
            })
            
        return alerts

    def get_supplier_scorecard(self, supplier_id: int, company_id: int) -> Dict:
        """Aggregates data for a supplier scorecard."""
        profile = self.get_supplier(supplier_id, company_id)
        if not profile:
            return {}
            
        # Get latest assessment
        sql_assess = """
            SELECT * FROM supplier_assessments 
            WHERE supplier_id = ? AND company_id = ? 
            ORDER BY assessment_date DESC LIMIT 1
        """
        rows = self.execute_query(sql_assess, (supplier_id, company_id), company_id=company_id)
        latest_assessment = rows[0] if rows else None
        
        # Get audits stats
        sql_audit = """
            SELECT COUNT(*) as audit_count, AVG(audit_score) as avg_audit_score, SUM(non_conformities) as total_nc
            FROM supplier_audits 
            WHERE supplier_id = ? AND company_id = ?
        """
        rows = self.execute_query(sql_audit, (supplier_id, company_id), company_id=company_id)
        audit_stats = rows[0] if rows else None
        
        # Get high risks
        sql_risks = """
            SELECT * FROM supplier_risks 
            WHERE supplier_id = ? AND company_id = ? AND risk_score >= 12
            ORDER BY risk_score DESC
        """
        high_risks = [dict(row) for row in self.execute_query(sql_risks, (supplier_id, company_id), company_id=company_id)]
        
        return {
            'profile': profile,
            'latest_assessment': dict(latest_assessment) if latest_assessment else None,
            'audit_stats': dict(audit_stats) if audit_stats else None,
            'high_risks': high_risks
        }

    def update_supplier_risk_score(self, supplier_id: int, company_id: int):
        """Calculates average risk score from assessments and updates profile."""
        # Calculate average score
        sql_avg = """
            SELECT AVG(total_score) as avg_score 
            FROM supplier_assessments 
            WHERE supplier_id = ? AND company_id = ?
        """
        rows = self.execute_query(sql_avg, (supplier_id, company_id), company_id=company_id)
        result = rows[0] if rows else None
        avg_score = result['avg_score'] if result and result['avg_score'] is not None else 0
        
        # Update profile
        self.execute_update("""
            UPDATE supplier_profiles 
            SET risk_score = ? 
            WHERE id = ?
        """, (avg_score, supplier_id), company_id=company_id)

    # --- Supplier Assessments ---

    def add_assessment(self, supplier_id: int, company_id: int, assessment_date: str, total_score: float, risk_level: str, responses_json: Dict, environmental_score: float = 0, social_score: float = 0, governance_score: float = 0) -> int:
        try:
            sql = """
                INSERT INTO supplier_assessments (
                    supplier_id, company_id, assessment_date, total_score, risk_level, responses_json,
                    environmental_score, social_score, governance_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            assessment_id = self.execute_update(sql, (
                supplier_id, company_id, assessment_date, total_score, risk_level, json.dumps(responses_json),
                environmental_score, social_score, governance_score
            ), company_id=company_id)
            
            # Update average risk score
            self.update_supplier_risk_score(supplier_id, company_id)
            return assessment_id
        except Exception as e:
            self.logger.error(f"Error adding assessment: {e}")
            raise

    # --- Supplier Audits ---

    def add_audit(self, supplier_id: int, company_id: int, data: Dict) -> int:
        try:
            sql = """
                INSERT INTO supplier_audits (
                    supplier_id, company_id, audit_date, auditor_name, audit_type, 
                    findings, non_conformities, audit_score, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            return self.execute_update(sql, (
                supplier_id, company_id, data.get('audit_date'), data.get('auditor_name'), 
                data.get('audit_type'), data.get('findings'), data.get('non_conformities', 0), 
                data.get('audit_score'), data.get('status', 'Open')
            ), company_id=company_id)
        except Exception as e:
            self.logger.error(f"Error adding audit: {e}")
            raise

    def get_audits(self, supplier_id: int, company_id: int) -> List[Dict]:
        sql = """
            SELECT * FROM supplier_audits 
            WHERE supplier_id = ? AND company_id = ?
            ORDER BY audit_date DESC
        """
        rows = self.execute_query(sql, (supplier_id, company_id), company_id=company_id)
        return [dict(row) for row in rows]

    # --- Supplier Risks ---

    def add_risk(self, supplier_id: int, company_id: int, data: Dict) -> int:
        try:
            prob = int(data.get('probability', 1))
            impact = int(data.get('impact', 1))
            risk_score = prob * impact
            
            sql = """
                INSERT INTO supplier_risks (
                    supplier_id, company_id, risk_category, risk_description, 
                    probability, impact, risk_score, mitigation_plan, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            return self.execute_update(sql, (
                supplier_id, company_id, data.get('risk_category'), data.get('risk_description'), 
                prob, impact, risk_score, data.get('mitigation_plan'), data.get('status', 'Active')
            ), company_id=company_id)
        except Exception as e:
            self.logger.error(f"Error adding risk: {e}")
            raise

    def get_risks(self, supplier_id: int, company_id: int) -> List[Dict]:
        sql = """
            SELECT * FROM supplier_risks 
            WHERE supplier_id = ? AND company_id = ?
            ORDER BY risk_score DESC
        """
        rows = self.execute_query(sql, (supplier_id, company_id), company_id=company_id)
        return [dict(row) for row in rows]
