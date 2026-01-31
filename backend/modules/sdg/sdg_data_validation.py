#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Veri Doğrulama Sistemi
Veri tutarlılığı, eksik veri tespiti ve kalite kontrolü
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from config.database import DB_PATH


class SDGDataValidation:
    """SDG Veri Doğrulama Sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path

        self._create_validation_tables()

    # --- Kural CRUD ---
    def get_rules(self) -> List[Tuple]:
        """Tüm doğrulama kurallarını getir (id, rule_name, rule_type, is_active)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, rule_name, rule_type, is_active FROM sdg_validation_rules ORDER BY id")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Kurallar getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_rule_by_id(self, rule_id: int) -> Optional[Dict]:
        """Kural detaylarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, rule_name, rule_type, rule_description, validation_expression,
                       error_message, severity_level, is_active, created_at
                FROM sdg_validation_rules WHERE id = ?
                """,
                (rule_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'rule_name': row[1],
                'rule_type': row[2],
                'rule_description': row[3],
                'validation_expression': row[4],
                'error_message': row[5],
                'severity_level': row[6],
                'is_active': bool(row[7]),
                'created_at': row[8],
            }
        except Exception as e:
            logging.error(f"Kural detayları getirilirken hata: {e}")
            return None
        finally:
            conn.close()

    def add_rule(self, rule_name: str, rule_type: str, validation_expression: str,
                 rule_description: Optional[str] = None, error_message: Optional[str] = None,
                 severity_level: str = 'warning', is_active: bool = True) -> Optional[int]:
        """Yeni doğrulama kuralı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO sdg_validation_rules (
                    rule_name, rule_type, rule_description, validation_expression,
                    error_message, severity_level, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (rule_name, rule_type, rule_description, validation_expression,
                 error_message, severity_level, 1 if is_active else 0)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Kural eklenirken hata: {e}")
            return None
        finally:
            conn.close()

    def update_rule(self, rule_id: int, **kwargs) -> bool:
        """Doğrulama kuralını güncelle"""
        allowed = {
            'rule_name', 'rule_type', 'rule_description', 'validation_expression',
            'error_message', 'severity_level', 'is_active'
        }
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
            params = list(fields.values()) + [rule_id]
            cursor.execute(f"UPDATE sdg_validation_rules SET {set_clause} WHERE id = ?", params)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Kural güncellenirken hata: {e}")
            return False
        finally:
            conn.close()

    def delete_rule(self, rule_id: int) -> bool:
        """Doğrulama kuralını sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sdg_validation_rules WHERE id = ?", (rule_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Kural silinirken hata: {e}")
            return False
        finally:
            conn.close()

    def _create_validation_tables(self) -> None:
        """Doğrulama tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Veri doğrulama kuralları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_description TEXT,
                validation_expression TEXT NOT NULL,
                error_message TEXT,
                severity_level TEXT DEFAULT 'warning',
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Veri doğrulama sonuçları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                rule_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                validation_status TEXT NOT NULL,
                error_message TEXT,
                suggested_fix TEXT,
                severity_level TEXT,
                FOREIGN KEY (rule_id) REFERENCES sdg_validation_rules(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Veri kalite skorları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_data_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                completeness_score REAL DEFAULT 0.0,
                accuracy_score REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,
                timeliness_score REAL DEFAULT 0.0,
                overall_quality_score REAL DEFAULT 0.0,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Varsayılan doğrulama kurallarını ekle
        self._insert_default_validation_rules(cursor)

        conn.commit()
        conn.close()
        logging.info("SDG veri doğrulama tabloları oluşturuldu")

    def _insert_default_validation_rules(self, cursor) -> None:
        """Varsayılan doğrulama kurallarını ekle"""
        rules = [
            # Eksik veri kuralları
            ('missing_data_check', 'completeness', 'Eksik veri kontrolü',
             'response_value IS NULL OR response_value = ""',
             'Bu soru için cevap verilmemiş', 'error'),

            # Sayısal değer kuralları
            ('numeric_range_check', 'accuracy', 'Sayısal değer aralık kontrolü',
             'question_type = "Sayı" AND (CAST(response_value AS REAL) < 0 OR CAST(response_value AS REAL) > 1000000)',
             'Sayısal değer geçersiz aralıkta', 'warning'),

            # Yüzde değer kuralları
            ('percentage_range_check', 'accuracy', 'Yüzde değer aralık kontrolü',
             'question_type = "Yüzde" AND (CAST(response_value AS REAL) < 0 OR CAST(response_value AS REAL) > 100)',
             'Yüzde değeri 0-100 arasında olmalı', 'warning'),

            # Tarih format kuralları
            ('date_format_check', 'consistency', 'Tarih format kontrolü',
             'question_type = "Tarih" AND response_value NOT GLOB "????-??-??"',
             'Tarih formatı YYYY-MM-DD olmalı', 'warning'),

            # Metin uzunluk kuralları
            ('text_length_check', 'completeness', 'Metin uzunluk kontrolü',
             'question_type = "Metin" AND LENGTH(response_value) < 10',
             'Metin cevabı çok kısa (minimum 10 karakter)', 'warning'),

            # Tutarlılık kuralları
            ('consistency_check', 'consistency', 'Veri tutarlılık kontrolü',
             'g.code IS NULL OR i.code IS NULL',
             'SDG numarası ve gösterge kodu tutarlı değil', 'error'),

            # Güncellik kuralları
            ('timeliness_check', 'timeliness', 'Veri güncellik kontrolü',
             'response_date < date("now", "-30 days")',
             'Veri 30 günden eski', 'info')
        ]

        for rule_name, rule_type, description, expression, error_message, severity in rules:
            cursor.execute("""
                INSERT OR IGNORE INTO sdg_validation_rules 
                (rule_name, rule_type, rule_description, validation_expression, error_message, severity_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (rule_name, rule_type, description, expression, error_message, severity))

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def validate_company_data(self, company_id: int) -> Dict[str, Any]:
        """Şirket verilerini doğrula"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Doğrulama kurallarını al
            cursor.execute("""
                SELECT id, rule_name, rule_type, validation_expression, error_message, severity_level
                FROM sdg_validation_rules 
                WHERE is_active = 1
            """)

            rules = cursor.fetchall()

            validation_results: Dict[str, Any] = {
                'company_id': company_id,
                'validation_date': datetime.now().isoformat(),
                'total_rules': len(rules),
                'passed_rules': 0,
                'failed_rules': 0,
                'warnings': 0,
                'errors': 0,
                'info': 0,
                'details': [],
                'quality_scores': {}
            }

            # Eski doğrulama sonuçlarını temizle
            cursor.execute("DELETE FROM sdg_validation_results WHERE company_id = ?", (company_id,))

            # Her kural için doğrulama yap
            for rule_id, rule_name, rule_type, expression, error_message, severity in rules:
                try:
                    # Doğrulama sorgusu
                    query = f"""
                        SELECT qr.id, qr.question_id, qr.response_value, qr.response_date,
                               g.code as sdg_no, i.code as indicator_code, qb.question_type
                        FROM sdg_question_responses qr
                        LEFT JOIN sdg_question_bank qb ON qr.question_id = qb.id
                        LEFT JOIN sdg_indicators i ON qb.indicator_id = i.id
                        LEFT JOIN sdg_targets t ON i.target_id = t.id
                        LEFT JOIN sdg_goals g ON t.goal_id = g.id
                        WHERE qr.company_id = ? AND ({expression})
                    """

                    cursor.execute(query, (company_id,))
                    violations = cursor.fetchall()

                    if violations:
                        validation_results['failed_rules'] += 1
                        
                        # Map severity to result keys
                        severity_key = 'errors' if severity == 'error' else 'warnings' if severity == 'warning' else 'info'
                        if severity_key in validation_results:
                            validation_results[severity_key] += 1

                        for violation in violations:
                            detail = {
                                'rule_id': rule_id,
                                'rule_name': rule_name,
                                'rule_type': rule_type,
                                'severity': severity,
                                'error_message': error_message,
                                'question_id': violation[1],
                                'response_value': violation[2],
                                'response_date': violation[3],
                                'sdg_no': violation[4],
                                'indicator_code': violation[5],
                                'question_type': violation[6],
                                'suggested_fix': self._get_suggested_fix(rule_name, violation)
                            }
                            validation_results['details'].append(detail)

                            # Veritabanına kaydet
                            self._save_validation_result(cursor, company_id, rule_id,
                                                       violation[4], violation[5],
                                                       'failed', error_message,
                                                       detail['suggested_fix'], severity)
                    else:
                        validation_results['passed_rules'] += 1

                except Exception as e:
                    logging.error(f"Kural {rule_name} doğrulanırken hata: {e}")
                    continue

            # Kalite skorlarını hesapla
            quality_scores = self._calculate_quality_scores(cursor, company_id)
            validation_results['quality_scores'] = quality_scores

            # Kalite skorlarını veritabanına kaydet
            cursor.execute("""
                INSERT INTO sdg_data_quality_scores (
                    company_id, completeness_score, accuracy_score, 
                    consistency_score, timeliness_score, overall_quality_score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                company_id, 
                quality_scores['completeness_score'],
                quality_scores['accuracy_score'],
                quality_scores['consistency_score'],
                quality_scores['timeliness_score'],
                quality_scores['overall_quality_score']
            ))

            # Veritabanına kaydet
            conn.commit()

            return validation_results

        except Exception as e:
            logging.error(f"Veri doğrulama sırasında hata: {e}")
            return {'error': str(e)}
        finally:
            conn.close()

    def _get_suggested_fix(self, rule_name: str, violation: Tuple) -> str:
        """Önerilen düzeltme önerisi"""
        fixes = {
            'missing_data_check': 'Bu soru için uygun bir cevap verin',
            'numeric_range_check': 'Sayısal değeri 0-1000000 arasında girin',
            'percentage_range_check': 'Yüzde değerini 0-100 arasında girin',
            'date_format_check': 'Tarihi YYYY-MM-DD formatında girin',
            'text_length_check': 'Daha detaylı bir açıklama yazın (minimum 10 karakter)',
            'consistency_check': 'SDG numarası ve gösterge kodunu kontrol edin',
            'timeliness_check': 'Veriyi güncelleyin'
        }
        return fixes.get(rule_name, 'Veriyi kontrol edin ve düzeltin')

    def _save_validation_result(self, cursor, company_id: int, rule_id: int,
                              sdg_no: int, indicator_code: str, status: str,
                              error_message: str, suggested_fix: str, severity: str):
        """Doğrulama sonucunu kaydet"""
        cursor.execute("""
            INSERT INTO sdg_validation_results 
            (company_id, rule_id, sdg_no, indicator_code, validation_status, 
             error_message, suggested_fix, severity_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, rule_id, sdg_no, indicator_code, status,
              error_message, suggested_fix, severity))

    def _calculate_quality_scores(self, cursor, company_id: int) -> Dict:
        """Kalite skorlarını hesapla"""
        try:
            # Toplam soru sayısı
            cursor.execute("SELECT COUNT(*) FROM sdg_question_bank")
            total_questions = cursor.fetchone()[0]

            # Cevaplanan soru sayısı
            cursor.execute("""
                SELECT COUNT(DISTINCT question_id) FROM sdg_question_responses 
                WHERE company_id = ?
            """, (company_id,))
            answered_questions = cursor.fetchone()[0]

            # Tamamlanma skoru
            completeness_score = (answered_questions / total_questions * 100) if total_questions > 0 else 0

            # Doğruluk skoru (hata sayısına göre)
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_validation_results 
                WHERE company_id = ? AND validation_status = 'failed' AND severity_level = 'error'
            """, (company_id,))
            error_count = cursor.fetchone()[0]

            accuracy_score = max(0, 100 - (error_count * 10))  # Her hata -10 puan

            # Tutarlılık skoru
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_validation_results vr
                JOIN sdg_validation_rules r ON vr.rule_id = r.id
                WHERE vr.company_id = ? AND vr.validation_status = 'failed' AND r.rule_type = 'consistency'
            """, (company_id,))
            consistency_errors = cursor.fetchone()[0]

            consistency_score = max(0, 100 - (consistency_errors * 15))  # Her tutarsızlık -15 puan

            # Güncellik skoru
            cursor.execute("""
                SELECT COUNT(*) FROM sdg_question_responses 
                WHERE company_id = ? AND response_date < date('now', '-30 days')
            """, (company_id,))
            old_responses = cursor.fetchone()[0]

            timeliness_score = max(0, 100 - (old_responses * 5))  # Her eski veri -5 puan

            # Genel kalite skoru
            overall_score = (completeness_score + accuracy_score + consistency_score + timeliness_score) / 4

            return {
                'completeness_score': round(completeness_score, 2),
                'accuracy_score': round(accuracy_score, 2),
                'consistency_score': round(consistency_score, 2),
                'timeliness_score': round(timeliness_score, 2),
                'overall_quality_score': round(overall_score, 2)
            }

        except Exception as e:
            logging.error(f"Kalite skorları hesaplanırken hata: {e}")
            return {
                'completeness_score': 0,
                'accuracy_score': 0,
                'consistency_score': 0,
                'timeliness_score': 0,
                'overall_quality_score': 0
            }

    def calculate_quality_scores(self, company_id: int) -> Dict:
        """Genel kalite skorlarını getir (public helper)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            return self._calculate_quality_scores(cursor, company_id)
        except Exception as e:
            logging.error(f"Kalite skorları alınırken hata: {e}")
            return {
                'completeness_score': 0,
                'accuracy_score': 0,
                'consistency_score': 0,
                'timeliness_score': 0,
                'overall_quality_score': 0
            }
        finally:
            conn.close()

    def calculate_quality_scores_by_sdg(self, company_id: int) -> Dict[int, Dict]:
        """SDG bazlı kalite skorlarını hesapla"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Toplam soru sayısı SDG bazında
            cursor.execute("""
                SELECT g.code, COUNT(qb.id)
                FROM sdg_question_bank qb
                JOIN sdg_indicators i ON qb.indicator_id = i.id
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                GROUP BY g.code
            """)
            total_map = {row[0]: row[1] for row in cursor.fetchall()}

            # Cevaplanan soru sayısı SDG bazında
            cursor.execute("""
                SELECT g.code, COUNT(DISTINCT qr.question_id)
                FROM sdg_question_responses qr
                JOIN sdg_question_bank qb ON qr.question_id = qb.id
                JOIN sdg_indicators i ON qb.indicator_id = i.id
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                WHERE qr.company_id = ?
                GROUP BY g.code
            """, (company_id,))
            answered_map = {row[0]: row[1] for row in cursor.fetchall()}

            # Hata (severity=error) SDG bazında
            cursor.execute("""
                SELECT sdg_no, COUNT(*)
                FROM sdg_validation_results
                WHERE company_id = ? AND validation_status = 'failed' AND severity_level = 'error' AND sdg_no IS NOT NULL
                GROUP BY sdg_no
            """, (company_id,))
            error_map = {row[0]: row[1] for row in cursor.fetchall()}

            # Tutarlılık hataları SDG bazında (rules join)
            cursor.execute("""
                SELECT vr.sdg_no, COUNT(*)
                FROM sdg_validation_results vr
                JOIN sdg_validation_rules r ON vr.rule_id = r.id
                WHERE vr.company_id = ? AND vr.validation_status = 'failed' AND r.rule_type = 'consistency' AND vr.sdg_no IS NOT NULL
                GROUP BY vr.sdg_no
            """, (company_id,))
            consistency_map = {row[0]: row[1] for row in cursor.fetchall()}

            # Eski cevaplar SDG bazında
            cursor.execute("""
                SELECT g.code, COUNT(*)
                FROM sdg_question_responses qr
                JOIN sdg_question_bank qb ON qr.question_id = qb.id
                JOIN sdg_indicators i ON qb.indicator_id = i.id
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                WHERE qr.company_id = ? AND qr.response_date < date('now', '-30 days')
                GROUP BY g.code
            """, (company_id,))
            old_map = {row[0]: row[1] for row in cursor.fetchall()}

            scores_by_sdg: Dict[int, Dict] = {}
            for sdg_no, total in total_map.items():
                answered = answered_map.get(sdg_no, 0)
                errors = error_map.get(sdg_no, 0)
                consistency_errors = consistency_map.get(sdg_no, 0)
                old_responses = old_map.get(sdg_no, 0)

                completeness = (answered / total * 100) if total > 0 else 0
                accuracy = max(0, 100 - (errors * 10))
                consistency = max(0, 100 - (consistency_errors * 15))
                timeliness = max(0, 100 - (old_responses * 5))
                overall = (completeness + accuracy + consistency + timeliness) / 4

                scores_by_sdg[sdg_no] = {
                    'completeness': round(completeness, 2),
                    'accuracy': round(accuracy, 2),
                    'consistency': round(consistency, 2),
                    'timeliness': round(timeliness, 2),
                    'overall': round(overall, 2)
                }

            return scores_by_sdg
        except Exception as e:
            logging.error(f"SDG bazlı kalite skorları hesaplanırken hata: {e}")
            return {}
        finally:
            conn.close()

    def get_validation_summary(self, company_id: int) -> Dict[str, Any]:
        """Doğrulama özetini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Son doğrulama sonuçlarını al
            cursor.execute("""
                SELECT vr.validation_date, vr.severity_level, COUNT(*) as count
                FROM sdg_validation_results vr
                WHERE vr.company_id = ? AND vr.validation_status = 'failed'
                GROUP BY vr.validation_date, vr.severity_level
                ORDER BY vr.validation_date DESC
                LIMIT 1
            """, (company_id,))

            results = cursor.fetchall()

            summary: Dict[str, Any] = {
                'last_validation_date': None,
                'error_count': 0,
                'warning_count': 0,
                'info_count': 0,
                'total_issues': 0
            }

            if results:
                summary['last_validation_date'] = results[0][0]
                for row in results:
                    severity = row[1]
                    count = row[2]
                    summary[f'{severity}_count'] = count
                    summary['total_issues'] += count

            # Kalite skorlarını al
            cursor.execute("""
                SELECT completeness_score, accuracy_score, consistency_score, 
                       timeliness_score, overall_quality_score
                FROM sdg_data_quality_scores 
                WHERE company_id = ?
                ORDER BY validation_date DESC
                LIMIT 1
            """, (company_id,))

            quality_row = cursor.fetchone()
            if quality_row:
                summary['quality_scores'] = {
                    'completeness': quality_row[0],
                    'accuracy': quality_row[1],
                    'consistency': quality_row[2],
                    'timeliness': quality_row[3],
                    'overall': quality_row[4]
                }

            return summary

        except Exception as e:
            logging.error(f"Doğrulama özeti getirilirken hata: {e}")
            return {'error': str(e)}
        finally:
            conn.close()

    def fix_validation_issues(self, company_id: int, issue_ids: List[int]) -> Dict:
        """Doğrulama sorunlarını otomatik düzelt"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            fixed_count = 0
            failed_count = 0

            for issue_id in issue_ids:
                try:
                    # Sorun detaylarını al
                    cursor.execute("""
                        SELECT vr.rule_name, vr.suggested_fix, qr.id as response_id
                        FROM sdg_validation_results vr
                        JOIN sdg_question_responses qr ON vr.question_id = qr.question_id
                        WHERE vr.id = ? AND qr.company_id = ?
                    """, (issue_id, company_id))

                    result = cursor.fetchone()
                    if not result:
                        failed_count += 1
                        continue

                    rule_name, suggested_fix, response_id = result

                    # Otomatik düzeltme uygula
                    if rule_name == 'missing_data_check':
                        # Eksik veri için varsayılan değer
                        cursor.execute("""
                            UPDATE sdg_question_responses 
                            SET response_value = 'Veri girilmedi', response_text = 'Veri girilmedi'
                            WHERE id = ?
                        """, (response_id,))
                        fixed_count += 1

                    elif rule_name == 'percentage_range_check':
                        # Yüzde değerini sınırla
                        cursor.execute("""
                            UPDATE sdg_question_responses 
                            SET response_value = CASE 
                                WHEN CAST(response_value AS REAL) < 0 THEN '0'
                                WHEN CAST(response_value AS REAL) > 100 THEN '100'
                                ELSE response_value
                            END
                            WHERE id = ?
                        """, (response_id,))
                        fixed_count += 1

                    elif rule_name == 'text_length_check':
                        # Kısa metni uzat
                        cursor.execute("""
                            UPDATE sdg_question_responses 
                            SET response_text = response_text || ' [Detay eklendi]'
                            WHERE id = ? AND LENGTH(response_text) < 10
                        """, (response_id,))
                        fixed_count += 1

                    else:
                        # Diğer sorunlar için manuel düzeltme gerekli
                        failed_count += 1

                except Exception as e:
                    logging.error(f"Sorun {issue_id} düzeltilirken hata: {e}")
                    failed_count += 1

            conn.commit()

            return {
                'fixed_count': fixed_count,
                'failed_count': failed_count,
                'total_processed': len(issue_ids)
            }

        except Exception as e:
            logging.error(f"Sorunlar düzeltilirken hata: {e}")
            conn.rollback()
            return {'error': str(e)}
        finally:
            conn.close()

    def validate_responses(self, company_id: int, check_types: List[str]) -> Dict:
        """Soru cevaplarını doğrula"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            results = {}

            for check_type in check_types:
                if check_type == 'completeness':
                    # Eksik veri kontrolü
                    cursor.execute("""
                        SELECT g.code, i.code, qb.question_text
                        FROM sdg_question_bank qb
                        JOIN sdg_indicators i ON qb.indicator_id = i.id
                        JOIN sdg_targets t ON i.target_id = t.id
                        JOIN sdg_goals g ON t.goal_id = g.id
                        LEFT JOIN sdg_question_responses qr ON qb.id = qr.question_id AND qr.company_id = ?
                        WHERE qr.id IS NULL
                    """, (company_id,))

                    missing_data = cursor.fetchall()
                    results['completeness'] = [f"SDG {row[0]} - {row[1]}: {row[2]}" for row in missing_data]

                elif check_type == 'consistency':
                    # Tutarlılık kontrolü
                    cursor.execute("""
                        SELECT qr.id, g.code, i.code, qr.response_value
                        FROM sdg_question_responses qr
                        JOIN sdg_question_bank qb ON qr.question_id = qb.id
                        LEFT JOIN sdg_indicators i ON qb.indicator_id = i.id
                        LEFT JOIN sdg_targets t ON i.target_id = t.id
                        LEFT JOIN sdg_goals g ON t.goal_id = g.id
                        WHERE qr.company_id = ? AND (g.code IS NULL OR i.code IS NULL)
                    """, (company_id,))

                    consistency_issues = cursor.fetchall()
                    results['consistency'] = [f"Tutarsızlık: SDG {row[1]} - {row[2]}" for row in consistency_issues]

                elif check_type == 'format':
                    # Format kontrolü
                    cursor.execute("""
                        SELECT qr.id, g.code, i.code, qr.response_value, qt.type_name
                        FROM sdg_question_responses qr
                        JOIN sdg_question_bank qb ON qr.question_id = qb.id
                        JOIN sdg_indicators i ON qb.indicator_id = i.id
                        JOIN sdg_targets t ON i.target_id = t.id
                        JOIN sdg_goals g ON t.goal_id = g.id
                        JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                        WHERE qr.company_id = ? AND qr.response_value IS NOT NULL
                    """, (company_id,))

                    format_issues = []
                    for row in cursor.fetchall():
                        response_value = row[3]
                        question_type = row[4]

                        if question_type == 'Sayı' and not response_value.replace('.', '').replace('-', '').isdigit():
                            format_issues.append(f"SDG {row[1]} - {row[2]}: Geçersiz sayı formatı")
                        elif question_type == 'Yüzde' and (not response_value.replace('.', '').isdigit() or float(response_value) < 0 or float(response_value) > 100):
                            format_issues.append(f"SDG {row[1]} - {row[2]}: Geçersiz yüzde formatı")

                    results['format'] = format_issues

            conn.close()
            return results

        except Exception as e:
            logging.error(f"Doğrulama çalıştırılırken hata: {e}")
            return {}

    # NOTE: Duplicate and conflicting implementation removed.
    # The canonical public method is `calculate_quality_scores` defined earlier,
    # which returns overall metrics keys: completeness_score, accuracy_score,
    # consistency_score, timeliness_score, overall_quality_score.
    # For SDG-level breakdown, use `calculate_quality_scores_by_sdg`.

if __name__ == "__main__":
    # Test
    validation = SDGDataValidation()
    logging.info("SDG Veri Doğrulama Sistemi başlatıldı")

    # Test doğrulama
    results = validation.validate_company_data(1)
    logging.info(f"Doğrulama sonuçları: {results}")
