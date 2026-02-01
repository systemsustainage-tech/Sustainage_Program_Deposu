import sqlite3
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class EconomicManager:
    """
    Ekonomik Performans ve Yatırım Yönetimi Modülü
    - Yatırım projeleri takibi (ROI, NPV, Geri Dönüş Süresi)
    - GRI 201 uyumlu ekonomik değer dağılımı (opsiyonel entegrasyon)
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Investment Projects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    initial_investment REAL NOT NULL,
                    start_date DATE,
                    description TEXT,
                    discount_rate REAL DEFAULT 0.10,
                    duration_years INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'Active',
                    roi REAL,
                    npv REAL,
                    payback_period REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Cash Flows
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_cash_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    cash_flow REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES investment_projects(id),
                    UNIQUE(project_id, year)
                )
            """)
            
            # Check for missing columns in investment_projects
            cursor.execute("PRAGMA table_info(investment_projects)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'roi' not in columns:
                cursor.execute("ALTER TABLE investment_projects ADD COLUMN roi REAL")
            if 'npv' not in columns:
                cursor.execute("ALTER TABLE investment_projects ADD COLUMN npv REAL")
            if 'payback_period' not in columns:
                cursor.execute("ALTER TABLE investment_projects ADD COLUMN payback_period REAL")

            conn.commit()
        except Exception as e:
            logging.error(f"EconomicManager init tables error: {e}")
        finally:
            conn.close()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_stats(self, company_id: int) -> Dict[str, Any]:
        """Dashboard istatistikleri"""
        conn = self.get_connection()
        stats = {
            "total_investment": 0,
            "active_projects": 0,
            "avg_roi": 0,
            "total_npv": 0
        }
        try:
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as count,
                    SUM(initial_investment) as total_inv,
                    AVG(roi) as avg_roi,
                    SUM(npv) as total_npv
                FROM investment_projects 
                WHERE company_id = ? AND status = 'Active'
            """, (company_id,))
            row = cursor.fetchone()
            if row:
                stats["active_projects"] = row["count"]
                stats["total_investment"] = row["total_inv"] or 0
                stats["avg_roi"] = round(row["avg_roi"] or 0, 2)
                stats["total_npv"] = round(row["total_npv"] or 0, 2)
        except Exception as e:
            logging.error(f"Error getting economic stats: {e}")
        finally:
            conn.close()
        return stats

    def get_recent_data(self, company_id: int) -> List[Dict]:
        """Son eklenen projeler"""
        return self.get_investment_projects(company_id)

    def get_investment_projects(self, company_id: int) -> List[Dict]:
        conn = self.get_connection()
        projects = []
        try:
            cursor = conn.execute("""
                SELECT * FROM investment_projects 
                WHERE company_id = ? 
                ORDER BY created_at DESC
            """, (company_id,))
            projects = [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error fetching projects: {e}")
        finally:
            conn.close()
        return projects

    def add_investment_project(self, company_id, project_name, initial_investment, start_date, description, discount_rate=0.10, duration_years=5):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                INSERT INTO investment_projects 
                (company_id, project_name, initial_investment, start_date, description, discount_rate, duration_years, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (company_id, project_name, initial_investment, start_date, description, discount_rate, duration_years))
            project_id = cursor.lastrowid
            conn.commit()
            return project_id
        except Exception as e:
            logging.error(f"Error adding project: {e}")
            return False
        finally:
            conn.close()

    def add_project_cash_flow(self, project_id, year, cash_flow):
        conn = sqlite3.connect(self.db_path)
        try:
            # Yıl zaten varsa güncelle, yoksa ekle
            cursor = conn.execute("INSERT OR REPLACE INTO investment_cash_flows (project_id, year, cash_flow) VALUES (?, ?, ?)", (project_id, year, cash_flow))
            conn.commit()
            self.calculate_project_metrics(project_id)
            return True
        except Exception as e:
            logging.error(f"Error adding cash flow: {e}")
            return False
        finally:
            conn.close()

    def calculate_project_metrics(self, project_id):
        """ROI, NPV ve Geri Dönüş Süresi Hesaplama"""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM investment_projects WHERE id = ?", (project_id,))
            project = cursor.fetchone()
            if not project: return False

            initial_inv = project['initial_investment']
            discount_rate = project['discount_rate'] or 0.10
            
            cursor = conn.execute("SELECT * FROM investment_cash_flows WHERE project_id = ? ORDER BY year ASC", (project_id,))
            flows = cursor.fetchall()
            
            if not flows:
                return True # No flows yet

            # Nakit akışlarını listeye al
            cash_flows = [f['cash_flow'] for f in flows]
            
            # 1. NPV Calculation
            npv = -initial_inv
            for i, cf in enumerate(cash_flows):
                # i+1 çünkü yıl 1'den başlıyor varsayıyoruz (iskonto için)
                npv += cf / ((1 + discount_rate) ** (i + 1))
            
            # 2. ROI Calculation (Basit ROI = (Net Kar / Yatırım) * 100)
            total_return = sum(cash_flows)
            net_profit = total_return - initial_inv
            roi = (net_profit / initial_inv * 100) if initial_inv > 0 else 0
            
            # 3. Payback Period
            payback = None
            cumulative = -initial_inv
            
            for i, cf in enumerate(cash_flows):
                prev_cumulative = cumulative
                cumulative += cf
                if cumulative >= 0:
                    # Geri dönüş bu yılda sağlandı
                    # Yıl indeksi i (0-based), yani (i) tam yıl bitti, (i+1). yılın içinde geri dönüş oldu.
                    # Formül: Tamamlanan Yıl Sayısı + (Kalan Maliyet / O Yılın Nakit Akışı)
                    # prev_cumulative negatifti (kalan maliyet = abs(prev_cumulative))
                    fraction = abs(prev_cumulative) / cf if cf != 0 else 0
                    payback = i + fraction
                    break
            
            conn.execute("UPDATE investment_projects SET npv = ?, roi = ?, payback_period = ? WHERE id = ?", (npv, roi, payback, project_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error calculating metrics: {e}")
            return False
        finally:
            conn.close()
