#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İnsan Kaynakları Metrikleri Modülü
İstihdam, çeşitlilik, ücret eşitliği ve çalışan verileri
GRI 401, 402, 404, 405, 406
"""

import logging
import os
from typing import Dict, List


from backend.core.base_manager import BaseTenantManager

class HRMetrics(BaseTenantManager):
    """İnsan Kaynakları metrikleri ve analizleri"""

    def __init__(self, db_path: str = None) -> None:
        super().__init__()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """İK tabloları"""
        try:
            # Çalışan demografik verileri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS hr_demographics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    gender TEXT,
                    age_group TEXT,
                    employment_type TEXT,
                    position_level TEXT,
                    department TEXT,
                    count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """, params=(), company_id=None, skip_filter=True)

            # İşe alım ve ayrılma
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS hr_turnover (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    period_month INTEGER,
                    new_hires INTEGER DEFAULT 0,
                    terminations INTEGER DEFAULT 0,
                    voluntary_exits INTEGER DEFAULT 0,
                    involuntary_exits INTEGER DEFAULT 0,
                    gender TEXT,
                    age_group TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """, params=(), company_id=None, skip_filter=True)

            # Ücret verileri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS hr_compensation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    position_level TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    avg_salary REAL,
                    min_salary REAL,
                    max_salary REAL,
                    employee_count INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """, params=(), company_id=None, skip_filter=True)

            # Çeşitlilik ve eşitlik
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS hr_diversity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    value REAL,
                    unit TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """, params=(), company_id=None, skip_filter=True)

            logging.info("[OK] IK tablolari hazir")

        except Exception as e:
            logging.error(f"[HATA] IK tablo: {e}")

    def add_demographics(self, company_id: int, year: int, gender: str,
                        age_group: str, employment_type: str, count: int, **kwargs) -> int:
        """Demografik veri ekle"""
        try:
            self.execute_update("""
                INSERT INTO hr_demographics 
                (company_id, period_year, gender, age_group, employment_type, 
                 position_level, department, count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, gender, age_group, employment_type,
                  kwargs.get('position_level'), kwargs.get('department'), count),
                  company_id=company_id)
            
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            return rows[0]['id'] if rows else 0
        except Exception as e:
            logging.error(f"Add demographics error: {e}")
            return 0

    def add_turnover(self, company_id: int, year: int, month: int = None,
                    new_hires: int = 0, terminations: int = 0, **kwargs) -> int:
        """İşe alım/ayrılma verisi ekle"""
        try:
            self.execute_update("""
                INSERT INTO hr_turnover 
                (company_id, period_year, period_month, new_hires, terminations,
                 voluntary_exits, involuntary_exits, gender, age_group)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, new_hires, terminations,
                  kwargs.get('voluntary_exits', 0), kwargs.get('involuntary_exits', 0),
                  kwargs.get('gender'), kwargs.get('age_group')),
                  company_id=company_id)
            
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            return rows[0]['id'] if rows else 0
        except Exception as e:
            logging.error(f"Add turnover error: {e}")
            return 0

    def add_compensation(self, company_id: int, year: int, position_level: str,
                        gender: str, avg_salary: float, employee_count: int, **kwargs) -> int:
        """Ücret verisi ekle"""
        try:
            self.execute_update("""
                INSERT INTO hr_compensation 
                (company_id, period_year, position_level, gender, avg_salary,
                 min_salary, max_salary, employee_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, position_level, gender, avg_salary,
                  kwargs.get('min_salary'), kwargs.get('max_salary'), employee_count),
                  company_id=company_id)
            
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            return rows[0]['id'] if rows else 0
        except Exception as e:
            logging.error(f"Add compensation error: {e}")
            return 0

    def get_workforce_summary(self, company_id: int, year: int) -> Dict:
        """İş gücü özeti"""
        try:
            # Toplam çalışan
            rows_total = self.execute_query("""
                SELECT SUM(count) as total FROM hr_demographics
                WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
            total = rows_total[0]['total'] if rows_total and rows_total[0]['total'] else 0

            # Cinsiyet dağılımı
            rows_gender = self.execute_query("""
                SELECT gender, SUM(count) as count FROM hr_demographics
                WHERE company_id=? AND period_year=?
                GROUP BY gender
            """, (company_id, year), company_id=company_id)
            gender_dist = {row['gender']: row['count'] for row in rows_gender}

            # İstihdam tipi
            rows_emp = self.execute_query("""
                SELECT employment_type, SUM(count) as count FROM hr_demographics
                WHERE company_id=? AND period_year=?
                GROUP BY employment_type
            """, (company_id, year), company_id=company_id)
            employment_dist = {row['employment_type']: row['count'] for row in rows_emp}

            return {
                'total_employees': int(total),
                'gender_distribution': gender_dist,
                'employment_distribution': employment_dist,
                'year': year
            }
        except Exception as e:
            logging.error(f"Get workforce summary error: {e}")
            return {'total_employees': 0}

    def get_turnover_rate(self, company_id: int, year: int) -> Dict:
        """İşgücü devir hızı"""
        try:
            # Toplam işe alım ve ayrılma
            rows = self.execute_query("""
                SELECT 
                    SUM(new_hires) as hires,
                    SUM(terminations) as exits,
                    SUM(voluntary_exits) as voluntary,
                    SUM(involuntary_exits) as involuntary
                FROM hr_turnover
                WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
            
            row = rows[0] if rows else {}

            # Ortalama çalışan sayısı
            workforce = self.get_workforce_summary(company_id, year)
            avg_employees = workforce.get('total_employees', 0)

            hires = row.get('hires') or 0
            exits = row.get('exits') or 0
            voluntary = row.get('voluntary') or 0
            involuntary = row.get('involuntary') or 0

            turnover_rate = (exits / avg_employees * 100) if avg_employees > 0 else 0
            hire_rate = (hires / avg_employees * 100) if avg_employees > 0 else 0

            return {
                'new_hires': int(hires),
                'terminations': int(exits),
                'voluntary_exits': int(voluntary),
                'involuntary_exits': int(involuntary),
                'turnover_rate': round(turnover_rate, 2),
                'hire_rate': round(hire_rate, 2),
                'year': year
            }
        except Exception as e:
            logging.error(f"Get turnover rate error: {e}")
            return {}

    def get_gender_pay_gap(self, company_id: int, year: int, position_level: str = None) -> Dict:
        """Cinsiyet ücret farkı"""
        try:
            if position_level:
                rows = self.execute_query("""
                    SELECT gender, AVG(avg_salary) as avg, SUM(employee_count) as count
                    FROM hr_compensation
                    WHERE company_id=? AND period_year=? AND position_level=?
                    GROUP BY gender
                """, (company_id, year, position_level), company_id=company_id)
            else:
                rows = self.execute_query("""
                    SELECT gender, AVG(avg_salary) as avg, SUM(employee_count) as count
                    FROM hr_compensation
                    WHERE company_id=? AND period_year=?
                    GROUP BY gender
                """, (company_id, year), company_id=company_id)

            salaries = {row['gender']: {'avg': row['avg'], 'count': row['count']} for row in rows}

            male_salary = salaries.get('Erkek', {}).get('avg', 0)
            female_salary = salaries.get('Kadın', {}).get('avg', 0)

            gap = 0
            if male_salary > 0:
                gap = ((male_salary - female_salary) / male_salary * 100)

            return {
                'male_avg_salary': round(male_salary, 2),
                'female_avg_salary': round(female_salary, 2),
                'pay_gap_percent': round(gap, 2),
                'position_level': position_level or 'Tümü',
                'year': year
            }
        except Exception as e:
            logging.error(f"Get gender pay gap error: {e}")
            return {}

    def get_diversity_metrics(self, company_id: int, year: int) -> Dict:
        """Çeşitlilik metrikleri"""
        try:
            workforce = self.get_workforce_summary(company_id, year)
            total = workforce.get('total_employees', 0)

            if total == 0:
                return {'error': 'Veri yok'}

            gender_dist = workforce.get('gender_distribution', {})

            female_count = gender_dist.get('Kadın', 0)
            female_percent = (female_count / total * 100) if total > 0 else 0

            # Yönetim kademesinde kadın oranı
            rows_female_mgr = self.execute_query("""
                SELECT SUM(count) as count FROM hr_demographics
                WHERE company_id=? AND period_year=? 
                AND gender='Kadın' AND position_level='Yönetici'
            """, (company_id, year), company_id=company_id)
            female_managers = rows_female_mgr[0]['count'] if rows_female_mgr and rows_female_mgr[0]['count'] else 0

            rows_total_mgr = self.execute_query("""
                SELECT SUM(count) as count FROM hr_demographics
                WHERE company_id=? AND period_year=? AND position_level='Yönetici'
            """, (company_id, year), company_id=company_id)
            total_managers = rows_total_mgr[0]['count'] if rows_total_mgr and rows_total_mgr[0]['count'] else 0

            female_manager_percent = (female_managers / total_managers * 100) if total_managers > 0 else 0

            return {
                'total_employees': total,
                'female_employees': int(female_count),
                'female_percent': round(female_percent, 2),
                'female_managers': int(female_managers),
                'total_managers': int(total_managers),
                'female_manager_percent': round(female_manager_percent, 2),
                'year': year
            }
        except Exception as e:
            logging.error(f"Get diversity metrics error: {e}")
            return {}

    def calculate_summary(self, company_id: int, year: int) -> Dict:
        """İK özet verilerini hesapla"""
        try:
            rows_total = self.execute_query("SELECT SUM(count) as total FROM hr_demographics WHERE company_id=? AND period_year=?",
                          (company_id, year), company_id=company_id)
            total_employees = rows_total[0]['total'] if rows_total and rows_total[0]['total'] else 0

            rows_hires = self.execute_query("SELECT SUM(new_hires) as hires FROM hr_turnover WHERE company_id=? AND period_year=?",
                          (company_id, year), company_id=company_id)
            new_hires = rows_hires[0]['hires'] if rows_hires and rows_hires[0]['hires'] else 0

            rows_term = self.execute_query("SELECT SUM(terminations) as term FROM hr_turnover WHERE company_id=? AND period_year=?",
                          (company_id, year), company_id=company_id)
            terminations = rows_term[0]['term'] if rows_term and rows_term[0]['term'] else 0

            turnover_rate = (terminations / total_employees * 100) if total_employees > 0 else 0

            return {
                'total_employees': total_employees,
                'new_hires': new_hires,
                'terminations': terminations,
                'turnover_rate': turnover_rate,
                'gender_ratio': 'N/A',
                'avg_age': 35
            }
        except Exception as e:
            logging.error(f"Calculate summary error: {e}")
            return {}

    def get_demographics(self, company_id: int, year: int) -> List[Dict]:
        """Demografik verileri getir"""
        try:
            return self.execute_query("""
                SELECT age_group, gender, employment_type, department, count
                FROM hr_demographics WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
        except Exception as e:
            logging.error(f"Get demographics error: {e}")
            return []

    def get_turnover(self, company_id: int, year: int) -> List[Dict]:
        """İşe alım/ayrılma verilerini getir"""
        try:
            rows = self.execute_query("""
                SELECT period_month, new_hires, terminations, voluntary_exits, involuntary_exits
                FROM hr_turnover WHERE company_id=? AND period_year=? ORDER BY period_month
            """, (company_id, year), company_id=company_id)
            
            return [{'month': r['period_month'] or 0, 'new_hires': r['new_hires'], 'terminations': r['terminations'],
                    'voluntary_exits': r['voluntary_exits'] or 0, 'involuntary_exits': r['involuntary_exits'] or 0}
                   for r in rows]
        except Exception as e:
            logging.error(f"Get turnover error: {e}")
            return []

    def get_compensation(self, company_id: int, year: int) -> List[Dict]:
        """Ücret verilerini getir"""
        try:
            return self.execute_query("""
                SELECT position_level, gender, avg_salary, min_salary, max_salary, employee_count
                FROM hr_compensation WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
        except Exception as e:
            logging.error(f"Get compensation error: {e}")
            return []

    def get_diversity_details(self, company_id: int, year: int) -> List[Dict]:
        """Çeşitlilik metriklerini detay kayıtlar olarak getir"""
        try:
            return self.execute_query("""
                SELECT category, subcategory, value, unit, description
                FROM hr_diversity WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
        except Exception as e:
            logging.error(f"Get diversity details error: {e}")
            return []

    def calculate_gender_pay_ratio(self, company_id: int, year: int) -> str:
        """Cinsiyet bazlı ücret oranı (GRI 405-2)"""
        try:
            rows = self.execute_query("""
                SELECT gender, AVG(avg_salary) as avg FROM hr_compensation
                WHERE company_id=? AND period_year=? GROUP BY gender
            """, (company_id, year), company_id=company_id)
            
            salaries = {row['gender']: row['avg'] for row in rows}
            female = salaries.get('Kadın', 0)
            male = salaries.get('Erkek', 1)
            ratio = female / male if male > 0 else 0
            return f"1:{ratio:.2f}"
        except Exception as e:
            logging.error(f"Calculate gender pay ratio error: {e}")
            return "1:0.00"

    def generate_hr_report(self, company_id: int, year: int) -> str:
        """İK raporu oluştur"""
        summary = self.calculate_summary(company_id, year)
        return f"""{self.lm.tr('hr_metrics_report_title', 'İNSAN KAYNAKLARI METRİKLERİ RAPORU')} - {year}

{self.lm.tr('overview', 'GENEL BAKIŞ')}
- {self.lm.tr('total_employees', 'Toplam Çalışan')}: {summary.get('total_employees', 0)}
- {self.lm.tr('new_hires', 'Yeni İşe Alımlar')}: {summary.get('new_hires', 0)}
- {self.lm.tr('turnover_rate', 'Devir Hızı')}: %{summary.get('turnover_rate', 0):.2f}
- {self.lm.tr('gender_ratio', 'Cinsiyet Oranı')}: {summary.get('gender_ratio', 'N/A')}
- {self.lm.tr('avg_age', 'Ortalama Yaş')}: {summary.get('avg_age', 'N/A')}
"""


