#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Survey Builder - Anket Oluşturma ve Yönetim Sistemi
"""

import logging
import json
import sqlite3
from typing import Dict, List, Optional


class SurveyBuilder:
    """Anket oluşturma ve yönetim sınıfı"""

    def __init__(self, db_path: str = None) -> None:
        import os
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self.create_tables()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Anket şablonları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'Genel',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Anket soruları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER,
                    question_text TEXT NOT NULL,
                    question_type TEXT DEFAULT 'text',
                    options TEXT, -- JSON format
                    weight REAL DEFAULT 1.0,
                    is_required INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES survey_templates(id)
                )
            """)

            # Kullanıcı anketleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    template_id INTEGER NOT NULL,
                    assigned_by INTEGER,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'assigned',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (template_id) REFERENCES survey_templates(id)
                )
            """)

            # Anket cevapları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_survey_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    response_value TEXT,
                    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_survey_id) REFERENCES user_surveys(id),
                    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
                )
            """)

            conn.commit()

            # Örnek veri oluştur - DEVRE DIŞI BIRAKILDI
            # self.create_sample_data()

        except Exception as e:
            logging.error(f"Survey tabloları oluşturulurken hata: {e}")
        finally:
            conn.close()

    def create_sample_data(self) -> None:
        """Örnek anket verisi oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Örnek anket şablonları
            sample_templates = [
                ("Sürdürülebilirlik Anketi", "SDG ve çevresel sürdürülebilirlik değerlendirmesi", "SDG"),
                ("İş Memnuniyeti Anketi", "Çalışan memnuniyeti ve motivasyon değerlendirmesi", "HR"),
                ("Kalite Anketi", "Ürün ve hizmet kalitesi değerlendirmesi", "Kalite"),
                ("Güvenlik Anketi", "İş güvenliği ve güvenlik kültürü değerlendirmesi", "Güvenlik"),
                ("Müşteri Memnuniyeti", "Müşteri deneyimi ve memnuniyet değerlendirmesi", "Müşteri")
            ]

            for name, desc, category in sample_templates:
                cursor.execute("""
                    INSERT OR IGNORE INTO survey_templates (name, description, category)
                    VALUES (?, ?, ?)
                """, (name, desc, category))

            # Örnek sorular
            template_id = 1  # Sürdürülebilirlik anketi

            sample_questions = [
                ("Şirketinizin çevresel sürdürülebilirlik hedefleri hakkında ne düşünüyorsunuz?", "scale", '{"min": 1, "max": 5, "labels": ["Çok Kötü", "Kötü", "Orta", "İyi", "Çok İyi"]}', 1.0, 1),
                ("Hangi SDG hedeflerinin öncelikli olduğunu düşünüyorsunuz?", "multiple_choice", '{"options": ["SDG 7 - Temiz Enerji", "SDG 13 - İklim Eylemi", "SDG 8 - İnsana Yakışır İş", "SDG 12 - Sorumlu Üretim"]}', 1.0, 1),
                ("Çevresel uygulamalarımızı nasıl değerlendiriyorsunuz?", "text", None, 0.8, 0),
                ("Sürdürülebilirlik eğitimleri yeterli mi?", "boolean", '{"options": ["Evet", "Hayır"]}', 0.6, 1),
                ("Hangi alanlarda iyileştirme yapılması gerektiğini düşünüyorsunuz?", "text", None, 0.9, 0)
            ]

            for question_text, question_type, options, weight, is_required in sample_questions:
                cursor.execute("""
                    INSERT OR IGNORE INTO survey_questions 
                    (template_id, question_text, question_type, options, weight, is_required)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (template_id, question_text, question_type, options, weight, is_required))

            # Örnek kullanıcı anketleri
            sample_user_surveys = [
                (1, 1, 1, "assigned"),  # user_id=1, template_id=1, assigned_by=1
                (1, 2, 1, "completed"), # user_id=1, template_id=2, assigned_by=1
                (1, 3, 1, "assigned"),  # user_id=1, template_id=3, assigned_by=1
            ]

            for user_id, template_id, assigned_by, status in sample_user_surveys:
                cursor.execute("""
                    INSERT OR IGNORE INTO user_surveys (user_id, template_id, assigned_by, status)
                    VALUES (?, ?, ?, ?)
                """, (user_id, template_id, assigned_by, status))

            conn.commit()

        except Exception as e:
            logging.error(f"Örnek anket verisi oluşturulurken hata: {e}")
        finally:
            conn.close()

    def get_user_surveys(self, user_id: int) -> List[Dict]:
        """Kullanıcının anketlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT us.id, st.name, st.description, st.category, us.status, us.assigned_at
                FROM user_surveys us
                JOIN survey_templates st ON us.template_id = st.id
                WHERE us.user_id = ?
                ORDER BY us.assigned_at DESC
            """, (user_id,))

            surveys = []
            for row in cursor.fetchall():
                surveys.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'category': row[3],
                    'status': row[4],
                    'assigned_at': row[5]
                })

            return surveys

        except Exception as e:
            logging.error(f"Kullanıcı anketleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_survey_questions(self, template_id: int) -> List[Dict]:
        """Anket sorularını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, question_text, question_type, options, weight, is_required
                FROM survey_questions
                WHERE template_id = ?
                ORDER BY id
            """, (template_id,))

            questions = []
            for row in cursor.fetchall():
                options = json.loads(row[3]) if row[3] else None
                questions.append({
                    'id': row[0],
                    'text': row[1],
                    'type': row[2],
                    'options': options,
                    'weight': row[4],
                    'required': bool(row[5])
                })

            return questions

        except Exception as e:
            logging.error(f"Anket soruları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_user_survey_detail(self, user_survey_id: int) -> Optional[Dict]:
        """user_surveys kaydı ve şablon bilgilerini getirir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT us.id, us.user_id, us.template_id, us.status, us.assigned_at, us.completed_at,
                       st.name, st.description, st.category
                FROM user_surveys us
                JOIN survey_templates st ON us.template_id = st.id
                WHERE us.id = ?
                """,
                (user_survey_id,)
            )

            row = cursor.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'user_id': row[1],
                'template_id': row[2],
                'status': row[3],
                'assigned_at': row[4],
                'completed_at': row[5],
                'template_name': row[6],
                'template_description': row[7],
                'template_category': row[8],
            }
        except Exception as e:
            logging.error(f"Kullanıcı anket detayı getirilirken hata: {e}")
            return None
        finally:
            conn.close()

    def get_existing_responses(self, user_survey_id: int) -> Dict[int, str]:
        """Önceden kaydedilmiş yanıtları sözlük olarak döndür (question_id -> response_value)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT question_id, response_value
                FROM survey_responses
                WHERE user_survey_id = ?
                """,
                (user_survey_id,)
            )
            responses = {}
            for qid, value in cursor.fetchall():
                responses[int(qid)] = value
            return responses
        except Exception as e:
            logging.error(f"Önceki anket cevapları getirilirken hata: {e}")
            return {}
        finally:
            conn.close()

    def submit_survey_response(self, user_survey_id: int, question_id: int, response_value: str) -> bool:
        """Anket cevabını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO survey_responses 
                (user_survey_id, question_id, response_value)
                VALUES (?, ?, ?)
            """, (user_survey_id, question_id, response_value))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Anket cevabı kaydedilirken hata: {e}")
            return False
        finally:
            conn.close()

    def complete_survey(self, user_survey_id: int) -> bool:
        """Anketi tamamlandı olarak işaretle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE user_surveys 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_survey_id,))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Anket tamamlanırken hata: {e}")
            return False
        finally:
            conn.close()
