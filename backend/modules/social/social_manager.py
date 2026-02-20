# -*- coding: utf-8 -*-
"""
Social Performance Manager
===========================
Central manager for all social performance metrics and data.
"""

import datetime
import os
import logging
from typing import Dict, List, Tuple, Optional, Union

try:
    from backend.core.base_manager import BaseTenantManager
    from config.database import DB_PATH
except ImportError:
    from backend.core.base_manager import BaseTenantManager
    from backend.config.database import DB_PATH

class SocialManager(BaseTenantManager):
    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None):
        if db_path is None:
            db_path = DB_PATH
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        super().__init__(db_path, company_id)
        self.init_database()

    def init_database(self):
        """Initialize social performance tables"""
        # Tables definition
        tables = [
            """CREATE TABLE IF NOT EXISTS hr_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                employee_count INTEGER,
                gender TEXT,
                department TEXT,
                age_group TEXT,
                year INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS ohs_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                incident_type TEXT,
                date DATE,
                severity TEXT,
                description TEXT,
                lost_time_days INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                training_name TEXT,
                hours REAL,
                participants INTEGER,
                date DATE,
                category TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS employee_satisfaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                year INTEGER,
                survey_date DATE,
                satisfaction_score REAL,
                turnover_rate REAL,
                participation_rate REAL,
                comments TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS community_investment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                project_name TEXT,
                investment_amount REAL,
                beneficiaries_count INTEGER,
                impact_description TEXT,
                date DATE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS human_rights_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                site_name TEXT,
                assessment_date DATE,
                risk_level TEXT,
                incidents_found INTEGER DEFAULT 0,
                mitigation_plan TEXT,
                status TEXT DEFAULT 'Completed',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS fair_labor_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                site_name TEXT,
                audit_date DATE,
                forced_labor_risk TEXT,
                child_labor_risk TEXT,
                wage_compliance TEXT,
                union_rights TEXT,
                audit_score REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS consumer_complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                complaint_date DATE,
                category TEXT,
                severity TEXT,
                description TEXT,
                resolution_status TEXT,
                satisfaction_score REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        
        for table_sql in tables:
            self.execute_query(table_sql)


    def add_human_rights_assessment(self, company_id: int, data: Dict) -> bool:
        """Add a new human rights assessment"""
        try:
            insert_data = {
                'site_name': data.get('site_name'),
                'assessment_date': data.get('assessment_date'),
                'risk_level': data.get('risk_level'),
                'incidents_found': data.get('incidents_found', 0),
                'mitigation_plan': data.get('mitigation_plan'),
                'status': data.get('status', 'Completed')
            }
            self.insert('human_rights_assessments', insert_data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding human rights assessment: {e}")
            return False

    def get_human_rights_assessments(self, company_id: int) -> List[Dict]:
        """Get all human rights assessments"""
        return self.select('human_rights_assessments', company_id=company_id, order_by='assessment_date DESC')

    def add_labor_audit(self, company_id: int, data: Dict) -> bool:
        """Add a new fair labor audit"""
        try:
            insert_data = {
                'site_name': data.get('site_name'),
                'audit_date': data.get('audit_date'),
                'forced_labor_risk': data.get('forced_labor_risk'),
                'child_labor_risk': data.get('child_labor_risk'),
                'wage_compliance': data.get('wage_compliance'),
                'union_rights': data.get('union_rights'),
                'audit_score': data.get('audit_score')
            }
            self.insert('fair_labor_audits', insert_data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding labor audit: {e}")
            return False

    def get_labor_audits(self, company_id: int) -> List[Dict]:
        """Get all labor audits"""
        return self.select('fair_labor_audits', company_id=company_id, order_by='audit_date DESC')

    def get_social_dashboard_stats(self, company_id: int) -> Dict:
        """Get aggregated stats for dashboard charts"""
        stats = {
            'satisfaction_score': 0,
            'training_hours_total': 0,
            'ohs_incidents_total': 0,
            'human_rights_incidents': 0,
            'labor_audit_avg_score': 0
        }
        try:
            # Satisfaction (Latest year)
            # Try to adapt to schema differences
            try:
                rows = self.execute_query("SELECT satisfaction_score FROM employee_satisfaction WHERE company_id=? ORDER BY year DESC LIMIT 1", (company_id,))
                if rows and rows[0][0]: stats['satisfaction_score'] = rows[0][0]
            except Exception:
                # Fallback for alternative schema (average_score, survey_year)
                rows = self.execute_query("SELECT average_score FROM employee_satisfaction WHERE company_id=? ORDER BY survey_year DESC LIMIT 1", (company_id,))
                if rows and rows[0][0]: stats['satisfaction_score'] = rows[0][0]
            
            # Training Hours (Sum)
            rows = self.execute_query("SELECT SUM(hours) FROM training_records WHERE company_id=?", (company_id,))
            if rows and rows[0][0]: stats['training_hours_total'] = rows[0][0]
            
            # OHS Incidents
            rows = self.execute_query("SELECT COUNT(*) FROM ohs_incidents WHERE company_id=?", (company_id,))
            if rows: stats['ohs_incidents_total'] = rows[0][0]
            
            # Human Rights Incidents
            rows = self.execute_query("SELECT SUM(incidents_found) FROM human_rights_assessments WHERE company_id=?", (company_id,))
            if rows and rows[0][0]: stats['human_rights_incidents'] = rows[0][0]
            
            # Labor Audit Score
            rows = self.execute_query("SELECT AVG(audit_score) FROM fair_labor_audits WHERE company_id=?", (company_id,))
            if rows and rows[0][0]: stats['labor_audit_avg_score'] = round(rows[0][0], 2)
            
        except Exception as e:
            logging.error(f"Error getting social stats: {e}")
            
        return stats

    def add_consumer_complaint(self, company_id: int, data: Dict) -> bool:
        """Add a new consumer complaint"""
        try:
            insert_data = {
                'complaint_date': data.get('complaint_date'),
                'category': data.get('category'),
                'severity': data.get('severity'),
                'description': data.get('description'),
                'resolution_status': data.get('resolution_status'),
                'satisfaction_score': data.get('satisfaction_score')
            }
            self.insert('consumer_complaints', insert_data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding consumer complaint: {e}")
            return False

    def get_consumer_complaints(self, company_id: int) -> List[Dict]:
        """Get all consumer complaints"""
        return self.select('consumer_complaints', {'company_id': company_id}, order_by='complaint_date DESC')
    
    def add_community_investment_dict(self, company_id: int, data: Dict) -> bool:
        """Add community investment (Dict version)"""
        try:
            insert_data = {
                'project_name': data.get('project_name'),
                'investment_amount': data.get('investment_amount'),
                'beneficiaries_count': data.get('beneficiaries_count'),
                'impact_description': data.get('impact_description'),
                'date': data.get('date')
            }
            self.insert('community_investment', insert_data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error adding community investment: {e}")
            return False

    def get_community_investments(self, company_id: int) -> List[Dict]:
        """Get community investments"""
        return self.select('community_investment', {'company_id': company_id}, order_by='date DESC')

    def get_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.get_dashboard_stats(company_id)

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        stats = {
            'employees': 0,
            'female_ratio': 0,
            'training_hours': 0,
            'incidents': 0,
            'avg_satisfaction': 0,
            'total_investment': 0
        }
        
        try:
            # Çalışan sayısı
            rows = self.execute_query("SELECT SUM(employee_count) FROM hr_employees WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['employees'] = rows[0][0]
                
            # Kadın çalışan oranı (basit hesap)
            rows = self.execute_query("SELECT SUM(employee_count) FROM hr_employees WHERE company_id = ? AND gender = 'Female'", (company_id,))
            female_count = rows[0][0] if rows and rows[0][0] else 0
            if stats['employees'] > 0:
                stats['female_ratio'] = round((female_count / stats['employees']) * 100, 1)
                
            # Eğitim saatleri
            rows = self.execute_query("SELECT SUM(hours * participants) FROM training_records WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['training_hours'] = rows[0][0]
                
            # Kazalar
            rows = self.execute_query("SELECT COUNT(*) FROM ohs_incidents WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['incidents'] = rows[0][0]
                
            # Ortalama Memnuniyet
            rows = self.execute_query("SELECT AVG(satisfaction_score) FROM employee_satisfaction WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['avg_satisfaction'] = round(rows[0][0], 1)
                
            # Topluluk Yatırımı
            rows = self.execute_query("SELECT SUM(investment_amount) FROM community_investment WHERE company_id = ?", (company_id,))
            if rows and rows[0][0]:
                stats['total_investment'] = rows[0][0]

        except Exception as e:
            logging.error(f"Stats Error: {e}")
            
        return stats

    def add_employee_data(self, company_id: int, count: int, gender: str, department: str, age_group: str, year: int):
        data = {
            'employee_count': count,
            'gender': gender,
            'department': department,
            'age_group': age_group,
            'year': year
        }
        self.insert('hr_employees', data, company_id=company_id)

    def add_ohs_incident(self, company_id: int, incident_type: str, date: str, severity: str, description: str, lost_time_days: int):
        data = {
            'incident_type': incident_type,
            'date': date,
            'severity': severity,
            'description': description,
            'lost_time_days': lost_time_days
        }
        self.insert('ohs_incidents', data, company_id=company_id)

    def add_training(self, company_id: int, name: str, hours: float, participants: int, date: str, category: str):
        data = {
            'training_name': name,
            'hours': hours,
            'participants': participants,
            'date': date,
            'category': category
        }
        self.insert('training_records', data, company_id=company_id)

    def add_employee_satisfaction(self, company_id: int, year: int, survey_date: str, score: float, turnover: float, participation: float, comments: str):
        data = {
            'year': year,
            'survey_date': survey_date,
            'satisfaction_score': score,
            'turnover_rate': turnover,
            'participation_rate': participation,
            'comments': comments
        }
        self.insert('employee_satisfaction', data, company_id=company_id)

    def add_community_investment(self, company_id: int, project_name: str, amount: float, beneficiaries: int, description: str, date: str):
        data = {
            'project_name': project_name,
            'investment_amount': amount,
            'beneficiaries_count': beneficiaries,
            'impact_description': description,
            'date': date
        }
        self.insert('community_investment', data, company_id=company_id)

    def get_satisfaction_trends(self, company_id: int) -> Dict:
        """Grafikler için memnuniyet ve devir hızı trendlerini getir"""
        trends = {
            'years': [],
            'satisfaction': [],
            'turnover': []
        }
        
        try:
            # Yıla göre sıralı verileri çek
            rows = self.execute_query("""
                SELECT year, AVG(satisfaction_score), AVG(turnover_rate) 
                FROM employee_satisfaction 
                WHERE company_id = ? 
                GROUP BY year 
                ORDER BY year ASC
            """, (company_id,))
            
            for row in rows:
                if row[0]: # Year not null
                    trends['years'].append(row[0])
                    trends['satisfaction'].append(round(row[1], 2) if row[1] else 0)
                    trends['turnover'].append(round(row[2], 2) if row[2] else 0)
                    
        except Exception as e:
            logging.error(f"Trend Error: {e}")
            
        return trends

    def get_recent_data(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen verileri getir"""
        data = []
        
        try:
            # HR Data
            rows = self.execute_query("SELECT 'employee', department || ' - ' || gender, created_date, employee_count FROM hr_employees WHERE company_id = ? ORDER BY created_date DESC LIMIT ?", (company_id, limit))
            for row in rows:
                data.append({'type': 'employee', 'detail': row[1], 'date': row[2], 'value': row[3]})
                
            # OHS Data
            rows = self.execute_query("SELECT 'ohs', incident_type, date, severity FROM ohs_incidents WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in rows:
                data.append({'type': 'ohs', 'detail': row[1], 'date': row[2], 'value': row[3]})
                
            # Training Data
            rows = self.execute_query("SELECT 'training', training_name, date, hours FROM training_records WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in rows:
                data.append({'type': 'training', 'detail': row[1], 'date': row[2], 'value': f"{row[3]} saat"})

            # Satisfaction Data
            rows = self.execute_query("SELECT 'satisfaction', 'Anket: ' || year, survey_date, satisfaction_score FROM employee_satisfaction WHERE company_id = ? ORDER BY survey_date DESC LIMIT ?", (company_id, limit))
            for row in rows:
                data.append({'type': 'satisfaction', 'detail': row[1], 'date': row[2], 'value': f"Skor: {row[3]}"})

            # Investment Data
            rows = self.execute_query("SELECT 'investment', project_name, date, investment_amount FROM community_investment WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in rows:
                data.append({'type': 'investment', 'detail': row[1], 'date': row[2], 'value': f"{row[3]:,.0f} TL"})
                
            # Sort all by date desc and limit again
            data.sort(key=lambda x: x['date'], reverse=True)
            return data[:limit]
            
        except Exception as e:
            logging.error(f"Error getting recent data: {e}")
            return []

    def export_social_data(self, company_id: int) -> str:
        """Sosyal verileri Excel formatında dışa aktar"""
        try:
            import pandas as pd
            import io
            
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            
            # Using BaseTenantManager's execute_query which enforces tenant isolation
            
            # HR Employees
            rows = self.execute_query("SELECT * FROM hr_employees WHERE company_id = ?", (company_id,))
            df_hr = pd.DataFrame([dict(row) for row in rows])
            df_hr.to_excel(writer, sheet_name='Çalışanlar', index=False)
            
            # OHS Incidents
            rows = self.execute_query("SELECT * FROM ohs_incidents WHERE company_id = ?", (company_id,))
            df_ohs = pd.DataFrame([dict(row) for row in rows])
            df_ohs.to_excel(writer, sheet_name='İSG Olayları', index=False)
            
            # Training Records
            rows = self.execute_query("SELECT * FROM training_records WHERE company_id = ?", (company_id,))
            df_training = pd.DataFrame([dict(row) for row in rows])
            df_training.to_excel(writer, sheet_name='Eğitimler', index=False)
            
            # Employee Satisfaction
            rows = self.execute_query("SELECT * FROM employee_satisfaction WHERE company_id = ?", (company_id,))
            df_sat = pd.DataFrame([dict(row) for row in rows])
            df_sat.to_excel(writer, sheet_name='Memnuniyet', index=False)
            
            # Community Investment
            rows = self.execute_query("SELECT * FROM community_investment WHERE company_id = ?", (company_id,))
            df_inv = pd.DataFrame([dict(row) for row in rows])
            df_inv.to_excel(writer, sheet_name='Topluluk Yatırımı', index=False)
            
            writer.close()
            output.seek(0)
            
            return output
            
        except Exception as e:
            print(f"Export Error: {e}")
            return None

    def get_employee_satisfaction_trends(self, company_id: int) -> Dict:
        """Memnuniyet ve devir hızı trendlerini getir"""
        trends = {
            'years': [],
            'satisfaction': [],
            'turnover': []
        }
        try:
            rows = self.execute_query("SELECT year, AVG(satisfaction_score), AVG(turnover_rate) FROM employee_satisfaction WHERE company_id = ? GROUP BY year ORDER BY year ASC", (company_id,))
            for row in rows:
                trends['years'].append(row[0])
                trends['satisfaction'].append(row[1])
                trends['turnover'].append(row[2])
        except Exception as e:
            print(f"Trend Error: {e}")
        return trends
