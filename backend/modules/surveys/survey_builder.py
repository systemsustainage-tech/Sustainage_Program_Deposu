#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Survey Builder - Anket Oluşturma ve Yönetim Sistemi
Refactored for Multi-tenancy using BaseTenantManager
"""

import logging
import json
from typing import Dict, List, Optional
from backend.core.base_manager import BaseTenantManager

class SurveyBuilder(BaseTenantManager):
    """
    Anket oluşturma ve yönetim sınıfı.
    Multi-tenant yapıya uygundur.
    """

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        import os
        # db_path verilmezse varsayılanı kullan
        final_db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        super().__init__(final_db_path, company_id)
        self.create_tables()

    def create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # Anket şablonları
            # Not: company_id ensure_multitenancy_schema.py tarafından ekleniyor, 
            # ancak burada yeni kurulumlar için ekleyebiliriz.
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS survey_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'Genel',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Anket soruları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS survey_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
                    template_id INTEGER,
                    survey_id INTEGER,
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
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS user_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
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

            # Anket cevapları (User Survey Responses)
            # survey_responses tablosu Materiality Survey ile çakıştığı için user_survey_responses kullanıyoruz
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS user_survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER DEFAULT 1,
                    user_survey_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    response_value TEXT,
                    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_survey_id) REFERENCES user_surveys(id),
                    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
                )
            """)
            
            # Indexler
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_survey_templates_company_id ON survey_templates (company_id)")
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_survey_questions_company_id ON survey_questions (company_id)")
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_user_surveys_company_id ON user_surveys (company_id)")
            self.execute_update("CREATE INDEX IF NOT EXISTS idx_user_survey_responses_company_id ON user_survey_responses (company_id)")

        except Exception as e:
            logging.error(f"Survey tabloları oluşturulurken hata: {e}")

    def create_sample_data(self) -> None:
        """Örnek anket verisi oluştur (Mevcut company için)"""
        try:
            cid = self._ensure_context(None)
            
            # Örnek anket şablonları
            sample_templates = [
                ("Sürdürülebilirlik Anketi", "SDG ve çevresel sürdürülebilirlik değerlendirmesi", "SDG"),
                ("İş Memnuniyeti Anketi", "Çalışan memnuniyeti ve motivasyon değerlendirmesi", "HR"),
                ("Kalite Anketi", "Ürün ve hizmet kalitesi değerlendirmesi", "Kalite"),
                ("Güvenlik Anketi", "İş güvenliği ve güvenlik kültürü değerlendirmesi", "Güvenlik"),
                ("Müşteri Memnuniyeti", "Müşteri deneyimi ve memnuniyet değerlendirmesi", "Müşteri")
            ]

            for name, desc, category in sample_templates:
                self.insert('survey_templates', {
                    'name': name,
                    'description': desc,
                    'category': category,
                    'is_active': 1
                }, company_id=cid)

            # Basitçe ilk şablonu alalım
            template = self.select_one('survey_templates', company_id=cid, order_by='id ASC')
            if not template:
                return
            
            template_id = template['id']

            sample_questions = [
                ("Şirketinizin çevresel sürdürülebilirlik hedefleri hakkında ne düşünüyorsunuz?", "scale", '{"min": 1, "max": 5, "labels": ["Çok Kötü", "Kötü", "Orta", "İyi", "Çok İyi"]}', 1.0, 1),
                ("Hangi SDG hedeflerinin öncelikli olduğunu düşünüyorsunuz?", "multiple_choice", '{"options": ["SDG 7 - Temiz Enerji", "SDG 13 - İklim Eylemi", "SDG 8 - İnsana Yakışır İş", "SDG 12 - Sorumlu Üretim"]}', 1.0, 1),
                ("Çevresel uygulamalarımızı nasıl değerlendiriyorsunuz?", "text", None, 0.8, 0),
                ("Sürdürülebilirlik eğitimleri yeterli mi?", "boolean", '{"options": ["Evet", "Hayır"]}', 0.6, 1),
                ("Hangi alanlarda iyileştirme yapılması gerektiğini düşünüyorsunuz?", "text", None, 0.9, 0)
            ]

            for question_text, question_type, options, weight, is_required in sample_questions:
                self.insert('survey_questions', {
                    'template_id': template_id,
                    'question_text': question_text,
                    'question_type': question_type,
                    'options': options,
                    'weight': weight,
                    'is_required': is_required
                }, company_id=cid)

            # Not: Kullanıcı anketleri oluşturmuyoruz çünkü user_id bilmemiz lazım.
            
        except Exception as e:
            logging.error(f"Örnek anket verisi oluşturulurken hata: {e}")

    def get_user_surveys(self, user_id: int) -> List[Dict]:
        """Kullanıcının anketlerini getir (Company context içinde)"""
        try:
            cid = self._ensure_context(None)
            
            # Join query olduğu için execute_query kullanıyoruz ve company_id'yi elle ekliyoruz
            query = """
                SELECT us.id, st.name, st.description, st.category, us.status, us.assigned_at
                FROM user_surveys us
                JOIN survey_templates st ON us.template_id = st.id
                WHERE us.user_id = ? AND us.company_id = ?
                ORDER BY us.assigned_at DESC
            """
            
            results = self.execute_query(query, (user_id, cid))
            
            surveys = []
            for row in results:
                # execute_query dictionary listesi döner
                surveys.append({
                    'id': row['id'],
                    'title': row['name'],
                    'description': row['description'],
                    'category': row['category'],
                    'status': row['status'],
                    'assigned_at': row['assigned_at']
                })

            return surveys

        except Exception as e:
            logging.error(f"Kullanıcı anketleri getirilirken hata: {e}")
            return []

    def get_survey_questions(self, template_id: int) -> List[Dict]:
        """Anket sorularını getir"""
        try:
            # BaseTenantManager.select otomatik company_id filtresi ekler
            rows = self.select(
                'survey_questions', 
                where='template_id = ?', 
                params=(template_id,),
                order_by='id'
            )

            questions = []
            for row in rows:
                options = json.loads(row['options']) if row.get('options') else None
                questions.append({
                    'id': row['id'],
                    'text': row['question_text'],
                    'type': row['question_type'],
                    'options': options,
                    'weight': row['weight'],
                    'required': bool(row['is_required'])
                })

            return questions

        except Exception as e:
            logging.error(f"Anket soruları getirilirken hata: {e}")
            return []

    def get_user_survey_detail(self, user_survey_id: int) -> Optional[Dict]:
        """user_surveys kaydı ve şablon bilgilerini getirir"""
        try:
            cid = self._ensure_context(None)
            
            query = """
                SELECT us.id, us.user_id, us.template_id, us.status, us.assigned_at, us.completed_at,
                       st.name, st.description, st.category
                FROM user_surveys us
                JOIN survey_templates st ON us.template_id = st.id
                WHERE us.id = ? AND us.company_id = ?
            """
            
            results = self.execute_query(query, (user_survey_id, cid))
            
            if not results:
                return None
                
            row = results[0]
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'template_id': row['template_id'],
                'status': row['status'],
                'assigned_at': row['assigned_at'],
                'completed_at': row['completed_at'],
                'template_name': row['name'],
                'template_description': row['description'],
                'template_category': row['category'],
            }
        except Exception as e:
            logging.error(f"Kullanıcı anket detayı getirilirken hata: {e}")
            return None

    def get_existing_responses(self, user_survey_id: int) -> Dict[int, str]:
        """Önceden kaydedilmiş yanıtları sözlük olarak döndür (question_id -> response_value)"""
        try:
            # BaseTenantManager.select otomatik company_id filtresi ekler
            rows = self.select(
                'user_survey_responses',
                columns=['question_id', 'response_value'],
                where='user_survey_id = ?',
                params=(user_survey_id,)
            )
            
            responses = {}
            for row in rows:
                responses[int(row['question_id'])] = row['response_value']
            return responses
        except Exception as e:
            logging.error(f"Önceki anket cevapları getirilirken hata: {e}")
            return {}

    def submit_survey_response(self, user_survey_id: int, question_id: int, response_value: str) -> bool:
        """Anket cevabını kaydet"""
        try:
            cid = self._ensure_context(None)
            
            # INSERT OR REPLACE için execute_update kullanıyoruz
            query = """
                INSERT OR REPLACE INTO user_survey_responses 
                (company_id, user_survey_id, question_id, response_value)
                VALUES (?, ?, ?, ?)
            """
            self.execute_update(query, (cid, user_survey_id, question_id, response_value))
            return True

        except Exception as e:
            logging.error(f"Anket cevabı kaydedilirken hata: {e}")
            return False

    def complete_survey(self, user_survey_id: int) -> bool:
        """Anketi tamamlandı olarak işaretle"""
        try:
            # BaseTenantManager.update otomatik company_id filtresi ekler
            self.update(
                'user_surveys',
                {'status': 'completed', 'completed_at': 'CURRENT_TIMESTAMP'}, # CURRENT_TIMESTAMP string olarak gider, DB'de string olur.
                # SQLite CURRENT_TIMESTAMP'i literal olarak kullanmak için raw SQL gerekir.
                # Ancak update metodumuz parametre olarak alıyor.
                # Bu yüzden Python tarafında zamanı almak daha iyi.
                where='id = ?',
                params=(user_survey_id,)
            )
            # Fix: CURRENT_TIMESTAMP'i düzeltelim
            from datetime import datetime
            now = datetime.now().isoformat()
            
            self.update(
                'user_surveys',
                {'status': 'completed', 'completed_at': now},
                where='id = ?',
                params=(user_survey_id,)
            )
            
            return True

        except Exception as e:
            logging.error(f"Anket tamamlanırken hata: {e}")
            return False
