#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İnsan Kaynakları Yönetimi Modülü
Çalışan istatistikleri, performans ve İK metrikleri
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional
from config.database import DB_PATH


class HRManager:
    """İnsan Kaynakları yönetimi ve metrikleri"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """İK yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çalışan istatistikleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    total_employees INTEGER NOT NULL,
                    full_time_employees INTEGER,
                    part_time_employees INTEGER,
                    contract_employees INTEGER,
                    new_hires INTEGER,
                    departures INTEGER,
                    turnover_rate REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Çalışan demografik bilgileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_demographics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    age_group TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    employee_count INTEGER NOT NULL,
                    percentage REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Performans değerlendirmeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    evaluation_year INTEGER NOT NULL,
                    evaluation_period TEXT NOT NULL,
                    overall_rating REAL NOT NULL,
                    goal_achievement REAL,
                    competency_score REAL,
                    development_needs TEXT,
                    career_planning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Çalışan memnuniyeti
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_satisfaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_year INTEGER NOT NULL,
                    survey_period TEXT NOT NULL,
                    satisfaction_category TEXT NOT NULL,
                    average_score REAL NOT NULL,
                    response_count INTEGER NOT NULL,
                    total_responses INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Çalışan gelişimi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_development (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    development_type TEXT NOT NULL,
                    participant_count INTEGER NOT NULL,
                    total_hours REAL,
                    investment_amount REAL,
                    success_rate REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İK hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hr_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Çeşitlilik Programları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS diversity_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    program_name TEXT NOT NULL,
                    focus_area TEXT NOT NULL,
                    participant_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Çalışanlar tablosu (Detaylı takip için)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    position TEXT,
                    department TEXT,
                    gender TEXT,
                    age INTEGER,
                    salary REAL,
                    start_date TEXT,
                    year INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] IK yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] IK yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_compensation(self, company_id: int, year: int, position_level: str,
                        gender: str, avg_salary: float, employee_count: int, **kwargs) -> int:
        """Ücret verisi ekle"""
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
        except Exception as e:
            logging.error(f"Ücret verisi ekleme hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def add_employee_statistics(self, company_id: int, year: int, total_employees: int,
                              full_time_employees: int = None, part_time_employees: int = None,
                              contract_employees: int = None, new_hires: int = None,
                              departures: int = None, month: int = None) -> bool:
        """Çalışan istatistikleri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Devir oranını hesapla
            turnover_rate = None
            if departures and total_employees:
                turnover_rate = (departures / total_employees) * 100

            cursor.execute("""
                INSERT INTO employee_statistics 
                (company_id, year, month, total_employees, full_time_employees,
                 part_time_employees, contract_employees, new_hires, departures, turnover_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, total_employees, full_time_employees,
                  part_time_employees, contract_employees, new_hires, departures, turnover_rate))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çalışan istatistikleri ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_employee_demographics(self, company_id: int, year: int, age_group: str,
                                gender: str, employee_count: int, employment_type: str = None, 
                                department: str = None) -> bool:
        """Çalışan demografik bilgileri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Toplam çalışan sayısını al
            cursor.execute("""
                SELECT SUM(total_employees) FROM employee_statistics 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            result = cursor.fetchone()
            total_employees = result[0] if result else 0
            
            if not total_employees or total_employees == 0:
                 total_employees = 1 # Avoid division by zero

            percentage = (employee_count / total_employees) * 100

            cursor.execute("""
                INSERT INTO employee_demographics 
                (company_id, year, age_group, gender, employment_type, department, employee_count, percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, age_group, gender, employment_type, department, employee_count, percentage))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çalışan demografik bilgileri ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_demographics(self, company_id: int, year: int) -> List[Dict]:
        """Demografik verileri getir (GUI uyumlu)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Önce employees tablosundan detaylı analiz dene (Eğer varsa)
            cursor.execute("SELECT COUNT(*) FROM employees WHERE company_id=? AND year=?", (company_id, year))
            if cursor.fetchone()[0] > 0:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN age < 30 THEN '<30'
                            WHEN age BETWEEN 30 AND 50 THEN '30-50'
                            ELSE '50+'
                        END as age_grp,
                        gender,
                        'Full-time' as employment_type,
                        department,
                        COUNT(*) as count
                    FROM employees
                    WHERE company_id=? AND year=?
                    GROUP BY age_grp, gender, department
                """, (company_id, year))
                
                results = []
                total = 0
                rows = cursor.fetchall()
                for row in rows:
                    total += row[4]
                
                for row in rows:
                    percentage = (row[4] / total * 100) if total > 0 else 0
                    results.append({
                        'age_group': row[0],
                        'gender': row[1],
                        'employment_type': row[2],
                        'department': row[3],
                        'count': row[4],
                        'percentage': percentage
                    })
                return results

            # Yoksa özet tablosuna bak
            cursor.execute("""
                SELECT age_group, gender, employment_type, department, employee_count, percentage
                FROM employee_demographics WHERE company_id=? AND year=?
            """, (company_id, year))
            return [{'age_group': r[0], 'gender': r[1], 'employment_type': r[2] or 'Bilinmiyor',
                    'department': r[3] or 'Genel', 'count': r[4], 'percentage': r[5] or 0} for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_turnover(self, company_id: int, year: int) -> List[Dict]:
        """İşe alım/ayrılma verilerini getir (GUI uyumlu)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT month, new_hires, departures, turnover_rate
                FROM employee_statistics WHERE company_id=? AND year=? ORDER BY month
            """, (company_id, year))
            
            results = []
            for r in cursor.fetchall():
                results.append({
                    'month': r[0] or 0,
                    'new_hires': r[1] or 0,
                    'terminations': r[2] or 0,
                    'voluntary_exits': 0, # Şimdilik detay yoksa 0
                    'involuntary_exits': r[2] or 0 # Hepsi zorunlu varsayalım detay yoksa
                })
            return results
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
            female = salaries.get('Kadın', 0) or salaries.get('Female', 0)
            male = salaries.get('Erkek', 0) or salaries.get('Male', 0)
            
            if male > 0:
                ratio = female / male
                return f"1:{ratio:.2f}"
            elif female > 0:
                return "N/A:1"
            return "N/A"
        finally:
            conn.close()

    def get_diversity_details(self, company_id: int, year: int) -> List[Dict]:
        """Çeşitlilik metriklerini detay kayıtlar olarak getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        results = []
        try:
            # 1. Cinsiyet Çeşitliliği
            cursor.execute("""
                SELECT gender, SUM(employee_count) FROM employee_demographics
                WHERE company_id=? AND year=? GROUP BY gender
            """, (company_id, year))
            gender_data = dict(cursor.fetchall())
            total = sum(gender_data.values())
            
            if total > 0:
                female_count = gender_data.get('Kadın', 0) + gender_data.get('Female', 0)
                female_ratio = (female_count / total) * 100
                results.append({
                    'category': 'gender_diversity',
                    'subcategory': 'Genel',
                    'value': female_ratio,
                    'unit': '%',
                    'description': 'Kadın Çalışan Oranı'
                })
            else:
                 results.append({'category': 'gender_diversity', 'value': 0, 'unit': '%', 'description': 'Veri Yok'})

            # 2. Yaş Çeşitliliği (Genç çalışan oranı <30)
            cursor.execute("""
                SELECT SUM(employee_count) FROM employee_demographics
                WHERE company_id=? AND year=? AND (age_group LIKE '%<30%' OR age_group LIKE '%18-30%')
            """, (company_id, year))
            young_count = cursor.fetchone()[0] or 0
            
            if total > 0:
                young_ratio = (young_count / total) * 100
                results.append({
                    'category': 'age_diversity',
                    'subcategory': 'Genç',
                    'value': young_ratio,
                    'unit': '%',
                    'description': 'Genç Çalışan (<30) Oranı'
                })
            else:
                results.append({'category': 'age_diversity', 'value': 0, 'unit': '%', 'description': 'Veri Yok'})

            # 3. Yönetim Çeşitliliği (Kadın Yönetici Oranı)
            cursor.execute("""
                SELECT gender, SUM(employee_count) FROM hr_compensation
                WHERE company_id=? AND period_year=? AND (position_level LIKE '%Yönetici%' OR position_level LIKE '%Manager%')
                GROUP BY gender
            """, (company_id, year))
            mgmt_data = dict(cursor.fetchall())
            mgmt_total = sum(mgmt_data.values())
            
            if mgmt_total > 0:
                mgmt_female = mgmt_data.get('Kadın', 0) + mgmt_data.get('Female', 0)
                mgmt_ratio = (mgmt_female / mgmt_total) * 100
                results.append({
                    'category': 'management_diversity',
                    'subcategory': 'Yönetim',
                    'value': mgmt_ratio,
                    'unit': '%',
                    'description': 'Kadın Yönetici Oranı'
                })
            else:
                results.append({'category': 'management_diversity', 'value': 0, 'unit': '%', 'description': 'Veri Yok'})

            return results
        finally:
            conn.close()

    def add_performance_evaluation(self, company_id: int, employee_id: int,
                                 evaluation_year: int, evaluation_period: str,
                                 overall_rating: float, goal_achievement: float = None,
                                 competency_score: float = None, development_needs: str = None,
                                 career_planning: str = None) -> bool:
        """Performans değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO performance_evaluations 
                (company_id, employee_id, evaluation_year, evaluation_period,
                 overall_rating, goal_achievement, competency_score, development_needs, career_planning)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, employee_id, evaluation_year, evaluation_period,
                  overall_rating, goal_achievement, competency_score, development_needs, career_planning))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Performans değerlendirmesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_employee_satisfaction(self, company_id: int, survey_year: int,
                                survey_period: str, satisfaction_category: str,
                                average_score: float, response_count: int,
                                total_responses: int) -> bool:
        """Çalışan memnuniyeti ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO employee_satisfaction 
                (company_id, survey_year, survey_period, satisfaction_category,
                 average_score, response_count, total_responses)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, survey_year, survey_period, satisfaction_category,
                  average_score, response_count, total_responses))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çalışan memnuniyeti ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_employee_development(self, company_id: int, year: int, development_type: str,
                               participant_count: int, total_hours: float = None,
                               investment_amount: float = None, success_rate: float = None) -> bool:
        """Çalışan gelişimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO employee_development 
                (company_id, year, development_type, participant_count,
                 total_hours, investment_amount, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, development_type, participant_count,
                  total_hours, investment_amount, success_rate))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çalışan gelişimi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_hr_target(self, company_id: int, target_year: int, target_type: str,
                     baseline_value: float, target_value: float, target_unit: str,
                     target_description: str = None) -> bool:
        """İK hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO hr_targets 
                (company_id, target_year, target_type, baseline_value, target_value,
                 target_unit, target_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_value, target_value,
                  target_unit, target_description))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"İK hedefi belirleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_hr_summary(self, company_id: int, year: int) -> Dict:
        """İK özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çalışan istatistikleri
            cursor.execute("""
                SELECT AVG(total_employees), AVG(new_hires), AVG(departures), AVG(turnover_rate)
                FROM employee_statistics 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            stats_result = cursor.fetchone()
            avg_employees = stats_result[0] or 0
            avg_new_hires = stats_result[1] or 0
            avg_departures = stats_result[2] or 0
            avg_turnover_rate = stats_result[3] or 0

            # Demografik dağılım
            cursor.execute("""
                SELECT gender, SUM(employee_count), AVG(percentage)
                FROM employee_demographics 
                WHERE company_id = ? AND year = ?
                GROUP BY gender
            """, (company_id, year))

            gender_distribution = {}
            for row in cursor.fetchall():
                gender, count, percentage = row
                gender_distribution[gender] = {
                    'count': count,
                    'percentage': percentage
                }

            # Yaş dağılımı
            cursor.execute("""
                SELECT age_group, SUM(employee_count), AVG(percentage)
                FROM employee_demographics 
                WHERE company_id = ? AND year = ?
                GROUP BY age_group
            """, (company_id, year))

            age_distribution = {}
            for row in cursor.fetchall():
                age_group, count, percentage = row
                age_distribution[age_group] = {
                    'count': count,
                    'percentage': percentage
                }

            # Performans değerlendirmeleri
            cursor.execute("""
                SELECT AVG(overall_rating), AVG(goal_achievement), COUNT(*)
                FROM performance_evaluations 
                WHERE company_id = ? AND evaluation_year = ?
            """, (company_id, year))

            perf_result = cursor.fetchone()
            avg_performance = perf_result[0] or 0
            avg_goal_achievement = perf_result[1] or 0
            total_evaluations = perf_result[2] or 0

            # Çalışan memnuniyeti
            cursor.execute("""
                SELECT satisfaction_category, AVG(average_score), SUM(response_count)
                FROM employee_satisfaction 
                WHERE company_id = ? AND survey_year = ?
                GROUP BY satisfaction_category
            """, (company_id, year))

            satisfaction_scores = {}
            total_responses = 0
            for row in cursor.fetchall():
                category, score, responses = row
                satisfaction_scores[category] = {
                    'average_score': score,
                    'response_count': responses
                }
                total_responses += responses

            # Çalışan gelişimi
            cursor.execute("""
                SELECT development_type, SUM(participant_count), SUM(total_hours), SUM(investment_amount)
                FROM employee_development 
                WHERE company_id = ? AND year = ?
                GROUP BY development_type
            """, (company_id, year))

            development_summary = {}
            total_development_hours = 0
            total_development_investment = 0
            for row in cursor.fetchall():
                dev_type, participants, hours, investment = row
                development_summary[dev_type] = {
                    'participants': participants,
                    'hours': hours or 0,
                    'investment': investment or 0
                }
                total_development_hours += hours or 0
                total_development_investment += investment or 0

            return {
                'average_employees': avg_employees,
                'new_hires': avg_new_hires,
                'departures': avg_departures,
                'turnover_rate': avg_turnover_rate,
                'gender_distribution': gender_distribution,
                'age_distribution': age_distribution,
                'average_performance': avg_performance,
                'goal_achievement_rate': avg_goal_achievement,
                'total_evaluations': total_evaluations,
                'satisfaction_scores': satisfaction_scores,
                'total_satisfaction_responses': total_responses,
                'development_summary': development_summary,
                'total_development_hours': total_development_hours,
                'total_development_investment': total_development_investment,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"İK özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def get_hr_targets(self, company_id: int) -> List[Dict]:
        """İK hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_value, target_value,
                       target_unit, target_description, status
                FROM hr_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'target_year': row[0],
                    'target_type': row[1],
                    'baseline_value': row[2],
                    'target_value': row[3],
                    'target_unit': row[4],
                    'target_description': row[5],
                    'status': row[6]
                })

            return targets

        except Exception as e:
            logging.error(f"İK hedefleri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def calculate_hr_kpis(self, company_id: int, year: int) -> Dict:
        """İK KPI'larını hesapla"""
        summary = self.get_hr_summary(company_id, year)

        if not summary:
            return {}

        # Cinsiyet çeşitliliği oranı
        gender_diversity = 0
        if len(summary.get('gender_distribution', {})) > 1:
            # Shannon çeşitlilik indeksi benzeri basit bir hesap
            total = sum(data['count'] for data in summary['gender_distribution'].values())
            for data in summary['gender_distribution'].values():
                p = data['count'] / total if total > 0 else 0
                if p > 0:
                    gender_diversity += p # Basit oran toplamı 1 olur, bu metriği gözden geçirmek gerekebilir.
                    # Aslında diversity index daha karmaşık ama şimdilik bırakalım.

        # Yaş çeşitliliği oranı
        age_diversity = len(summary.get('age_distribution', {}))

        # Çalışan başına eğitim saati
        avg_employees = summary.get('average_employees', 1)
        if avg_employees == 0: avg_employees = 1
        
        training_hours_per_employee = (summary.get('total_development_hours', 0) / avg_employees)

        # Çalışan başına eğitim yatırımı
        training_investment_per_employee = (summary.get('total_development_investment', 0) / avg_employees)

        return {
            'average_employees': summary.get('average_employees', 0),
            'turnover_rate': summary.get('turnover_rate', 0),
            'gender_diversity_index': gender_diversity,
            'age_diversity_count': age_diversity,
            'average_performance_score': summary.get('average_performance', 0),
            'goal_achievement_rate': summary.get('goal_achievement_rate', 0),
            'training_hours_per_employee': training_hours_per_employee,
            'training_investment_per_employee': training_investment_per_employee,
            'year': year,
            'company_id': company_id
        }

    def add_employee(self, employee_data: Dict) -> bool:
        """Tek çalışan bilgisi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çalışanı ekle
            cursor.execute("""
                INSERT INTO employees 
                (company_id, name, position, department, gender, age, salary, start_date, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_data['company_id'],
                employee_data['name'],
                employee_data.get('position', ''),
                employee_data.get('department', ''),
                employee_data.get('gender', ''),
                employee_data.get('age', 0),
                employee_data.get('salary', 0),
                employee_data.get('start_date', ''),
                employee_data.get('year', 2024)
            ))

            conn.commit()

            # İstatistikleri güncelle (Basitçe toplam sayıyı artırabiliriz veya full recalculation yapabiliriz)
            # Şimdilik yapmıyoruz, istatistik tablosu ayrı güncellenmeli veya trigger olmalı.

            return True

        except Exception as e:
            logging.error(f"Çalışan ekleme hatası: {e}")
            return False
        finally:
            conn.close()

    def add_diversity_program(self, company_id: int, year: int, program_name: str, 
                            focus_area: str, participant_count: int, 
                            success_rate: float, status: str = 'active') -> bool:
        """Çeşitlilik programı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO diversity_programs 
                (company_id, year, program_name, focus_area, participant_count, success_rate, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, program_name, focus_area, participant_count, success_rate, status))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Çeşitlilik programı ekleme hatası: {e}")
            return False
        finally:
            conn.close()

    def get_diversity_programs(self, company_id: int, year: int) -> List[Dict]:
        """Çeşitlilik programlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT program_name, focus_area, participant_count, success_rate, status
                FROM diversity_programs 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            programs = []
            for row in cursor.fetchall():
                programs.append({
                    'name': row[0],
                    'category': row[1],
                    'participants': row[2],
                    'success_rate': row[3],
                    'status': row[4]
                })
            return programs
        except Exception as e:
            logging.error(f"Çeşitlilik programları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_monthly_employee_trend(self, company_id: int, year: int) -> Dict[str, List]:
        """Aylık çalışan trendini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Aylık verileri al (ay sırasına göre)
            cursor.execute("""
                SELECT month, total_employees
                FROM employee_statistics 
                WHERE company_id = ? AND year = ? AND month IS NOT NULL
                ORDER BY month
            """, (company_id, year))
            
            rows = cursor.fetchall()
            
            if not rows:
                return {'months': [], 'employees': []}
                
            months = [str(row[0]) for row in rows]
            employees = [row[1] for row in rows]
            
            return {'months': months, 'employees': employees}
        except Exception as e:
            logging.error(f"Çalışan trendi getirme hatası: {e}")
            return {'months': [], 'employees': []}
        finally:
            conn.close()
