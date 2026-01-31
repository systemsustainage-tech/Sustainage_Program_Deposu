import logging
import csv
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from config.settings import ensure_directories, get_db_path


class PrioritizationManager:
    """Önceliklendirme modülü yöneticisi - Materyal konu analizi ve anket sistemi"""

    def __init__(self, db_path: str | None = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            ensure_directories()
            self.db_path = get_db_path()
        self.create_tables()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS materiality_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    sdg_mapping TEXT,
                    priority_score REAL DEFAULT 0,
                    stakeholder_impact REAL DEFAULT 0,
                    business_impact REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
                """
            )
            # Anket şablonları tablosu
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

            # Anket soruları tablosu (Şablonlar için)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_template_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    category TEXT,
                    sdg_mapping TEXT,
                    options TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(template_id) REFERENCES survey_templates(id) ON DELETE CASCADE
                )
            """)

            # Stakeholder anketleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_name TEXT NOT NULL,
                    stakeholder_category TEXT NOT NULL,
                    survey_data TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # Materyal konu değerlendirmeleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materiality_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_name TEXT NOT NULL,
                    stakeholder_category TEXT NOT NULL,
                    assessment_data TEXT,
                    priority_scores TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Anket cevapları tablosu (şirket bazlı)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    response_value TEXT,
                    score REAL DEFAULT 0,
                    response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
                )
            """)

            # Önceliklendirme sonuçları tablosu (kategori bazlı)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prioritization_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    total_score REAL NOT NULL,
                    priority_level TEXT NOT NULL,
                    calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            logging.info("[OK] Prioritization tabloları oluşturuldu ve senkronize edildi")

            # Varsayılan anket şablonu oluştur
            self.create_default_survey_template()

        except Exception as e:
            logging.error(f"[HATA] Prioritization tablolari olusturulamadi: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {
            'total_topics': 0,
            'high_priority_topics': 0,
            'completed_assessments': 0,
            'pending_surveys': 0
        }
        try:
            cursor.execute("SELECT COUNT(*) FROM materiality_topics WHERE company_id = ?", (company_id,))
            stats['total_topics'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM materiality_topics WHERE company_id = ? AND priority_score >= 3.0", (company_id,))
            stats['high_priority_topics'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM materiality_assessments WHERE company_id = ?", (company_id,))
            stats['completed_assessments'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM stakeholder_surveys WHERE company_id = ? AND status != 'completed'", (company_id,))
            stats['pending_surveys'] = cursor.fetchone()[0] or 0
            
            return stats
        except Exception as e:
            logging.error(f"Önceliklendirme istatistikleri getirme hatası: {e}")
            return stats
        finally:
            conn.close()

    def save_materiality_topic(
        self,
        company_id: int,
        topic_name: str,
        stakeholder_impact: float,
        business_impact: float,
        priority_score: float,
        category: str = "Genel",
        description: str = None,
        sdg_mapping: str = None,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO materiality_topics (
                    company_id, topic_name, category, description,
                    sdg_mapping, priority_score, stakeholder_impact, business_impact
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    topic_name,
                    category,
                    description,
                    sdg_mapping,
                    priority_score,
                    stakeholder_impact,
                    business_impact,
                ),
            )
            topic_id = cursor.lastrowid
            conn.commit()
            return topic_id
        except Exception as e:
            logging.error(f"Materyal konu kaydetme hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_materiality_topics(self, company_id: int) -> List[Dict]:
        """Materyal konuları getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM materiality_topics 
                WHERE company_id = ? 
                ORDER BY priority_score DESC, created_at DESC
            """, (company_id,))
            
            topics = [dict(row) for row in cursor.fetchall()]
            return topics
        except Exception as e:
            logging.error(f"Materyal konu listeleme hatası: {e}")
            return []
        finally:
            conn.close()

    def create_default_survey_template(self) -> None:
        """Varsayılan anket şablonu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if template exists
            cursor.execute("SELECT id FROM survey_templates WHERE name = ?", ("Genel Sürdürülebilirlik Anketi",))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO survey_templates (name, description, category)
                    VALUES (?, ?, ?)
                """, ("Genel Sürdürülebilirlik Anketi", "Şirket genel sürdürülebilirlik durumunu ölçmek için standart anket.", "Genel"))
                
                template_id = cursor.lastrowid
                
                # Add default questions
                questions = [
                    ("Şirketinizin karbon ayak izi ölçümü yapılıyor mu?", "yes_no", "Çevre", "13"),
                    ("Çalışan memnuniyeti anketi düzenli olarak yapılıyor mu?", "yes_no", "Sosyal", "8"),
                    ("Yönetim kurulunda sürdürülebilirlik temsilcisi var mı?", "yes_no", "Yönetişim", "16"),
                    ("Atık yönetimi politikanız var mı?", "yes_no", "Çevre", "12"),
                    ("Tedarikçi denetimi yapıyor musunuz?", "yes_no", "Yönetişim", "12")
                ]
                
                for q in questions:
                    cursor.execute("""
                        INSERT INTO survey_template_questions (template_id, question_text, question_type, category, sdg_mapping)
                        VALUES (?, ?, ?, ?, ?)
                    """, (template_id, q[0], q[1], q[2], q[3]))
                
                conn.commit()
                logging.info("Varsayılan anket şablonu oluşturuldu.")
                
        except Exception as e:
            logging.error(f"Varsayılan anket şablonu oluşturma hatası: {e}")
        finally:
            conn.close()

    def populate_default_topics(self) -> None:
        """Eğer hiç konu yoksa varsayılan materyal konuları ekle (GRI/ESRS bazlı)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Check if any topic exists for default company (id=1)
            cursor.execute("SELECT COUNT(*) FROM materiality_topics WHERE company_id = 1")
            count = cursor.fetchone()[0]
            
            if count == 0:
                default_topics = [
                    ("İklim Değişikliği Azaltımı", "Çevre", "Sera gazı emisyonlarının azaltılması ve enerji verimliliği", "13", 4.5, 4.8),
                    ("İklim Değişikliğine Uyum", "Çevre", "Fiziksel iklim risklerine karşı dayanıklılık", "13", 4.0, 4.2),
                    ("Su ve Atıksu Yönetimi", "Çevre", "Su tüketimi ve atıksu arıtma süreçleri", "6", 3.8, 4.0),
                    ("Döngüsel Ekonomi ve Atık", "Çevre", "Atık azaltımı, geri dönüşüm ve kaynak verimliliği", "12", 4.2, 3.5),
                    ("Biyoçeşitlilik", "Çevre", "Doğal yaşam alanlarının korunması", "15", 3.0, 3.2),
                    ("Çalışan Sağlığı ve Güvenliği", "Sosyal", "İş kazalarının önlenmesi ve çalışan refahı", "3", 4.8, 4.5),
                    ("Çeşitlilik ve Kapsayıcılık", "Sosyal", "Fırsat eşitliği ve ayrımcılıkla mücadele", "5", 3.5, 3.8),
                    ("Tedarik Zinciri Yönetimi", "Yönetişim", "Tedarikçilerin çevresel ve sosyal denetimi", "12", 4.0, 4.1),
                    ("İş Etiği ve Yolsuzlukla Mücadele", "Yönetişim", "Rüşvet ve yolsuzluk karşıtı politikalar", "16", 4.9, 4.9),
                    ("Veri Gizliliği ve Siber Güvenlik", "Yönetişim", "Müşteri ve çalışan verilerinin korunması", "9", 4.3, 4.6)
                ]
                
                for topic in default_topics:
                    # Calculate priority score (average of impact and business)
                    priority = (topic[4] + topic[5]) / 2.0
                    cursor.execute("""
                        INSERT INTO materiality_topics 
                        (company_id, topic_name, category, description, sdg_mapping, stakeholder_impact, business_impact, priority_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (1, topic[0], topic[1], topic[2], topic[3], topic[4], topic[5], priority))
                
                conn.commit()
                logging.info("Varsayılan materyal konular eklendi.")
        except Exception as e:
            logging.error(f"Varsayılan konu ekleme hatası: {e}")
        finally:
            conn.close()

    def create_survey_template(self, name: str, description: str, category: str = "Genel") -> int:
        """Yeni anket şablonu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO survey_templates (name, description, category, is_active)
                VALUES (?, ?, ?, ?)
            """, (name, description, category, 1))

            template_id = cursor.lastrowid
            conn.commit()
            return template_id

        except Exception as e:
            logging.error(f"Anket şablonu oluşturma hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def add_survey_question(self, template_id: int, question_text: str,
                           question_type: str, weight: float, category: str,
                           sdg_mapping: str = None) -> int:
        """Anket sorusu ekle (Şablona)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO survey_template_questions 
                (template_id, question_text, question_type, weight, category, sdg_mapping)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (template_id, question_text, question_type, weight, category, sdg_mapping))

            question_id = cursor.lastrowid
            conn.commit()
            return question_id

        except Exception as e:
            logging.error(f"Soru ekleme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_survey_templates(self, company_id: int = None) -> List[Dict]:
        """Tüm anket şablonlarını getir"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            sql = """
                SELECT t.id, t.name, t.description, t.category, t.created_at, t.is_active,
                       count(q.id) as question_count
                FROM survey_templates t
                LEFT JOIN survey_template_questions q ON t.id = q.template_id
                WHERE t.is_active = 1
            """
            params = []
            
            if company_id is not None:
                sql += " AND (t.company_id = ? OR t.company_id IS NULL)"
                params.append(company_id)
            
            sql += """
                GROUP BY t.id
                ORDER BY t.created_at DESC
            """
            
            cursor.execute(sql, params)

            templates = [dict(row) for row in cursor.fetchall()]
            return templates
        except Exception as e:
            logging.error(f"Şablon listeleme hatası: {e}")
            return []
        finally:
            conn.close()

    def delete_survey_template(self, template_id: int) -> bool:
        """Anket şablonunu sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Önce soruları sil (cascade)
            cursor.execute("DELETE FROM survey_questions WHERE template_id = ?", (template_id,))

            # Sonra şablonu sil
            cursor.execute("DELETE FROM survey_templates WHERE id = ?", (template_id,))

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Anket şablonu silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_survey_question(self, question_id: int) -> bool:
        """Tek bir anket sorusunu sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM survey_questions WHERE id = ?", (question_id,))
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Anket sorusu silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_survey_questions(self, template_id: int) -> List[Dict]:
        """Anket sorularını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, question_text, question_type, weight, category, sdg_mapping
            FROM survey_questions
            WHERE template_id = ?
            ORDER BY id
        """, (template_id,))

        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'question_text': row[1],
                'question_type': row[2],
                'weight': row[3],
                'category': row[4],
                'sdg_mapping': row[5]
            })

        conn.close()
        return questions

    def update_survey_question(self, question_id: int, question_text: str = None,
                               question_type: str = None, weight: float = None,
                               category: str = None, sdg_mapping: str = None,
                               options: str = None) -> bool:
        """Mevcut anket sorusunu güncelle (verilen alanlar)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        if question_text is not None:
            fields.append("question_text = ?")
            values.append(question_text)
        if question_type is not None:
            fields.append("question_type = ?")
            values.append(question_type)
        if weight is not None:
            fields.append("weight = ?")
            values.append(weight)
        if category is not None:
            fields.append("category = ?")
            values.append(category)
        if sdg_mapping is not None:
            fields.append("sdg_mapping = ?")
            values.append(sdg_mapping)
        if options is not None:
            fields.append("options = ?")
            values.append(options)

        if not fields:
            conn.close()
            return False

        values.append(question_id)
        try:
            cursor.execute(f"UPDATE survey_questions SET {', '.join(fields)} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Soru güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def populate_standard_questions(self, template_id: int, framework: str,
                                    csv_path: str = None) -> int:
        """
        sdg_232_questions.csv dosyasından framework (SDG/GRI/TSRS) için
        standart soruları içe aktar ve belirtilen şablona ekle.
        Dönen değer: eklenen soru sayısı.
        """
        if csv_path is None:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'sdg_232_questions.csv')
            # Fallback: kök klasörde ise
            if not os.path.exists(csv_path):
                csv_path = 'c:/SDG/sdg_232_questions.csv'

        added = 0
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Soruları topla (Soru 1-3)
                    question_cols = ['Soru 1', 'Soru 2', 'Soru 3']
                    for qc in question_cols:
                        qtext = (row.get(qc) or '').strip()
                        if not qtext:
                            continue

                        sdg_no = (row.get('SDG No') or '').strip()
                        sdg_title = (row.get('SDG Başlık') or '').strip()
                        alt_hedef = (row.get('Alt Hedef Kodu') or '').strip()
                        gosterge = (row.get('Gösterge Kodu') or '').strip()
                        gri_map = (row.get('GRI Bağlantısı') or '').strip()
                        tsrs_map = (row.get('TSRS Bağlantısı') or '').strip()

                        mapping_parts = []
                        if sdg_no or sdg_title:
                            mapping_parts.append(f"SDG {sdg_no} {sdg_title}".strip())
                        if alt_hedef:
                            mapping_parts.append(f"Alt Hedef: {alt_hedef}")
                        if gosterge:
                            mapping_parts.append(f"Gösterge: {gosterge}")
                        if gri_map:
                            mapping_parts.append(f"GRI: {gri_map}")
                        if tsrs_map:
                            mapping_parts.append(f"TSRS: {tsrs_map}")
                        sdg_mapping = ' | '.join(mapping_parts)

                        # Kategori belirleme: framework veya SDG başlığı
                        if framework.upper() == 'SDG':
                            category = sdg_title or 'SDG'
                        elif framework.upper() == 'GRI':
                            category = 'GRI'
                        elif framework.upper() == 'TSRS':
                            category = 'TSRS'
                        else:
                            category = 'Genel'

                        # Varsayılan tip: ölçek (1-5)
                        qtype = 'scale'
                        weight = 1.0

                        if self.add_survey_question(template_id, qtext, qtype, weight, category, sdg_mapping):
                            added += 1
        except Exception as e:
            logging.error(f"Standart sorular içe aktarma hatası: {e}")
            return 0

        return added

    def save_survey_response(self, company_id: int, question_id: int,
                           response_value: str, score: float) -> bool:
        """Anket cevabını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO survey_responses 
                (company_id, question_id, response_value, score, response_date)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, question_id, response_value, score, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Cevap kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def calculate_priority_scores(self, company_id: int, template_id: int) -> Dict:
        """Öncelik skorlarını hesapla"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Anket cevaplarını ve soruları getir (sr.survey_id yerine template_id üzerinden bağla)
        cursor.execute("""
            SELECT sr.question_id, sr.response_value, sr.score, 
                   sq.question_text, sq.weight, sq.category, sq.sdg_mapping
            FROM survey_responses sr
            JOIN survey_questions sq ON sr.question_id = sq.id
            WHERE sq.template_id = ? AND sr.company_id = ?
        """, (template_id, company_id))

        responses = cursor.fetchall()

        # Kategori bazında skorları hesapla
        category_scores = {}
        total_score = 0
        max_possible_score = 0

        for response in responses:
            question_id, response_value, score, question_text, weight, category, sdg_mapping = response

            if category not in category_scores:
                category_scores[category] = {
                    'total_score': 0,
                    'max_score': 0,
                    'question_count': 0,
                    'questions': []
                }

            category_scores[category]['total_score'] += score * weight
            category_scores[category]['max_score'] += 5 * weight  # Maksimum 5 puan
            category_scores[category]['question_count'] += 1
            category_scores[category]['questions'].append({
                'question_text': question_text,
                'response_value': response_value,
                'score': score,
                'weight': weight
            })

            total_score += score * weight
            max_possible_score += 5 * weight

        # Normalize edilmiş skorları hesapla
        normalized_scores = {}
        for category, data in category_scores.items():
            if data['max_score'] > 0:
                normalized_score = (data['total_score'] / data['max_score']) * 100
                priority_level = self.determine_priority_level(normalized_score)

                normalized_scores[category] = {
                    'score': normalized_score,
                    'priority_level': priority_level,
                    'question_count': data['question_count'],
                    'questions': data['questions']
                }

        # Genel skor
        overall_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        overall_priority = self.determine_priority_level(overall_score)

        # Sonuçları kaydet
        self.save_prioritization_results(company_id, normalized_scores, overall_score, overall_priority)

        conn.close()

        return {
            'overall_score': overall_score,
            'overall_priority': overall_priority,
            'category_scores': normalized_scores,
            'total_questions': len(responses)
        }

    def determine_priority_level(self, score: float) -> str:
        """Öncelik seviyesi belirle"""
        if score >= 75:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"

    def save_prioritization_results(self, company_id: int, category_scores: Dict,
                                  overall_score: float, overall_priority: str) -> bool:
        """Önceliklendirme sonuçlarını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Mevcut sonuçları sil
            cursor.execute("DELETE FROM prioritization_results WHERE company_id = ?", (company_id,))

            # Yeni sonuçları kaydet
            for category, data in category_scores.items():
                cursor.execute("""
                    INSERT INTO prioritization_results 
                    (company_id, category, total_score, priority_level, calculation_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, category, data['score'], data['priority_level'],
                      datetime.now().isoformat()))

            # Genel sonucu kaydet
            cursor.execute("""
                INSERT INTO prioritization_results 
                (company_id, category, total_score, priority_level, calculation_date)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, "GENEL", overall_score, overall_priority,
                  datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Sonuç kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_prioritization_results(self, company_id: int) -> List[Dict]:
        """Önceliklendirme sonuçlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category, total_score, priority_level, calculation_date
            FROM prioritization_results
            WHERE company_id = ?
            ORDER BY total_score DESC
        """, (company_id,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'category': row[0],
                'total_score': row[1],
                'priority_level': row[2],
                'calculation_date': row[3]
            })

        conn.close()
        return results
