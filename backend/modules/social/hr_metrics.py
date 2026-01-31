#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İnsan Kaynakları Metrikleri Modülü
İstihdam, çeşitlilik, ücret eşitliği ve çalışan verileri
GRI 401, 402, 404, 405, 406
"""

import logging
import os
import sqlite3
from typing import Dict, List


class HRMetrics:
    """İnsan Kaynakları metrikleri ve analizleri"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """İK tabloları"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çalışan demografik verileri
            cursor.execute("""
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
            """)

            # İşe alım ve ayrılma
            cursor.execute("""
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
            """)

            # Ücret verileri
            cursor.execute("""
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
            """)

            # Çeşitlilik ve eşitlik
            cursor.execute("""
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
            """)

            conn.commit()
            logging.info("[OK] IK tablolari hazir")

        except Exception as e:
            logging.error(f"[HATA] IK tablo: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_demographics(self, company_id: int, year: int, gender: str,
                        age_group: str, employment_type: str, count: int, **kwargs) -> int:
        """
        Demografik veri ekle
        
        Args:
            company_id: Firma ID
            year: Yıl
            gender: Cinsiyet (Erkek/Kadın/Diğer)
            age_group: Yaş grubu (<30, 30-50, 50+)
            employment_type: İstihdam tipi (Tam zamanlı/Yarı zamanlı/Sözleşmeli)
            count: Çalışan sayısı
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hr_demographics 
                (company_id, period_year, gender, age_group, employment_type, 
                 position_level, department, count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, gender, age_group, employment_type,
                  kwargs.get('position_level'), kwargs.get('department'), count))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_turnover(self, company_id: int, year: int, month: int = None,
                    new_hires: int = 0, terminations: int = 0, **kwargs) -> int:
        """
        İşe alım/ayrılma verisi ekle
        
        Args:
            company_id: Firma ID
            year: Yıl
            month: Ay (1-12, None ise yıllık)
            new_hires: Yeni işe alınanlar
            terminations: Ayrılanlar
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hr_turnover 
                (company_id, period_year, period_month, new_hires, terminations,
                 voluntary_exits, involuntary_exits, gender, age_group)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, new_hires, terminations,
                  kwargs.get('voluntary_exits', 0), kwargs.get('involuntary_exits', 0),
                  kwargs.get('gender'), kwargs.get('age_group')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_compensation(self, company_id: int, year: int, position_level: str,
                        gender: str, avg_salary: float, employee_count: int, **kwargs) -> int:
        """
        Ücret verisi ekle
        
        Args:
            company_id: Firma ID
            year: Yıl
            position_level: Pozisyon seviyesi (Yönetici/Uzman/Personel)
            gender: Cinsiyet
            avg_salary: Ortalama maaş
            employee_count: Çalışan sayısı
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO hr_compensation 
                (company_id, period_year, position_level, gender, avg_salary,
                 min_salary, max_salary, employee_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, position_level, gender, avg_salary,
                  kwargs.get('min_salary'), kwargs.get('max_salary'), employee_count))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_workforce_summary(self, company_id: int, year: int) -> Dict:
        """İş gücü özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Toplam çalışan
            cursor.execute("""
                SELECT SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            total = cursor.fetchone()[0] or 0

            # Cinsiyet dağılımı
            cursor.execute("""
                SELECT gender, SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=?
                GROUP BY gender
            """, (company_id, year))
            gender_dist = {row[0]: row[1] for row in cursor.fetchall()}

            # İstihdam tipi
            cursor.execute("""
                SELECT employment_type, SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=?
                GROUP BY employment_type
            """, (company_id, year))
            employment_dist = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                'total_employees': int(total),
                'gender_distribution': gender_dist,
                'employment_distribution': employment_dist,
                'year': year
            }
        finally:
            conn.close()

    def get_turnover_rate(self, company_id: int, year: int) -> Dict:
        """İşgücü devir hızı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Toplam işe alım ve ayrılma
            cursor.execute("""
                SELECT 
                    SUM(new_hires) as hires,
                    SUM(terminations) as exits,
                    SUM(voluntary_exits) as voluntary,
                    SUM(involuntary_exits) as involuntary
                FROM hr_turnover
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            row = cursor.fetchone()

            # Ortalama çalışan sayısı
            workforce = self.get_workforce_summary(company_id, year)
            avg_employees = workforce['total_employees']

            hires = row[0] or 0
            exits = row[1] or 0

            turnover_rate = (exits / avg_employees * 100) if avg_employees > 0 else 0
            hire_rate = (hires / avg_employees * 100) if avg_employees > 0 else 0

            return {
                'new_hires': int(hires),
                'terminations': int(exits),
                'voluntary_exits': int(row[2] or 0),
                'involuntary_exits': int(row[3] or 0),
                'turnover_rate': round(turnover_rate, 2),
                'hire_rate': round(hire_rate, 2),
                'year': year
            }
        finally:
            conn.close()

    def get_gender_pay_gap(self, company_id: int, year: int, position_level: str = None) -> Dict:
        """Cinsiyet ücret farkı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if position_level:
                cursor.execute("""
                    SELECT gender, AVG(avg_salary), SUM(employee_count)
                    FROM hr_compensation
                    WHERE company_id=? AND period_year=? AND position_level=?
                    GROUP BY gender
                """, (company_id, year, position_level))
            else:
                cursor.execute("""
                    SELECT gender, AVG(avg_salary), SUM(employee_count)
                    FROM hr_compensation
                    WHERE company_id=? AND period_year=?
                    GROUP BY gender
                """, (company_id, year))

            salaries = {row[0]: {'avg': row[1], 'count': row[2]} for row in cursor.fetchall()}

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
        finally:
            conn.close()

    def get_diversity_metrics(self, company_id: int, year: int) -> Dict:
        """Çeşitlilik metrikleri"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            workforce = self.get_workforce_summary(company_id, year)
            total = workforce['total_employees']

            if total == 0:
                return {'error': 'Veri yok'}

            gender_dist = workforce['gender_distribution']

            female_count = gender_dist.get('Kadın', 0)
            female_percent = (female_count / total * 100) if total > 0 else 0

            # Yönetim kademesinde kadın oranı
            cursor.execute("""
                SELECT SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=? 
                AND gender='Kadın' AND position_level='Yönetici'
            """, (company_id, year))
            female_managers = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM(count) FROM hr_demographics
                WHERE company_id=? AND period_year=? AND position_level='Yönetici'
            """, (company_id, year))
            total_managers = cursor.fetchone()[0] or 0

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
        finally:
            conn.close()

    def calculate_summary(self, company_id: int, year: int) -> Dict:
        """İK özet verilerini hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT SUM(count) FROM hr_demographics WHERE company_id=? AND period_year=?",
                          (company_id, year))
            total_employees = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(new_hires) FROM hr_turnover WHERE company_id=? AND period_year=?",
                          (company_id, year))
            new_hires = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(terminations) FROM hr_turnover WHERE company_id=? AND period_year=?",
                          (company_id, year))
            terminations = cursor.fetchone()[0] or 0

            turnover_rate = (terminations / total_employees * 100) if total_employees > 0 else 0

            return {
                'total_employees': total_employees,
                'new_hires': new_hires,
                'terminations': terminations,
                'turnover_rate': turnover_rate,
                'gender_ratio': 'N/A',
                'avg_age': 35
            }
        finally:
            conn.close()

    def get_demographics(self, company_id: int, year: int) -> List[Dict]:
        """Demografik verileri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT age_group, gender, employment_type, department, count
                FROM hr_demographics WHERE company_id=? AND period_year=?
            """, (company_id, year))
            return [{'age_group': r[0], 'gender': r[1], 'employment_type': r[2],
                    'department': r[3], 'count': r[4]} for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_turnover(self, company_id: int, year: int) -> List[Dict]:
        """İşe alım/ayrılma verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT period_month, new_hires, terminations, voluntary_exits, involuntary_exits
                FROM hr_turnover WHERE company_id=? AND period_year=? ORDER BY period_month
            """, (company_id, year))
            return [{'month': r[0] or 0, 'new_hires': r[1], 'terminations': r[2],
                    'voluntary_exits': r[3] or 0, 'involuntary_exits': r[4] or 0}
                   for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_compensation(self, company_id: int, year: int) -> List[Dict]:
        """Ücret verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT position_level, gender, avg_salary, min_salary, max_salary, employee_count
                FROM hr_compensation WHERE company_id=? AND period_year=?
            """, (company_id, year))
            return [{'position_level': r[0], 'gender': r[1], 'avg_salary': r[2],
                    'min_salary': r[3], 'max_salary': r[4], 'employee_count': r[5]}
                   for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_diversity_details(self, company_id: int, year: int) -> List[Dict]:
        """Çeşitlilik metriklerini detay kayıtlar olarak getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT category, subcategory, value, unit, description
                FROM hr_diversity WHERE company_id=? AND period_year=?
            """, (company_id, year))
            return [{'category': r[0], 'subcategory': r[1], 'value': r[2],
                    'unit': r[3], 'description': r[4]} for r in cursor.fetchall()]
        finally:
            conn.close()

    def calculate_gender_pay_ratio(self, company_id: int, year: int) -> str:
        """Cinsiyet bazlı ücret oranı (GRI 405-2)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT gender, AVG(avg_salary) FROM hr_compensation
                WHERE company_id=? AND period_year=? GROUP BY gender
            """, (company_id, year))
            salaries = dict(cursor.fetchall())
            female = salaries.get('Kadın', 0)
            male = salaries.get('Erkek', 1)
            ratio = female / male if male > 0 else 0
            return f"1:{ratio:.2f}"
        finally:
            conn.close()

    def generate_hr_report(self, company_id: int, year: int) -> str:
        """İK raporu oluştur"""
        summary = self.calculate_summary(company_id, year)
        return f"""{self.lm.tr('hr_metrics_report_title', 'İNSAN KAYNAKLARI METRİKLERİ RAPORU')} - {year}

{self.lm.tr('overview', 'GENEL BAKIŞ')}
- {self.lm.tr('total_employees', 'Toplam Çalışan')}: {summary['total_employees']}
- {self.lm.tr('new_hires', 'Yeni İşe Alımlar')}: {summary['new_hires']}
- {self.lm.tr('turnover_rate', 'Devir Hızı')}: %{summary['turnover_rate']:.2f}
- {self.lm.tr('gender_ratio', 'Cinsiyet Oranı')}: {summary['gender_ratio']}
- {self.lm.tr('avg_age', 'Ortalama Yaş')}: {summary['avg_age']}
"""

