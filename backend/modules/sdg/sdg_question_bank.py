import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Soru Bankası Sistemi
232 SDG göstergesi için soru bankası yönetimi
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from config.database import DB_PATH


class SDGQuestionBank:
    """SDG Soru Bankası Yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            # modules/sdg/sdg_question_bank.py -> modules/sdg -> modules -> root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path

        self._create_question_tables()

    # --- CRUD Yardımcıları ---
    def add_question(self, sdg_no: int, indicator_code: str, question_text: str,
                     question_type: str = 'text', category_id: Optional[int] = None,
                     is_required: bool = True, difficulty_level: str = 'medium',
                     validation_rules: Optional[str] = None, help_text: Optional[str] = None,
                     options: Optional[str] = None, correct_answer: Optional[str] = None,
                     points: int = 1) -> Optional[int]:
        """Yeni soru ekle ve soru ID'sini döndür"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Soru tipi ID'sini bul/oluştur
            cursor.execute("SELECT id FROM sdg_question_types WHERE type_name = ?", (self._map_type_name(question_type),))
            row = cursor.fetchone()
            if row:
                qtype_id = row[0]
            else:
                cursor.execute("INSERT INTO sdg_question_types (type_name, description, input_type) VALUES (?, ?, ?)",
                               (self._map_type_name(question_type), 'Otomatik eklendi', self._map_input_type(question_type)))
                qtype_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO sdg_question_bank (
                    sdg_no, indicator_code, question_text, question_type_id, category_id,
                    difficulty_level, is_required, validation_rules, help_text,
                    options, correct_answer, points
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (sdg_no, indicator_code, question_text, qtype_id, category_id,
                 difficulty_level, 1 if is_required else 0, validation_rules, help_text,
                 options, correct_answer, points)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Soru eklenirken hata: {e}")
            return None
        finally:
            conn.close()

    def update_question(self, question_id: int, **kwargs) -> bool:
        """Mevcut soruyu güncelle"""
        allowed = {
            'sdg_no', 'indicator_code', 'question_text', 'question_type', 'category_id',
            'difficulty_level', 'is_required', 'validation_rules', 'help_text',
            'options', 'correct_answer', 'points'
        }
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # question_type özel işleme
            if 'question_type' in fields:
                qt = fields.pop('question_type')
                cursor.execute("SELECT id FROM sdg_question_types WHERE type_name = ?", (self._map_type_name(qt),))
                row = cursor.fetchone()
                if row:
                    fields['question_type_id'] = row[0]
                else:
                    cursor.execute("INSERT INTO sdg_question_types (type_name, description, input_type) VALUES (?, ?, ?)",
                                   (self._map_type_name(qt), 'Otomatik eklendi', self._map_input_type(qt)))
                    fields['question_type_id'] = cursor.lastrowid

            cursor.execute("PRAGMA table_info(sdg_question_bank)")
            cols = [c[1] for c in cursor.fetchall()]
            safe_keys = [k for k in fields.keys() if k in cols and k.isidentifier()]
            set_clause = ", ".join([k + " = ?" for k in safe_keys])
            params = [fields[k] for k in safe_keys] + [question_id]
            cursor.execute(
                "UPDATE sdg_question_bank SET " + set_clause + ", updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                params,
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Soru güncellenirken hata: {e}")
            return False
        finally:
            conn.close()

    def delete_question(self, question_id: int) -> bool:
        """Soruyu sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sdg_question_bank WHERE id = ?", (question_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Soru silinirken hata: {e}")
            return False
        finally:
            conn.close()

    def _map_type_name(self, question_type: str) -> str:
        mapping = {
            'text': 'Metin',
            'numeric': 'Sayı',
            'boolean': 'Evet/Hayır'
        }
        return mapping.get(question_type, 'Metin')

    def _map_input_type(self, question_type: str) -> str:
        mapping = {
            'text': 'text',
            'numeric': 'number',
            'boolean': 'checkbox'
        }
        return mapping.get(question_type, 'text')

    def _create_question_tables(self) -> None:
        """Soru bankası tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SDG soru kategorileri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # SDG soru tipleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL UNIQUE,
                description TEXT,
                input_type TEXT NOT NULL,
                validation_rules TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Eski şemaları uyumlu hale getir: validation_rules sütunu eksikse ekle
        try:
            cursor.execute("PRAGMA table_info(sdg_question_types)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'validation_rules' not in cols:
                cursor.execute("ALTER TABLE sdg_question_types ADD COLUMN validation_rules TEXT")
        except Exception as e:
            # ALTER başarısız olursa sessizce devam et; tablo yeni ise zaten mevcut
            logging.error(f"Silent error caught: {str(e)}")

        # SDG soru bankası
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_question_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type_id INTEGER NOT NULL,
                category_id INTEGER,
                difficulty_level TEXT DEFAULT 'medium',
                is_required BOOLEAN DEFAULT 1,
                validation_rules TEXT,
                help_text TEXT,
                options TEXT,
                correct_answer TEXT,
                points INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_type_id) REFERENCES sdg_question_types(id),
                FOREIGN KEY (category_id) REFERENCES sdg_question_categories(id)
            )
        """)

        # Eski şemalar için eksik sütunları ekle (migrasyon)
        try:
            cursor.execute("PRAGMA table_info(sdg_question_bank)")
            cols = [row[1] for row in cursor.fetchall()]
            # Eksik kolonları tek tek ekle
            if 'validation_rules' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN validation_rules TEXT")
            if 'help_text' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN help_text TEXT")
            if 'options' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN options TEXT")
            if 'correct_answer' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN correct_answer TEXT")
            if 'points' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN points INTEGER DEFAULT 1")
            if 'updated_at' not in cols:
                cursor.execute("ALTER TABLE sdg_question_bank ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
        except Exception as e:
            # ALTER başarısız olabilir; tablo yeni ise zaten tam şema var
            logging.error(f"Silent error caught: {str(e)}")

        # SDG soru cevapları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_bank_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                response_text TEXT,
                response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                is_validated BOOLEAN DEFAULT 0,
                validation_notes TEXT,
                FOREIGN KEY (question_id) REFERENCES sdg_question_bank(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Varsayılan verileri ekle
        self._insert_default_data(cursor)

        conn.commit()
        conn.close()
        logging.info("SDG soru bankası tabloları oluşturuldu")

    def _insert_default_data(self, cursor) -> None:
        """Varsayılan verileri ekle"""
        # Soru kategorileri
        categories = [
            ('Genel Bilgi', 'Genel SDG bilgileri ve temel sorular'),
            ('Veri Toplama', 'Veri toplama süreçleri ve metodolojileri'),
            ('Performans', 'Performans göstergeleri ve metrikleri'),
            ('Raporlama', 'Raporlama süreçleri ve standartları'),
            ('İyileştirme', 'İyileştirme önerileri ve aksiyon planları')
        ]

        for category_name, description in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO sdg_question_categories (category_name, description)
                VALUES (?, ?)
            """, (category_name, description))

        # Soru tipleri
        question_types = [
            ('Metin', 'Açık uçlu metin sorusu', 'text', '{"min_length": 10, "max_length": 1000}'),
            ('Sayı', 'Sayısal değer sorusu', 'number', '{"min": 0, "max": 1000000}'),
            ('Evet/Hayır', 'Evet/Hayır sorusu', 'boolean', '{}'),
            ('Çoktan Seçmeli', 'Çoktan seçmeli sorusu', 'select', '{"options": []}'),
            ('Tarih', 'Tarih sorusu', 'date', '{"format": "YYYY-MM-DD"}'),
            ('Yüzde', 'Yüzde değeri sorusu', 'percentage', '{"min": 0, "max": 100}'),
            ('Para Birimi', 'Para birimi sorusu', 'currency', '{"currency": "TRY"}'),
            ('Derecelendirme', '1-5 arası derecelendirme', 'rating', '{"min": 1, "max": 5}')
        ]

        for type_name, description, input_type, validation_rules in question_types:
            cursor.execute("""
                INSERT OR IGNORE INTO sdg_question_types (type_name, description, input_type, validation_rules)
                VALUES (?, ?, ?, ?)
            """, (type_name, description, input_type, validation_rules))

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_questions_for_indicator(self, sdg_no: int, indicator_code: str, indicator_title: str) -> List[int]:
        """Gösterge için 3 soru oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Soru tiplerini al
            cursor.execute("SELECT id, type_name, input_type FROM sdg_question_types")
            question_types: Dict[str, Tuple[int, str]] = {row[1]: (row[0], row[2]) for row in cursor.fetchall()}

            # Kategori ID'sini al
            cursor.execute("SELECT id FROM sdg_question_categories WHERE category_name = 'Veri Toplama'")
            category_id = cursor.fetchone()[0]

            # 3 soru oluştur
            questions: List[Dict[str, Any]] = [
                {
                    'question_text': f"SDG {sdg_no} - {indicator_code} göstergesi için mevcut durumunuz nedir?",
                    'type_name': 'Derecelendirme',
                    'help_text': f"{indicator_title} göstergesi için mevcut durumunuzu 1-5 arası değerlendirin",
                    'options': '{"1": "Çok Zayıf", "2": "Zayıf", "3": "Orta", "4": "İyi", "5": "Mükemmel"}',
                    'is_required': 1
                },
                {
                    'question_text': f"SDG {sdg_no} - {indicator_code} göstergesi için hangi veri kaynaklarını kullanıyorsunuz?",
                    'type_name': 'Metin',
                    'help_text': f"{indicator_title} göstergesi için kullandığınız veri kaynaklarını detaylı olarak açıklayın",
                    'options': None,
                    'is_required': 1
                },
                {
                    'question_text': f"SDG {sdg_no} - {indicator_code} göstergesi için hedefiniz nedir?",
                    'type_name': 'Yüzde',
                    'help_text': f"{indicator_title} göstergesi için ulaşmayı hedeflediğiniz yüzde değeri",
                    'options': None,
                    'is_required': 1
                }
            ]

            question_ids: List[int] = []

            for i, question in enumerate(questions, 1):
                question_type_id = question_types[question['type_name']][0]

                cursor.execute("""
                    INSERT INTO sdg_question_bank 
                    (sdg_no, indicator_code, question_text, question_type_id, category_id, 
                     difficulty_level, is_required, help_text, options, points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sdg_no, indicator_code, question['question_text'], question_type_id, category_id,
                    'medium', question['is_required'], question['help_text'], question['options'], 1
                ))

                qid = cursor.lastrowid or 0
                question_ids.append(int(qid))

                logging.info(f"SDG {sdg_no} - {indicator_code} için soru {i} oluşturuldu (ID: {int(qid)})")

            conn.commit()
            return question_ids

        except Exception as e:
            logging.error(f"Soru oluşturulurken hata: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()

    def create_all_questions(self) -> Dict[str, Any]:
        """Tüm SDG göstergeleri için sorular oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Tüm SDG göstergelerini al
            cursor.execute("""
                SELECT sg.code as sdg_no, si.code as indicator_code, si.title_tr as indicator_title
                FROM sdg_indicators si
                JOIN sdg_targets st ON si.target_id = st.id
                JOIN sdg_goals sg ON st.goal_id = sg.id
                ORDER BY sg.code, si.code
            """)

            indicators = cursor.fetchall()

            stats: Dict[str, Any] = {
                'total_indicators': len(indicators),
                'questions_created': 0,
                'errors': 0,
                'sdg_stats': {}
            }

            for sdg_no, indicator_code, indicator_title in indicators:
                try:
                    # Bu gösterge için soru var mı kontrol et
                    cursor.execute("""
                        SELECT COUNT(*) FROM sdg_question_bank 
                        WHERE sdg_no = ? AND indicator_code = ?
                    """, (sdg_no, indicator_code))

                    if cursor.fetchone()[0] > 0:
                        logging.info(f"SDG {sdg_no} - {indicator_code} için sorular zaten mevcut")
                        continue

                    # Soruları oluştur
                    question_ids = self.create_questions_for_indicator(sdg_no, indicator_code, indicator_title)

                    if question_ids:
                        stats['questions_created'] += len(question_ids)

                        if sdg_no not in stats['sdg_stats']:
                            stats['sdg_stats'][sdg_no] = 0
                        stats['sdg_stats'][sdg_no] += len(question_ids)
                    else:
                        stats['errors'] += 1

                except Exception as e:
                    logging.error(f"SDG {sdg_no} - {indicator_code} için soru oluşturulurken hata: {e}")
                    stats['errors'] += 1

            conn.commit()
            return stats

        except Exception as e:
            logging.error(f"Tüm sorular oluşturulurken hata: {e}")
            return {'error': str(e)}
        finally:
            conn.close()

    def get_questions_for_indicator(self, sdg_no: int, indicator_code: str) -> List[Dict]:
        """Gösterge için soruları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT qb.id, qb.question_text, qb.help_text, qb.options, qb.is_required,
                       qb.difficulty_level, qb.points, qt.type_name, qt.input_type, qt.validation_rules
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                WHERE qb.sdg_no = ? AND qb.indicator_code = ?
                ORDER BY qb.id
            """, (sdg_no, indicator_code))

            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row[0],
                    'question_text': row[1],
                    'help_text': row[2],
                    'options': row[3],
                    'is_required': bool(row[4]),
                    'difficulty_level': row[5],
                    'points': row[6],
                    'type_name': row[7],
                    'input_type': row[8],
                    'validation_rules': row[9]
                })

            return questions

        except Exception as e:
            logging.error(f"Sorular getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_questions_for_sdg(self, sdg_no: int) -> List[Dict]:
        """SDG için tüm soruları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT qb.id, qb.indicator_code, qb.question_text, qb.help_text, qb.options, 
                       qb.is_required, qb.difficulty_level, qb.points, qt.type_name, qt.input_type
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                WHERE qb.sdg_no = ?
                ORDER BY qb.indicator_code, qb.id
            """, (sdg_no,))

            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row[0],
                    'indicator_code': row[1],
                    'question_text': row[2],
                    'help_text': row[3],
                    'options': row[4],
                    'is_required': bool(row[5]),
                    'difficulty_level': row[6],
                    'points': row[7],
                    'type_name': row[8],
                    'input_type': row[9]
                })

            return questions

        except Exception as e:
            logging.error(f"SDG soruları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def save_response(self, company_id: int, question_id: int, response_value: str, response_text: Optional[str] = None) -> bool:
        """Soru cevabını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Mevcut cevabı güncelle veya yeni ekle
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_question_responses 
                (company_id, question_id, response_value, response_text, response_date)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, question_id, response_value, response_text, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Cevap kaydedilirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_responses_for_company(self, company_id: int, sdg_no: Optional[int] = None) -> List[Dict]:
        """Şirket için cevapları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if sdg_no:
                cursor.execute("""
                    SELECT qr.id, qr.question_id, qr.response_value, qr.response_text, 
                           qr.response_date, qr.is_validated, qb.indicator_code, qb.question_text
                    FROM sdg_question_responses qr
                    JOIN sdg_question_bank qb ON qr.question_id = qb.id
                    WHERE qr.company_id = ? AND qb.sdg_no = ?
                    ORDER BY qb.indicator_code, qr.response_date
                """, (company_id, sdg_no))
            else:
                cursor.execute("""
                    SELECT qr.id, qr.question_id, qr.response_value, qr.response_text, 
                           qr.response_date, qr.is_validated, qb.indicator_code, qb.question_text, qb.sdg_no
                    FROM sdg_question_responses qr
                    JOIN sdg_question_bank qb ON qr.question_id = qb.id
                    WHERE qr.company_id = ?
                    ORDER BY qb.sdg_no, qb.indicator_code, qr.response_date
                """, (company_id,))

            responses = []
            for row in cursor.fetchall():
                responses.append({
                    'id': row[0],
                    'question_id': row[1],
                    'response_value': row[2],
                    'response_text': row[3],
                    'response_date': row[4],
                    'is_validated': bool(row[5]),
                    'indicator_code': row[6],
                    'question_text': row[7],
                    'sdg_no': row[8] if len(row) > 8 else None
                })

            return responses

        except Exception as e:
            logging.error(f"Cevaplar getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_question_statistics(self, company_id: int) -> Dict:
        """Soru istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

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

            # SDG bazında istatistikler
            cursor.execute("""
                SELECT qb.sdg_no, COUNT(DISTINCT qb.id) as total, 
                       COUNT(DISTINCT qr.question_id) as answered
                FROM sdg_question_bank qb
                LEFT JOIN sdg_question_responses qr ON qb.id = qr.question_id AND qr.company_id = ?
                GROUP BY qb.sdg_no
                ORDER BY qb.sdg_no
            """, (company_id,))

            sdg_stats = {}
            for row in cursor.fetchall():
                sdg_stats[row[0]] = {
                    'total': row[1],
                    'answered': row[2],
                    'percentage': round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2)
                }

            return {
                'total_questions': total_questions,
                'answered_questions': answered_questions,
                'completion_percentage': round((answered_questions / total_questions * 100) if total_questions > 0 else 0, 2),
                'sdg_stats': sdg_stats
            }

        except Exception as e:
            logging.error(f"İstatistikler getirilirken hata: {e}")
            return {
                'total_questions': 0,
                'answered_questions': 0,
                'completion_percentage': 0,
                'sdg_stats': {}
            }
        finally:
            conn.close()

    def get_sdg_goals(self) -> List[Tuple]:
        """SDG hedeflerini getir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT code, title_tr FROM sdg_goals ORDER BY code")
            goals = cursor.fetchall()

            conn.close()
            return goals

        except Exception as e:
            logging.error(f"SDG hedefleri getirilirken hata: {e}")
            return []

    def get_questions_for_sdg_brief(self, sdg_no: int) -> List[Dict]:
        """Belirli SDG'ye ait soruları getir (özet alanlarla)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT qb.id, qb.sdg_no, qb.indicator_code, qb.question_text, qb.created_at,
                       qt.type_name, qt.input_type
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                WHERE qb.sdg_no = ?
                ORDER BY qb.indicator_code, qb.id
                """,
                (sdg_no,)
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'sdg_no': row[1],
                    'indicator_code': row[2],
                    'question_text': row[3],
                    'created_at': row[4],
                    'type_name': row[5],
                    'input_type': row[6],
                })

            conn.close()
            return results
        except Exception as e:
            logging.error(f"SDG soruları getirilirken hata: {e}")
            return []

    def get_all_questions(self) -> List[Dict]:
        """Tüm SDG'lere ait soruları getir (tip bilgisiyle birlikte)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT qb.id, qb.sdg_no, qb.indicator_code, qb.question_text, qb.created_at,
                       qt.type_name, qt.input_type
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                ORDER BY qb.sdg_no, qb.indicator_code, qb.id
                """
            )

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'sdg_no': row[1],
                    'indicator_code': row[2],
                    'question_text': row[3],
                    'created_at': row[4],
                    'type_name': row[5],
                    'input_type': row[6],
                })

            conn.close()
            return results
        except Exception as e:
            logging.error(f"Tüm sorular getirilirken hata: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Soru bankası istatistiklerini getir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Toplam SDG hedefi
            cursor.execute("SELECT COUNT(*) FROM sdg_goals")
            total_sdg_goals = cursor.fetchone()[0]

            # Toplam soru
            cursor.execute("SELECT COUNT(*) FROM sdg_question_bank")
            total_questions = cursor.fetchone()[0]

            # Soru türlerine göre dağılım
            cursor.execute("""
                SELECT qt.type_name, COUNT(*) 
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                GROUP BY qt.type_name
            """)
            type_counts = dict(cursor.fetchall())

            # Ortalama soru/HDG
            avg_questions_per_sdg = total_questions / total_sdg_goals if total_sdg_goals > 0 else 0

            conn.close()

            return {
                'total_sdg_goals': total_sdg_goals,
                'total_questions': total_questions,
                'text_questions': type_counts.get('Metin', 0),
                'numeric_questions': type_counts.get('Sayı', 0),
                'boolean_questions': type_counts.get('Evet/Hayır', 0),
                'avg_questions_per_sdg': avg_questions_per_sdg
            }

        except Exception as e:
            logging.error(f"İstatistikler getirilirken hata: {e}")
            return {}

    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Tek bir sorunun detayını getir"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT qb.id, qb.sdg_no, qb.indicator_code, qb.question_text, qb.help_text,
                       qb.options, qb.is_required, qb.difficulty_level, qb.points,
                       qt.type_name, qt.input_type
                FROM sdg_question_bank qb
                JOIN sdg_question_types qt ON qb.question_type_id = qt.id
                WHERE qb.id = ?
                """,
                (question_id,)
            )

            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            return {
                'id': row[0],
                'sdg_no': row[1],
                'indicator_code': row[2],
                'question_text': row[3],
                'help_text': row[4],
                'options': row[5],
                'is_required': bool(row[6]),
                'difficulty_level': row[7],
                'points': row[8],
                'type_name': row[9],
                'input_type': row[10],
            }
        except Exception as e:
            logging.error(f"Soru detayları getirilirken hata: {e}")
            return None

if __name__ == "__main__":
    # Test
    question_bank = SDGQuestionBank()
    logging.info("SDG Soru Bankası başlatıldı")

    # Tüm soruları oluştur
    stats = question_bank.create_all_questions()
    logging.info(f"Soru oluşturma istatistikleri: {stats}")
