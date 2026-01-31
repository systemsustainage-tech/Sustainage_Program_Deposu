#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ekonomik Değer Yönetimi Modülü
GRI 201-1 Ekonomik Değer Dağılımı ve finansal metrikler
"""

import logging
import os
import sqlite3
from typing import Dict


from utils.language_manager import LanguageManager
from config.database import DB_PATH


class EconomicValueManager:
    """Ekonomik değer yönetimi ve dağılımı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.lm = LanguageManager()
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Ekonomik değer tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS economic_value_distribution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    revenue REAL NOT NULL,
                    operating_costs REAL,
                    employee_wages REAL,
                    payments_to_capital_providers REAL,
                    payments_to_governments REAL,
                    community_investments REAL,
                    retained_earnings REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_assets REAL,
                    total_liabilities REAL,
                    equity REAL,
                    net_profit REAL,
                    operating_profit REAL,
                    ebitda REAL,
                    return_on_equity REAL,
                    return_on_assets REAL,
                    debt_to_equity_ratio REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tax_contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    corporate_tax REAL,
                    payroll_tax REAL,
                    vat_collected REAL,
                    property_tax REAL,
                    other_taxes REAL,
                    total_tax_paid REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    description TEXT,
                    initial_investment REAL NOT NULL,
                    discount_rate REAL DEFAULT 0.10,
                    start_date TEXT,
                    duration_years INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'Planned', -- Planned, Active, Completed, Cancelled
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_cash_flows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    year INTEGER NOT NULL, -- Relative year (1, 2, 3...)
                    cash_flow REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES investment_projects(id) ON DELETE CASCADE
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS investment_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    npv REAL, -- Net Present Value
                    roi REAL, -- Return on Investment (%)
                    payback_period REAL, -- Years
                    irr REAL, -- Internal Rate of Return (%)
                    evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES investment_projects(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            # print(self.lm.tr('economic_tables_success', "[OK] Ekonomik deger yonetimi modulu tablolari basariyla olusturuldu"))

        except Exception as e:
            logging.error(f"{self.lm.tr('economic_table_error', '[HATA] Ekonomik deger yonetimi modulu tablo olusturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_economic_value_distribution(self, company_id: int, year: int, revenue: float,
                                      operating_costs: float = None, employee_wages: float = None,
                                      payments_to_capital_providers: float = None,
                                      payments_to_governments: float = None,
                                      community_investments: float = None,
                                      retained_earnings: float = None) -> bool:
        """Ekonomik değer dağılımı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO economic_value_distribution 
                (company_id, year, revenue, operating_costs, employee_wages,
                 payments_to_capital_providers, payments_to_governments,
                 community_investments, retained_earnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, revenue, operating_costs, employee_wages,
                  payments_to_capital_providers, payments_to_governments,
                  community_investments, retained_earnings))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('economic_value_add_error', 'Ekonomik değer dağılımı ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_financial_performance(self, company_id: int, year: int, total_assets: float,
                                total_liabilities: float = None, equity: float = None,
                                net_profit: float = None, operating_profit: float = None,
                                ebitda: float = None) -> bool:
        """Finansal performans ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Finansal oranları hesapla
            return_on_equity = None
            return_on_assets = None
            debt_to_equity_ratio = None

            if equity and net_profit:
                return_on_equity = (net_profit / equity) * 100

            if total_assets and net_profit:
                return_on_assets = (net_profit / total_assets) * 100

            if equity and total_liabilities:
                debt_to_equity_ratio = total_liabilities / equity

            cursor.execute("""
                INSERT INTO financial_performance 
                (company_id, year, total_assets, total_liabilities, equity,
                 net_profit, operating_profit, ebitda, return_on_equity,
                 return_on_assets, debt_to_equity_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, total_assets, total_liabilities, equity,
                  net_profit, operating_profit, ebitda, return_on_equity,
                  return_on_assets, debt_to_equity_ratio))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('financial_performance_add_error', 'Finansal performans ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_tax_contributions(self, company_id: int, year: int, corporate_tax: float,
                            payroll_tax: float = None, vat_collected: float = None,
                            property_tax: float = None, other_taxes: float = None) -> bool:
        """Vergi katkıları ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            total_tax_paid = corporate_tax + (payroll_tax or 0) + (vat_collected or 0) + (property_tax or 0) + (other_taxes or 0)

            cursor.execute("""
                INSERT INTO tax_contributions 
                (company_id, year, corporate_tax, payroll_tax, vat_collected,
                 property_tax, other_taxes, total_tax_paid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, corporate_tax, payroll_tax, vat_collected,
                  property_tax, other_taxes, total_tax_paid))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('tax_add_error', 'Vergi katkısı ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir (alias)"""
        return self.get_stats(company_id)

    def get_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {'revenue': 0, 'net_profit': 0, 'tax_paid': 0}

        try:
            # En son yılın geliri
            cursor.execute("""
                SELECT revenue FROM economic_value_distribution 
                WHERE company_id = ? ORDER BY year DESC LIMIT 1
            """, (company_id,))
            row = cursor.fetchone()
            if row:
                stats['revenue'] = row[0]

            # En son yılın net karı
            cursor.execute("""
                SELECT net_profit FROM financial_performance 
                WHERE company_id = ? ORDER BY year DESC LIMIT 1
            """, (company_id,))
            row = cursor.fetchone()
            if row:
                stats['net_profit'] = row[0]

            # En son yılın toplam vergisi
            cursor.execute("""
                SELECT total_tax_paid FROM tax_contributions 
                WHERE company_id = ? ORDER BY year DESC LIMIT 1
            """, (company_id,))
            row = cursor.fetchone()
            if row:
                stats['tax_paid'] = row[0]

        except Exception as e:
            logging.error(f"Ekonomik istatistik getirme hatası: {e}")
        finally:
            conn.close()

        return stats

    def get_recent_data(self, company_id: int) -> list:
        """Son eklenen finansal verileri getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        recent_data = []

        try:
            cursor.execute("""
                SELECT id, year, net_profit as amount, 'risk' as data_type, 'Net Kâr' as description, created_at 
                FROM financial_performance 
                WHERE company_id = ? 
                UNION ALL
                SELECT id, year, revenue as amount, 'revenue' as data_type, 'Gelir' as description, created_at
                FROM economic_value_distribution
                WHERE company_id = ?
                UNION ALL
                SELECT id, year, total_tax_paid as amount, 'tax' as data_type, 'Toplam Vergi' as description, created_at
                FROM tax_contributions
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT 5
            """, (company_id, company_id, company_id))
            
            rows = cursor.fetchall()
            for row in rows:
                recent_data.append({
                    'id': row['id'],
                    'year': row['year'],
                    'amount': row['amount'],
                    'data_type': row['data_type'],
                    'description': row['description'],
                    'created_at': row['created_at']
                })
                
        except Exception as e:
            logging.error(f"Ekonomik geçmiş veri getirme hatası: {e}")
        finally:
            conn.close()

        return recent_data

    def get_economic_summary(self, company_id: int, year: int) -> Dict:
        """Ekonomik özet getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Ekonomik değer dağılımı
            cursor.execute("""
                SELECT revenue, operating_costs, employee_wages, payments_to_capital_providers,
                       payments_to_governments, community_investments, retained_earnings
                FROM economic_value_distribution 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            evd_result = cursor.fetchone()
            if evd_result:
                revenue, operating_costs, employee_wages, payments_capital, payments_gov, community_inv, retained = evd_result

                # Yüzde hesaplamaları
                (employee_wages or 0) + (payments_capital or 0) + (payments_gov or 0) + (community_inv or 0)
                wage_percentage = ((employee_wages or 0) / revenue * 100) if revenue > 0 else 0
                capital_percentage = ((payments_capital or 0) / revenue * 100) if revenue > 0 else 0
                gov_percentage = ((payments_gov or 0) / revenue * 100) if revenue > 0 else 0
                community_percentage = ((community_inv or 0) / revenue * 100) if revenue > 0 else 0
            else:
                revenue = employee_wages = payments_capital = payments_gov = community_inv = retained = 0
                wage_percentage = capital_percentage = gov_percentage = community_percentage = 0

            # Finansal performans
            cursor.execute("""
                SELECT total_assets, total_liabilities, equity, net_profit, operating_profit,
                       ebitda, return_on_equity, return_on_assets, debt_to_equity_ratio
                FROM financial_performance 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            financial_result = cursor.fetchone()
            if financial_result:
                total_assets, total_liabilities, equity, net_profit, operating_profit, ebitda, roe, roa, der = financial_result
            else:
                total_assets = total_liabilities = equity = net_profit = operating_profit = ebitda = roe = roa = der = 0

            # Vergi katkıları
            cursor.execute("""
                SELECT corporate_tax, payroll_tax, vat_collected, property_tax, other_taxes, total_tax_paid
                FROM tax_contributions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            tax_result = cursor.fetchone()
            if tax_result:
                corporate_tax, payroll_tax, vat_collected, property_tax, other_taxes, total_tax_paid = tax_result
            else:
                corporate_tax = payroll_tax = vat_collected = property_tax = other_taxes = total_tax_paid = 0

            return {
                'revenue': revenue,
                'economic_value_distribution': {
                    'employee_wages': employee_wages,
                    'payments_to_capital_providers': payments_capital,
                    'payments_to_governments': payments_gov,
                    'community_investments': community_inv,
                    'retained_earnings': retained
                },
                'distribution_percentages': {
                    'wage_percentage': wage_percentage,
                    'capital_percentage': capital_percentage,
                    'government_percentage': gov_percentage,
                    'community_percentage': community_percentage
                },
                'financial_performance': {
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'equity': equity,
                    'net_profit': net_profit,
                    'operating_profit': operating_profit,
                    'ebitda': ebitda,
                    'return_on_equity': roe,
                    'return_on_assets': roa,
                    'debt_to_equity_ratio': der
                },
                'tax_contributions': {
                    'corporate_tax': corporate_tax,
                    'payroll_tax': payroll_tax,
                    'vat_collected': vat_collected,
                    'property_tax': property_tax,
                    'other_taxes': other_taxes,
                    'total_tax_paid': total_tax_paid
                },
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('economic_summary_error', 'Ekonomik özet getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def calculate_gri_201_metrics(self, company_id: int, year: int) -> Dict:
        """GRI 201-1 metriklerini hesapla"""
        summary = self.get_economic_summary(company_id, year)

        if not summary:
            return {}

        # GRI 201-1 Ekonomik Değer Dağılımı metrikleri
        return {
            'gri_201_1_revenue': summary['revenue'],
            'gri_201_1_employee_wages': summary['economic_value_distribution']['employee_wages'],
            'gri_201_1_payments_to_capital': summary['economic_value_distribution']['payments_to_capital_providers'],
            'gri_201_1_payments_to_government': summary['economic_value_distribution']['payments_to_governments'],
            'gri_201_1_community_investment': summary['economic_value_distribution']['community_investments'],
            'gri_201_1_retained_earnings': summary['economic_value_distribution']['retained_earnings'],
            'gri_201_1_total_distributed': (
                summary['economic_value_distribution']['employee_wages'] +
                summary['economic_value_distribution']['payments_to_capital_providers'] +
                summary['economic_value_distribution']['payments_to_governments'] +
                summary['economic_value_distribution']['community_investments']
            ),
            'distribution_percentages': summary['distribution_percentages'],
            'year': year,
            'company_id': company_id
        }

    def add_investment_project(self, company_id: int, project_name: str, initial_investment: float,
                             start_date: str, description: str = None, discount_rate: float = 0.10,
                             duration_years: int = 5, status: str = 'Planned') -> int:
        """Yatırım projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO investment_projects 
                (company_id, project_name, description, initial_investment, discount_rate, start_date, duration_years, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, description, initial_investment, discount_rate, start_date, duration_years, status))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error adding investment project: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def add_project_cash_flow(self, project_id: int, year: int, cash_flow: float) -> bool:
        """Proje nakit akışı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO investment_cash_flows (project_id, year, cash_flow)
                VALUES (?, ?, ?)
            """, (project_id, year, cash_flow))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding cash flow: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_investment_projects(self, company_id: int) -> list:
        """Yatırım projelerini ve metriklerini getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        projects = []
        try:
            cursor.execute("""
                SELECT p.*, e.npv, e.roi, e.payback_period, e.irr 
                FROM investment_projects p
                LEFT JOIN investment_evaluations e ON p.id = e.project_id
                WHERE p.company_id = ?
                ORDER BY p.created_at DESC
            """, (company_id,))
            rows = cursor.fetchall()
            for row in rows:
                projects.append(dict(row))
        except Exception as e:
            logging.error(f"Error fetching investment projects: {e}")
        finally:
            conn.close()
        return projects

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Önce varsa sil (update mantığı)
            cursor.execute("DELETE FROM investment_cash_flows WHERE project_id = ? AND year = ?", (project_id, year))
            
            cursor.execute("""
                INSERT INTO investment_cash_flows (project_id, year, cash_flow)
                VALUES (?, ?, ?)
            """, (project_id, year, cash_flow))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error adding cash flow: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_investment_projects(self, company_id: int) -> list:
        """Yatırım projelerini listele"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        projects = []
        try:
            cursor.execute("""
                SELECT p.*, e.npv, e.roi, e.payback_period, e.irr
                FROM investment_projects p
                LEFT JOIN investment_evaluations e ON p.id = e.project_id
                WHERE p.company_id = ?
                ORDER BY p.created_at DESC
            """, (company_id,))
            rows = cursor.fetchall()
            for row in rows:
                projects.append(dict(row))
        except Exception as e:
            logging.error(f"Error getting investment projects: {e}")
        finally:
            conn.close()
        return projects

    def calculate_project_metrics(self, project_id: int) -> dict:
        """Proje metriklerini (NPV, ROI, Payback) hesapla ve kaydet"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            # Proje bilgilerini al
            cursor.execute("SELECT * FROM investment_projects WHERE id = ?", (project_id,))
            project = cursor.fetchone()
            if not project:
                return {}

            initial_investment = project['initial_investment']
            discount_rate = project['discount_rate']

            # Nakit akışlarını al
            cursor.execute("SELECT year, cash_flow FROM investment_cash_flows WHERE project_id = ? ORDER BY year ASC", (project_id,))
            flows = cursor.fetchall()

            npv = -initial_investment
            total_return = 0
            payback_period = None
            cumulative_cash = -initial_investment
            
            # Yıl 0 (Initial)
            # Yıl 1, 2, 3...
            
            for flow in flows:
                t = flow['year']
                cf = flow['cash_flow']
                
                # NPV Calculation
                npv += cf / ((1 + discount_rate) ** t)
                
                # ROI & Payback (Basit)
                total_return += cf
                
                prev_cumulative = cumulative_cash
                cumulative_cash += cf
                
                # Payback Period Calculation (Linear interpolation)
                if payback_period is None and cumulative_cash >= 0:
                    # If became positive this year
                    # Fraction of year needed = |prev_cumulative| / cf
                    fraction = abs(prev_cumulative) / cf if cf != 0 else 0
                    payback_period = (t - 1) + fraction

            # ROI Calculation: (Net Profit / Cost) * 100
            # Net Profit = Total Cash Inflows - Initial Investment
            net_profit = total_return - initial_investment
            roi = (net_profit / initial_investment * 100) if initial_investment > 0 else 0
            
            irr = 0 # Not implemented yet

            # Save to DB
            cursor.execute("DELETE FROM investment_evaluations WHERE project_id = ?", (project_id,))
            cursor.execute("""
                INSERT INTO investment_evaluations (project_id, npv, roi, payback_period, irr)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, npv, roi, payback_period, irr))
            conn.commit()

            return {
                'npv': npv,
                'roi': roi,
                'payback_period': payback_period,
                'irr': irr
            }

        except Exception as e:
            logging.error(f"Error calculating metrics: {e}")
            conn.rollback()
            return {}
        finally:
            conn.close()
