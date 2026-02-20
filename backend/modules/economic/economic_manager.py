#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
from typing import Dict, List, Optional, Any
from backend.core.base_manager import BaseTenantManager

try:
    from config.database import DB_PATH
except ImportError:
    from backend.config.database import DB_PATH

class EconomicManager(BaseTenantManager):
    """
    Ekonomik Performans ve Yatırım Yönetimi Modülü
    - Yatırım projeleri takibi (ROI, NPV, Geri Dönüş Süresi)
    - GRI 201 uyumlu ekonomik değer dağılımı (opsiyonel entegrasyon)
    """
    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        try:
            # Investment Projects
            self.execute_update("""
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
            
            # Cash Flows - Added company_id for strict multi-tenancy
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS investment_cash_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL DEFAULT 0,
                    project_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    cash_flow REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES investment_projects(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(project_id, year)
                )
            """)
            
            # Check for missing columns in investment_projects
            rows = self.execute_query("PRAGMA table_info(investment_projects)")
            columns = [row['name'] for row in rows]
            
            if 'roi' not in columns:
                self.execute_update("ALTER TABLE investment_projects ADD COLUMN roi REAL")
            if 'npv' not in columns:
                self.execute_update("ALTER TABLE investment_projects ADD COLUMN npv REAL")
            if 'payback_period' not in columns:
                self.execute_update("ALTER TABLE investment_projects ADD COLUMN payback_period REAL")

            # Check for missing company_id in investment_cash_flows
            rows_cf = self.execute_query("PRAGMA table_info(investment_cash_flows)")
            columns_cf = [row['name'] for row in rows_cf]
            
            if 'company_id' not in columns_cf:
                # If adding column to populated table, we need a default.
                # However, we can't easily backfill correct company_id without complex SQL.
                # For now, default to 0 and assume migration script handles it or data is fresh.
                self.execute_update("ALTER TABLE investment_cash_flows ADD COLUMN company_id INTEGER NOT NULL DEFAULT 0")

        except Exception as e:
            logging.error(f"EconomicManager init tables error: {e}")

    def get_stats(self, company_id: int) -> Dict[str, Any]:
        """Dashboard istatistikleri"""
        stats = {
            "total_investment": 0,
            "active_projects": 0,
            "avg_roi": 0,
            "total_npv": 0
        }
        try:
            rows = self.execute_query("""
                SELECT 
                    COUNT(*) as count,
                    SUM(initial_investment) as total_inv,
                    AVG(roi) as avg_roi,
                    SUM(npv) as total_npv
                FROM investment_projects 
                WHERE company_id = ? AND status = 'Active'
            """, (company_id,), company_id=company_id)
            
            if rows:
                row = rows[0]
                stats["active_projects"] = row["count"]
                stats["total_investment"] = row["total_inv"] or 0
                stats["avg_roi"] = round(row["avg_roi"] or 0, 2)
                stats["total_npv"] = round(row["total_npv"] or 0, 2)
        except Exception as e:
            logging.error(f"Error getting economic stats: {e}")
        return stats

    def get_recent_data(self, company_id: int) -> List[Dict]:
        """Son eklenen projeler"""
        return self.get_investment_projects(company_id)

    def get_investment_projects(self, company_id: int) -> List[Dict]:
        projects = []
        try:
            rows = self.execute_query("""
                SELECT * FROM investment_projects 
                WHERE company_id = ? 
                ORDER BY created_at DESC
            """, (company_id,), company_id=company_id)
            projects = [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Error fetching projects: {e}")
        return projects

    def add_investment_project(self, company_id: int, project_name: str, initial_investment: float, 
                             start_date: str, description: str, discount_rate: float = 0.10, 
                             duration_years: int = 5) -> int:
        try:
            row_id = self.execute_update("""
                INSERT INTO investment_projects 
                (company_id, project_name, initial_investment, start_date, description, discount_rate, duration_years, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (company_id, project_name, initial_investment, start_date, description, discount_rate, duration_years), company_id=company_id)
            return row_id
        except Exception as e:
            logging.error(f"Error adding project: {e}")
            return 0

    def add_project_cash_flow(self, company_id: int, project_id: int, year: int, cash_flow: float) -> bool:
        """
        Adds cash flow and recalculates metrics.
        Requires company_id to verify project ownership before modification.
        """
        try:
            # First verify ownership
            rows = self.execute_query("SELECT id FROM investment_projects WHERE id = ? AND company_id = ?", 
                                    (project_id, company_id), company_id=company_id)
            if not rows:
                logging.error(f"Project {project_id} not found for company {company_id}")
                return False

            # Yıl zaten varsa güncelle, yoksa ekle
            self.execute_update("INSERT OR REPLACE INTO investment_cash_flows (company_id, project_id, year, cash_flow) VALUES (?, ?, ?, ?)", 
                              (company_id, project_id, year, cash_flow), company_id=company_id)
            
            self.calculate_project_metrics(company_id, project_id)
            return True
        except Exception as e:
            logging.error(f"Error adding cash flow: {e}")
            return False

    def calculate_project_metrics(self, company_id: int, project_id: int) -> bool:
        """ROI, NPV ve Geri Dönüş Süresi Hesaplama"""
        try:
            # Verify ownership and get project
            rows = self.execute_query("SELECT * FROM investment_projects WHERE id = ? AND company_id = ?", 
                                    (project_id, company_id), company_id=company_id)
            if not rows: return False
            project = rows[0]

            initial_inv = project['initial_investment']
            discount_rate = project['discount_rate'] or 0.10
            
            # Get flows
            rows = self.execute_query("SELECT * FROM investment_cash_flows WHERE project_id = ? AND company_id = ? ORDER BY year ASC", 
                                    (project_id, company_id), company_id=company_id)
            flows = rows
            
            if not flows:
                return True # No flows yet

            # Nakit akışlarını listeye al
            cash_flows = [f['cash_flow'] for f in flows]
            
            # 1. NPV Calculation
            npv = -initial_inv
            for i, cf in enumerate(cash_flows):
                npv += cf / ((1 + discount_rate) ** (i + 1))
            
            # 2. ROI Calculation
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
                    fraction = abs(prev_cumulative) / cf if cf != 0 else 0
                    payback = i + fraction
                    break
            
            self.execute_update("UPDATE investment_projects SET npv = ?, roi = ?, payback_period = ? WHERE id = ?", 
                              (npv, roi, payback, project_id), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Error calculating metrics: {e}")
            return False
