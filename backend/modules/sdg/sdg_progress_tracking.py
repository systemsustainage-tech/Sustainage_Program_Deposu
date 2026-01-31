#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG İlerleme Takibi Sistemi
Veri toplama sisteminden gelen verileri analiz ederek ilerleme takibi
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.database import DB_PATH


class SDGProgressTracking:
    """SDG İlerleme Takibi Sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            # Proje kökü: modules/sdg/ -> .. -> ..
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(project_root, db_path)
        else:
            self.db_path = db_path
        # DB klasörünü garanti et
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._create_tables()

    def _create_tables(self) -> None:
        """İlerleme takibi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SDG hedef ilerleme tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_goal_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                sdg_title TEXT NOT NULL,
                total_indicators INTEGER DEFAULT 0,
                completed_indicators INTEGER DEFAULT 0,
                in_progress_indicators INTEGER DEFAULT 0,
                not_started_indicators INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                UNIQUE(company_id, sdg_no)
            )
        """)

        # SDG gösterge ilerleme detayları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_indicator_progress_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                target_code TEXT NOT NULL,
                target_title TEXT NOT NULL,
                question_1_status TEXT DEFAULT 'not_answered',
                question_2_status TEXT DEFAULT 'not_answered',
                question_3_status TEXT DEFAULT 'not_answered',
                question_1_answer_date TEXT,
                question_2_answer_date TEXT,
                question_3_answer_date TEXT,
                completion_percentage REAL DEFAULT 0.0,
                last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG trend analizi tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_progress_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                measurement_date TEXT NOT NULL,
                completion_percentage REAL NOT NULL,
                answered_questions INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                new_answers INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG performans metrikleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                measurement_date TEXT NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()
        logging.info("SDG ilerleme takibi tabloları oluşturuldu")

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def calculate_goal_progress(self, company_id: int, sdg_no: int) -> Dict:
        """SDG hedef ilerlemesini hesapla
        Not: sdg_no parametresi SDG kodunu (1-17) temsil eder. Başlık ve seçim filtresi bu koda göre yapılır.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # İlgili goal_id'yi ve başlığı koddan al
            cursor.execute("SELECT id, title_tr FROM sdg_goals WHERE code = ?", (sdg_no,))
            goal_row = cursor.fetchone()
            goal_id = goal_row[0] if goal_row else None
            sdg_title = goal_row[1] if goal_row else f"SDG {sdg_no}"

            # Şirketin bu hedef için seçtiği gösterge kodlarını al
            selected_codes: List[str] = []
            if goal_id is not None:
                cursor.execute(
                    """
                    SELECT i.code
                    FROM selections s
                    JOIN sdg_indicators i ON s.indicator_id = i.id
                    WHERE s.company_id = ? AND s.selected = 1 AND s.goal_id = ?
                    ORDER BY i.code
                    """,
                    (company_id, goal_id)
                )
                selected_codes = [row[0] for row in cursor.fetchall()]

            # Gösterge durumlarını al (seçili kodlar varsa onlara göre filtrele)
            if selected_codes:
                placeholders = ",".join(["?"] * len(selected_codes))
                query = (
                    """
                    SELECT indicator_code, indicator_title, target_code, target_title,
                           answered_questions, total_questions, completion_percentage,
                           question_1_answered, question_2_answered, question_3_answered
                    FROM sdg_indicator_status 
                    WHERE company_id = ? AND sdg_no = ? AND indicator_code IN (""" + placeholders + ")"
                )
                params = [company_id, sdg_no] + selected_codes
                cursor.execute(query, params)
            else:
                # Seçim yoksa sadece hedef koduna göre filtrele
                cursor.execute(
                    """
                    SELECT indicator_code, indicator_title, target_code, target_title,
                           answered_questions, total_questions, completion_percentage,
                           question_1_answered, question_2_answered, question_3_answered
                    FROM sdg_indicator_status 
                    WHERE company_id = ? AND sdg_no = ?
                    """,
                    (company_id, sdg_no)
                )

            indicators = cursor.fetchall()

            if not indicators:
                return {
                    'sdg_no': sdg_no,
                    'sdg_title': sdg_title,
                    'total_indicators': 0,
                    'completed_indicators': 0,
                    'in_progress_indicators': 0,
                    'not_started_indicators': 0,
                    'completion_percentage': 0.0,
                    'indicators': []
                }

            # İlerleme kategorilerini hesapla
            completed = 0
            in_progress = 0
            not_started = 0
            total_completion = 0.0

            indicator_details = []

            for indicator in indicators:
                completion = indicator[6] or 0.0
                answered_questions = indicator[4] or 0
                total_questions = indicator[5] or 3

                if completion == 100.0:
                    completed += 1
                    status = 'completed'
                elif completion > 0:
                    in_progress += 1
                    status = 'in_progress'
                else:
                    not_started += 1
                    status = 'not_started'

                total_completion += completion

                indicator_details.append({
                    'indicator_code': indicator[0],
                    'indicator_title': indicator[1],
                    'target_code': indicator[2],
                    'target_title': indicator[3],
                    'answered_questions': answered_questions,
                    'total_questions': total_questions,
                    'completion_percentage': completion,
                    'status': status,
                    'question_1_answered': bool(indicator[7]),
                    'question_2_answered': bool(indicator[8]),
                    'question_3_answered': bool(indicator[9])
                })

            # Ortalama tamamlanma yüzdesi
            avg_completion = total_completion / len(indicators) if indicators else 0.0

            result = {
                'sdg_no': sdg_no,
                'sdg_title': sdg_title,
                'total_indicators': len(indicators),
                'completed_indicators': completed,
                'in_progress_indicators': in_progress,
                'not_started_indicators': not_started,
                'completion_percentage': round(avg_completion, 2),
                'indicators': indicator_details
            }

            # Veritabanına kaydet
            self._save_goal_progress(company_id, result)

            return result

        except Exception as e:
            logging.error(f"SDG hedef ilerlemesi hesaplanırken hata: {e}")
            return {
                'sdg_no': sdg_no,
                'total_indicators': 0,
                'completed_indicators': 0,
                'in_progress_indicators': 0,
                'not_started_indicators': 0,
                'completion_percentage': 0.0,
                'indicators': []
            }
        finally:
            conn.close()

    def _save_goal_progress(self, company_id: int, progress_data: Dict) -> None:
        """Hedef ilerlemesini veritabanına kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_goal_progress 
                (company_id, sdg_no, sdg_title, total_indicators, completed_indicators,
                 in_progress_indicators, not_started_indicators, completion_percentage, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                company_id, progress_data['sdg_no'], progress_data['sdg_title'],
                progress_data['total_indicators'], progress_data['completed_indicators'],
                progress_data['in_progress_indicators'], progress_data['not_started_indicators'],
                progress_data['completion_percentage']
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"Hedef ilerlemesi kaydedilirken hata: {e}")
        finally:
            conn.close()

    def get_all_goals_progress(self, company_id: int) -> Dict:
        """Tüm SDG hedeflerinin ilerlemesini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Tüm SDG hedeflerini al
            cursor.execute("SELECT id, code, title_tr FROM sdg_goals ORDER BY code")
            goals = cursor.fetchall()

            all_progress = []
            total_indicators = 0
            total_completed = 0
            total_in_progress = 0
            total_not_started = 0
            total_completion = 0.0

            for goal in goals:
                sdg_no = goal[0]
                progress = self.calculate_goal_progress(company_id, sdg_no)
                all_progress.append(progress)

                total_indicators += progress['total_indicators']
                total_completed += progress['completed_indicators']
                total_in_progress += progress['in_progress_indicators']
                total_not_started += progress['not_started_indicators']
                total_completion += progress['completion_percentage']

            # Genel özet
            overall_progress = {
                'total_goals': len(goals),
                'total_indicators': total_indicators,
                'total_completed': total_completed,
                'total_in_progress': total_in_progress,
                'total_not_started': total_not_started,
                'overall_completion': round(total_completion / len(goals), 2) if goals else 0.0,
                'goals': all_progress
            }

            return overall_progress

        except Exception as e:
            logging.error(f"Tüm hedefler ilerlemesi getirilirken hata: {e}")
            return {
                'total_goals': 0,
                'total_indicators': 0,
                'total_completed': 0,
                'total_in_progress': 0,
                'total_not_started': 0,
                'overall_completion': 0.0,
                'goals': []
            }
        finally:
            conn.close()

    def get_progress_trends(self, company_id: int, sdg_no: Optional[int] = None, days: int = 30) -> List[Dict]:
        """İlerleme trendlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Tarih aralığı
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            if sdg_no:
                cursor.execute("""
                    SELECT measurement_date, completion_percentage, answered_questions, 
                           total_questions, new_answers
                    FROM sdg_progress_trends 
                    WHERE company_id = ? AND sdg_no = ? 
                    AND measurement_date >= ? AND measurement_date <= ?
                    ORDER BY measurement_date
                """, (company_id, sdg_no, start_date.isoformat(), end_date.isoformat()))
            else:
                cursor.execute("""
                    SELECT measurement_date, AVG(completion_percentage) as avg_completion,
                           SUM(answered_questions) as total_answered,
                           SUM(total_questions) as total_questions,
                           SUM(new_answers) as total_new_answers
                    FROM sdg_progress_trends 
                    WHERE company_id = ? 
                    AND measurement_date >= ? AND measurement_date <= ?
                    GROUP BY measurement_date
                    ORDER BY measurement_date
                """, (company_id, start_date.isoformat(), end_date.isoformat()))

            trends = []
            for row in cursor.fetchall():
                trends.append({
                    'date': row[0],
                    'completion_percentage': row[1],
                    'answered_questions': row[2],
                    'total_questions': row[3],
                    'new_answers': row[4] if len(row) > 4 else 0
                })

            return trends

        except Exception as e:
            logging.error(f"İlerleme trendleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def record_progress_snapshot(self, company_id: int, sdg_no: int) -> None:
        """İlerleme anlık görüntüsünü kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Mevcut ilerleme durumunu al
            progress = self.calculate_goal_progress(company_id, sdg_no)

            # Toplam soru sayısını hesapla
            total_questions = sum(ind['total_questions'] for ind in progress['indicators'])
            answered_questions = sum(ind['answered_questions'] for ind in progress['indicators'])

            # Önceki kaydı kontrol et
            cursor.execute("""
                SELECT answered_questions FROM sdg_progress_trends 
                WHERE company_id = ? AND sdg_no = ? 
                ORDER BY measurement_date DESC LIMIT 1
            """, (company_id, sdg_no))

            previous_record = cursor.fetchone()
            new_answers = 0
            if previous_record:
                new_answers = max(0, answered_questions - previous_record[0])

            # Yeni kayıt oluştur
            cursor.execute("""
                INSERT INTO sdg_progress_trends 
                (company_id, sdg_no, measurement_date, completion_percentage,
                 answered_questions, total_questions, new_answers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, sdg_no, datetime.now().isoformat(),
                progress['completion_percentage'], answered_questions,
                total_questions, new_answers
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"İlerleme anlık görüntüsü kaydedilirken hata: {e}")
        finally:
            conn.close()

    def get_performance_metrics(self, company_id: int, sdg_no: Optional[int] = None) -> List[Dict]:
        """Performans metriklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if sdg_no:
                cursor.execute("""
                    SELECT metric_name, metric_value, metric_unit, measurement_date, indicator_code
                    FROM sdg_performance_metrics 
                    WHERE company_id = ? AND sdg_no = ?
                    ORDER BY measurement_date DESC
                """, (company_id, sdg_no))
            else:
                cursor.execute("""
                    SELECT metric_name, metric_value, metric_unit, measurement_date, indicator_code
                    FROM sdg_performance_metrics 
                    WHERE company_id = ?
                    ORDER BY measurement_date DESC
                """, (company_id,))

            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    'metric_name': row[0],
                    'metric_value': row[1],
                    'metric_unit': row[2],
                    'measurement_date': row[3],
                    'indicator_code': row[4]
                })

            return metrics

        except Exception as e:
            logging.error(f"Performans metrikleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def add_performance_metric(self, company_id: int, metric_name: str, metric_value: float,
                             metric_unit: Optional[str] = None, sdg_no: Optional[int] = None,
                             indicator_code: Optional[str] = None) -> bool:
        """Performans metriği ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sdg_performance_metrics 
                (company_id, metric_name, metric_value, metric_unit, measurement_date, sdg_no, indicator_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, metric_name, metric_value, metric_unit,
                  datetime.now().isoformat(), sdg_no, indicator_code))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Performans metriği eklenirken hata: {e}")
            return False
        finally:
            conn.close()

    def get_progress_summary(self, company_id: int) -> Dict:
        """İlerleme özetini getir"""
        try:
            all_progress = self.get_all_goals_progress(company_id)

            # En iyi ve en kötü performans
            goals = all_progress['goals']
            if goals:
                best_goal = max(goals, key=lambda x: x['completion_percentage'])
                worst_goal = min(goals, key=lambda x: x['completion_percentage'])

                # Son 7 günlük trend
                recent_trends = self.get_progress_trends(company_id, days=7)
                trend_direction = "stable"
                if len(recent_trends) >= 2:
                    first_completion = recent_trends[0]['completion_percentage']
                    last_completion = recent_trends[-1]['completion_percentage']
                    if last_completion > first_completion + 1:
                        trend_direction = "improving"
                    elif last_completion < first_completion - 1:
                        trend_direction = "declining"
            else:
                best_goal = None
                worst_goal = None
                trend_direction = "stable"

            return {
                'overall': all_progress,
                'best_performing_goal': best_goal,
                'worst_performing_goal': worst_goal,
                'trend_direction': trend_direction,
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"İlerleme özeti getirilirken hata: {e}")
            return {
                'overall': {'total_goals': 0, 'overall_completion': 0.0},
                'best_performing_goal': None,
                'worst_performing_goal': None,
                'trend_direction': 'stable',
                'last_updated': datetime.now().isoformat()
            }

if __name__ == "__main__":
    # Test
    progress_tracking = SDGProgressTracking()
    logging.info("SDG İlerleme Takibi Sistemi başlatıldı")

    # Test ilerleme hesaplama
    progress = progress_tracking.calculate_goal_progress(1, 9)
    logging.info(f"SDG 9 ilerlemesi: {progress['completion_percentage']}%")
