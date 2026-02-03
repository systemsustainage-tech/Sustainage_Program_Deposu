# -*- coding: utf-8 -*-
"""
Social Performance Manager
===========================
Central manager for all social performance metrics and data.
"""

import datetime
import sqlite3
from typing import Dict, List, Tuple

try:
    from config.database import DB_PATH
except ImportError:
    from backend.config.database import DB_PATH

class SocialManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path else DB_PATH
        self.init_database()

    def init_database(self):
        """Initialize social performance tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # HR Employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hr_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                employee_count INTEGER,
                gender TEXT,
                department TEXT,
                age_group TEXT,
                year INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # OHS Incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohs_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                incident_type TEXT,
                date DATE,
                severity TEXT,
                description TEXT,
                lost_time_days INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Training Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                training_name TEXT,
                hours REAL,
                participants INTEGER,
                date DATE,
                category TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Employee Satisfaction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_satisfaction (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                year INTEGER,
                survey_date DATE,
                satisfaction_score REAL, -- 0-100 or 1-5
                turnover_rate REAL, -- Percentage
                participation_rate REAL, -- Percentage
                comments TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Community Investment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_investment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                project_name TEXT,
                investment_amount REAL,
                beneficiaries_count INTEGER,
                impact_description TEXT,
                date DATE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Human Rights Assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS human_rights_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                site_name TEXT,
                assessment_date DATE,
                risk_level TEXT, -- Low, Medium, High
                incidents_found INTEGER DEFAULT 0,
                mitigation_plan TEXT,
                status TEXT DEFAULT 'Completed',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fair Labor Audits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fair_labor_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                site_name TEXT,
                audit_date DATE,
                forced_labor_risk TEXT, -- Low, Medium, High
                child_labor_risk TEXT,
                wage_compliance TEXT, -- Compliant, Non-Compliant
                union_rights TEXT, -- Respected, Restricted
                audit_score REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Consumer Complaints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumer_complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL DEFAULT 1,
                complaint_date DATE,
                category TEXT, -- Product Quality, Safety, Privacy, etc.
                severity TEXT, -- Low, Medium, High
                description TEXT,
                resolution_status TEXT, -- Open, In Progress, Resolved
                satisfaction_score REAL, -- 1-5
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_human_rights_assessment(self, company_id: int, data: Dict) -> bool:
        """Add a new human rights assessment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO human_rights_assessments 
                (company_id, site_name, assessment_date, risk_level, incidents_found, mitigation_plan, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, data.get('site_name'), data.get('assessment_date'), 
                  data.get('risk_level'), data.get('incidents_found', 0), 
                  data.get('mitigation_plan'), data.get('status', 'Completed')))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding human rights assessment: {e}")
            return False

    def get_human_rights_assessments(self, company_id: int) -> List[Dict]:
        """Get all human rights assessments"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM human_rights_assessments WHERE company_id = ? ORDER BY assessment_date DESC", (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_labor_audit(self, company_id: int, data: Dict) -> bool:
        """Add a new fair labor audit"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fair_labor_audits 
                (company_id, site_name, audit_date, forced_labor_risk, child_labor_risk, wage_compliance, union_rights, audit_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, data.get('site_name'), data.get('audit_date'), 
                  data.get('forced_labor_risk'), data.get('child_labor_risk'), 
                  data.get('wage_compliance'), data.get('union_rights'), data.get('audit_score')))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding labor audit: {e}")
            return False

    def get_labor_audits(self, company_id: int) -> List[Dict]:
        """Get all labor audits"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fair_labor_audits WHERE company_id = ? ORDER BY audit_date DESC", (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Satisfaction (Latest year)
            # Try to adapt to schema differences
            try:
                cursor.execute("SELECT satisfaction_score FROM employee_satisfaction WHERE company_id=? ORDER BY year DESC LIMIT 1", (company_id,))
                row = cursor.fetchone()
                if row and row[0]: stats['satisfaction_score'] = row[0]
            except sqlite3.OperationalError:
                # Fallback for alternative schema (average_score, survey_year)
                cursor.execute("SELECT average_score FROM employee_satisfaction WHERE company_id=? ORDER BY survey_year DESC LIMIT 1", (company_id,))
                row = cursor.fetchone()
                if row and row[0]: stats['satisfaction_score'] = row[0]
            
            # Training Hours (Sum)
            cursor.execute("SELECT SUM(hours) FROM training_records WHERE company_id=?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]: stats['training_hours_total'] = row[0]
            
            # OHS Incidents
            cursor.execute("SELECT COUNT(*) FROM ohs_incidents WHERE company_id=?", (company_id,))
            row = cursor.fetchone()
            if row: stats['ohs_incidents_total'] = row[0]
            
            # Human Rights Incidents
            cursor.execute("SELECT SUM(incidents_found) FROM human_rights_assessments WHERE company_id=?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]: stats['human_rights_incidents'] = row[0]
            
            # Labor Audit Score
            cursor.execute("SELECT AVG(audit_score) FROM fair_labor_audits WHERE company_id=?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]: stats['labor_audit_avg_score'] = round(row[0], 2)
            
            conn.close()
        except Exception as e:
            print(f"Error getting social stats: {e}")
            
        return stats

    def add_consumer_complaint(self, company_id: int, data: Dict) -> bool:
        """Add a new consumer complaint"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO consumer_complaints 
                (company_id, complaint_date, category, severity, description, resolution_status, satisfaction_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, data.get('complaint_date'), data.get('category'), 
                  data.get('severity'), data.get('description'), 
                  data.get('resolution_status'), data.get('satisfaction_score')))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding consumer complaint: {e}")
            return False

    def get_consumer_complaints(self, company_id: int) -> List[Dict]:
        """Get all consumer complaints"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consumer_complaints WHERE company_id = ? ORDER BY complaint_date DESC", (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_community_investment(self, company_id: int, data: Dict) -> bool:
        """Add community investment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO community_investment 
                (company_id, project_name, investment_amount, beneficiaries_count, impact_description, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, data.get('project_name'), data.get('investment_amount'), 
                  data.get('beneficiaries_count'), data.get('impact_description'), data.get('date')))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding community investment: {e}")
            return False

    def get_community_investments(self, company_id: int) -> List[Dict]:
        """Get community investments"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM community_investment WHERE company_id = ? ORDER BY date DESC", (company_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.get_dashboard_stats(company_id)

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
            cursor.execute("SELECT SUM(employee_count) FROM hr_employees WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]:
                stats['employees'] = row[0]
                
            # Kadın çalışan oranı (basit hesap)
            cursor.execute("SELECT SUM(employee_count) FROM hr_employees WHERE company_id = ? AND gender = 'Female'", (company_id,))
            row = cursor.fetchone()
            female_count = row[0] if row and row[0] else 0
            if stats['employees'] > 0:
                stats['female_ratio'] = round((female_count / stats['employees']) * 100, 1)
                
            # Eğitim saatleri
            cursor.execute("SELECT SUM(hours * participants) FROM training_records WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]:
                stats['training_hours'] = row[0]
                
            # Kazalar
            cursor.execute("SELECT COUNT(*) FROM ohs_incidents WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]:
                stats['incidents'] = row[0]
                
            # Ortalama Memnuniyet
            cursor.execute("SELECT AVG(satisfaction_score) FROM employee_satisfaction WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]:
                stats['avg_satisfaction'] = round(row[0], 1)
                
            # Topluluk Yatırımı
            cursor.execute("SELECT SUM(investment_amount) FROM community_investment WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row and row[0]:
                stats['total_investment'] = row[0]

        except Exception as e:
            print(f"Stats Error: {e}")
        finally:
            conn.close()
            
        return stats

    def add_employee_data(self, company_id: int, count: int, gender: str, department: str, age_group: str, year: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO hr_employees (company_id, employee_count, gender, department, age_group, year)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, count, gender, department, age_group, year))
        conn.commit()
        conn.close()

    def add_ohs_incident(self, company_id: int, incident_type: str, date: str, severity: str, description: str, lost_time_days: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ohs_incidents (company_id, incident_type, date, severity, description, lost_time_days)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, incident_type, date, severity, description, lost_time_days))
        conn.commit()
        conn.close()

    def add_training(self, company_id: int, name: str, hours: float, participants: int, date: str, category: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO training_records (company_id, training_name, hours, participants, date, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, name, hours, participants, date, category))
        conn.commit()
        conn.close()

    def add_employee_satisfaction(self, company_id: int, year: int, survey_date: str, score: float, turnover: float, participation: float, comments: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO employee_satisfaction (company_id, year, survey_date, satisfaction_score, turnover_rate, participation_rate, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, year, survey_date, score, turnover, participation, comments))
        conn.commit()
        conn.close()

    def add_community_investment(self, company_id: int, project_name: str, amount: float, beneficiaries: int, description: str, date: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO community_investment (company_id, project_name, investment_amount, beneficiaries_count, impact_description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, project_name, amount, beneficiaries, description, date))
        conn.commit()
        conn.close()

    def get_satisfaction_trends(self, company_id: int) -> Dict:
        """Grafikler için memnuniyet ve devir hızı trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        trends = {
            'years': [],
            'satisfaction': [],
            'turnover': []
        }
        
        try:
            # Yıla göre sıralı verileri çek
            cursor.execute("""
                SELECT year, AVG(satisfaction_score), AVG(turnover_rate) 
                FROM employee_satisfaction 
                WHERE company_id = ? 
                GROUP BY year 
                ORDER BY year ASC
            """, (company_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                if row[0]: # Year not null
                    trends['years'].append(row[0])
                    trends['satisfaction'].append(round(row[1], 2) if row[1] else 0)
                    trends['turnover'].append(round(row[2], 2) if row[2] else 0)
                    
        except Exception as e:
            print(f"Trend Error: {e}")
        finally:
            conn.close()
            
        return trends
    def get_recent_data(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen verileri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        data = []
        
        try:
            # HR Data
            cursor.execute("SELECT 'employee', department || ' - ' || gender, created_date, employee_count FROM hr_employees WHERE company_id = ? ORDER BY created_date DESC LIMIT ?", (company_id, limit))
            for row in cursor.fetchall():
                data.append({'type': 'employee', 'detail': row[1], 'date': row[2], 'value': row[3]})
                
            # OHS Data
            cursor.execute("SELECT 'ohs', incident_type, date, severity FROM ohs_incidents WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in cursor.fetchall():
                data.append({'type': 'ohs', 'detail': row[1], 'date': row[2], 'value': row[3]})
                
            # Training Data
            cursor.execute("SELECT 'training', training_name, date, hours FROM training_records WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in cursor.fetchall():
                data.append({'type': 'training', 'detail': row[1], 'date': row[2], 'value': f"{row[3]} saat"})

            # Satisfaction Data
            cursor.execute("SELECT 'satisfaction', 'Anket: ' || year, survey_date, satisfaction_score FROM employee_satisfaction WHERE company_id = ? ORDER BY survey_date DESC LIMIT ?", (company_id, limit))
            for row in cursor.fetchall():
                data.append({'type': 'satisfaction', 'detail': row[1], 'date': row[2], 'value': f"Skor: {row[3]}"})

            # Investment Data
            cursor.execute("SELECT 'investment', project_name, date, investment_amount FROM community_investment WHERE company_id = ? ORDER BY date DESC LIMIT ?", (company_id, limit))
            for row in cursor.fetchall():
                data.append({'type': 'investment', 'detail': row[1], 'date': row[2], 'value': f"{row[3]:,.0f} TL"})
                
            # Sort by date
            data.sort(key=lambda x: x['date'], reverse=True)
            return data[:limit]
            
        except Exception as e:
            print(f"Recent Data Error: {e}")
            return []
        finally:
            conn.close()

    def export_social_data(self, company_id: int) -> str:
        """Sosyal verileri Excel formatında dışa aktar"""
        try:
            import pandas as pd
            import io
            
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='openpyxl')
            
            conn = sqlite3.connect(self.db_path)
            
            # HR Employees
            df_hr = pd.read_sql_query("SELECT * FROM hr_employees WHERE company_id = ?", conn, params=(company_id,))
            df_hr.to_excel(writer, sheet_name='Çalışanlar', index=False)
            
            # OHS Incidents
            df_ohs = pd.read_sql_query("SELECT * FROM ohs_incidents WHERE company_id = ?", conn, params=(company_id,))
            df_ohs.to_excel(writer, sheet_name='İSG Olayları', index=False)
            
            # Training Records
            df_training = pd.read_sql_query("SELECT * FROM training_records WHERE company_id = ?", conn, params=(company_id,))
            df_training.to_excel(writer, sheet_name='Eğitimler', index=False)
            
            # Employee Satisfaction
            df_sat = pd.read_sql_query("SELECT * FROM employee_satisfaction WHERE company_id = ?", conn, params=(company_id,))
            df_sat.to_excel(writer, sheet_name='Memnuniyet', index=False)
            
            # Community Investment
            df_inv = pd.read_sql_query("SELECT * FROM community_investment WHERE company_id = ?", conn, params=(company_id,))
            df_inv.to_excel(writer, sheet_name='Topluluk Yatırımı', index=False)
            
            conn.close()
            writer.close()
            output.seek(0)
            
            return output
            
        except Exception as e:
            print(f"Export Error: {e}")
            return None

    def get_employee_satisfaction_trends(self, company_id: int) -> Dict:
        """Memnuniyet ve devir hızı trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        trends = {
            'years': [],
            'satisfaction': [],
            'turnover': []
        }
        try:
            cursor.execute("SELECT year, AVG(satisfaction_score), AVG(turnover_rate) FROM employee_satisfaction WHERE company_id = ? GROUP BY year ORDER BY year ASC", (company_id,))
            for row in cursor.fetchall():
                trends['years'].append(row[0])
                trends['satisfaction'].append(row[1])
                trends['turnover'].append(row[2])
        except Exception as e:
            print(f"Trend Error: {e}")
        finally:
            conn.close()
        return trends
