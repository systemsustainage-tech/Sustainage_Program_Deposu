#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Paydaş Etkileşim Sistemi - TAM VE EKSİKSİZ
Portal, online anket, feedback, toplantı, eylem planı
"""

import logging
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config.database import DB_PATH


class StakeholderEngagement:
    """Paydaş etkileşim sistemi"""

    STAKEHOLDER_GROUPS = {
        "yatirimci": "Yatırımcılar",
        "calisan": "Çalışanlar",
        "musteri": "Müşteriler",
        "tedarikci": "Tedarikçiler",
        "topluluk": "Yerel Topluluk",
        "devlet": "Devlet ve Düzenleyiciler",
        "ngo": "STK'lar",
        "medya": "Medya"
    }

    ENGAGEMENT_PRIORITIES = {
        "yuksek": "Yüksek",
        "orta": "Orta",
        "dusuk": "Düşük"
    }

    EMPLOYEE_SATISFACTION_QUESTIONS = [
        {"id": "es_1", "question": "Şirkette çalışmaktan genel olarak ne kadar memnunsunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_2", "question": "Yöneticinizden aldığınız geri bildirimler ne kadar yapıcı?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_3", "question": "Şirket içi iletişim ne kadar etkili?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_4", "question": "Kariyer gelişim fırsatlarını yeterli buluyor musunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_5", "question": "İş-yaşam dengesi konusunda şirketin tutumunu nasıl değerlendiriyorsunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_6", "question": "Şirket değerleri ile kişisel değerleriniz ne kadar örtüşüyor?", "type": "scale", "min": 1, "max": 5},
        {"id": "es_comment", "question": "Eklemek istediğiniz diğer görüşleriniz:", "type": "text"}
    ]

    STAKEHOLDER_SATISFACTION_QUESTIONS = [
        {"id": "ss_1", "question": "Şirketimizle olan iş ilişkinizden genel olarak ne kadar memnunsunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "ss_2", "question": "Şirketimizin şeffaflık ve hesap verebilirlik düzeyini nasıl değerlendiriyorsunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "ss_3", "question": "Şirketimizle iletişim kurma kolaylığını nasıl değerlendiriyorsunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "ss_4", "question": "Şirketimizin sürdürülebilirlik konusundaki çabalarını samimi buluyor musunuz?", "type": "scale", "min": 1, "max": 5},
        {"id": "ss_5", "question": "Gelecekte şirketimizle iş birliğini sürdürme niyetiniz nedir?", "type": "scale", "min": 1, "max": 5},
        {"id": "ss_comment", "question": "Öneri ve görüşleriniz:", "type": "text"}
    ]

    SDG17_QUESTION_SET = [
        {
            "id": "SDG1",
            "goal": 1,
            "title": "Yoksulluğa Son",
            "question": "Şirketimizin yoksulluğun azaltılmasına ve kırılgan grupların desteklenmesine katkısını genel olarak nasıl değerlendiriyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG2",
            "goal": 2,
            "title": "Açlığa Son",
            "question": "Şirketimizin gıda güvenliği, sağlıklı beslenme ve sürdürülebilir tarım uygulamalarına etkisini genel olarak nasıl görüyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG3",
            "goal": 3,
            "title": "Sağlık ve Kaliteli Yaşam",
            "question": "Çalışanların ve toplumun sağlığı ile iş güvenliği konusunda şirketimizin performansını nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG4",
            "goal": 4,
            "title": "Nitelikli Eğitim",
            "question": "Şirketimizin çalışanlar ve paydaşlar için eğitim ve yetkinlik geliştirme olanaklarını ne ölçüde yeterli buluyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG5",
            "goal": 5,
            "title": "Toplumsal Cinsiyet Eşitliği",
            "question": "Toplumsal cinsiyet eşitliği, fırsat eşitliği ve kapsayıcılık açısından şirketimizin uygulamalarını nasıl görüyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG6",
            "goal": 6,
            "title": "Temiz Su ve Sanitasyon",
            "question": "Şirketimizin su kullanımı, atıksu yönetimi ve su kaynaklarının korunması konularındaki yaklaşımını nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG7",
            "goal": 7,
            "title": "Erişilebilir ve Temiz Enerji",
            "question": "Enerji verimliliği ve yenilenebilir enerji kullanımı açısından şirketimizin performansını nasıl buluyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG8",
            "goal": 8,
            "title": "İnsana Yakışır İş ve Ekonomik Büyüme",
            "question": "Çalışma koşulları, iş sağlığı ve güvenliği, adil ücret ve istihdam fırsatları açısından şirketimizi nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG9",
            "goal": 9,
            "title": "Sanayi, Yenilikçilik ve Altyapı",
            "question": "Şirketimizin yenilikçilik, verimli üretim ve sürdürülebilir altyapı yatırımları konusundaki yaklaşımını nasıl görüyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG10",
            "goal": 10,
            "title": "Eşitsizliklerin Azaltılması",
            "question": "Şirketimizin gelir, fırsat ve erişim eşitsizliklerini azaltmaya yönelik uygulamalarını ne kadar yeterli buluyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG11",
            "goal": 11,
            "title": "Sürdürülebilir Şehirler ve Topluluklar",
            "question": "Şirketimizin yerel topluluklarla ilişkisi, şehir yaşamına katkısı ve kentsel sürdürülebilirlik üzerindeki etkisini nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG12",
            "goal": 12,
            "title": "Sorumlu Üretim ve Tüketim",
            "question": "Kaynak verimliliği, atık azaltımı, döngüsel ekonomi ve sürdürülebilir tedarik zinciri uygulamaları açısından şirketimizi nasıl görüyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG13",
            "goal": 13,
            "title": "İklim Eylemi",
            "question": "İklim değişikliği ile mücadele, emisyon azaltımı ve iklim risklerinin yönetimi konularında şirketimizin performansını nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG14",
            "goal": 14,
            "title": "Sudaki Yaşam",
            "question": "Şirket faaliyetlerinin deniz ve su ekosistemleri üzerindeki etkilerini azaltmaya yönelik uygulamalarını nasıl buluyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG15",
            "goal": 15,
            "title": "Karasal Yaşam",
            "question": "Biyoçeşitliliğin korunması, arazi kullanımı ve ekosistemlerin yönetimi konularında şirketimizin yaklaşımını nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG16",
            "goal": 16,
            "title": "Barış, Adalet ve Güçlü Kurumlar",
            "question": "Etik değerler, şeffaflık, yolsuzlukla mücadele ve şikayet mekanizmaları açısından şirketimizi nasıl değerlendirirsiniz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        },
        {
            "id": "SDG17",
            "goal": 17,
            "title": "Amaçlar için Ortaklıklar",
            "question": "Şirketimizin kamu, özel sektör, STK'lar ve diğer paydaşlarla sürdürülebilirlik odaklı iş birliklerini nasıl görüyorsunuz?",
            "type": "scale",
            "min": 1,
            "max": 5,
            "allow_na": True
        }
    ]

    DEMOGRAPHIC_QUESTIONS = [
        {
            "id": "dem_stakeholder_group",
            "label": "Şirketle ilişkinizi en iyi tanımlayan paydaş grubu",
            "type": "select",
            "required": False,
            "options": [
                {"value": "calisan", "label": "Çalışan"},
                {"value": "tedarikci", "label": "Tedarikçi"},
                {"value": "musteri", "label": "Müşteri"},
                {"value": "yatirimci", "label": "Yatırımcı"},
                {"value": "topluluk", "label": "Yerel topluluk / toplum temsilcisi"},
                {"value": "devlet", "label": "Kamu kurumu / düzenleyici"},
                {"value": "ngo", "label": "STK / sivil toplum"},
                {"value": "medya", "label": "Medya"},
                {"value": "diger", "label": "Diğer"}
            ]
        },
        {
            "id": "dem_relationship_years",
            "label": "Şirketle iş ilişkisi süreniz",
            "type": "select",
            "required": False,
            "options": [
                {"value": "lt1", "label": "1 yıldan az"},
                {"value": "1_3", "label": "1-3 yıl"},
                {"value": "3_5", "label": "3-5 yıl"},
                {"value": "gt5", "label": "5 yıldan uzun"}
            ]
        },
        {
            "id": "dem_country",
            "label": "Bulunduğunuz ülke",
            "type": "text",
            "required": False
        }
    ]

    GROUP_SDG_SUBSETS = {
        "calisan": ["SDG3", "SDG4", "SDG5", "SDG8", "SDG10", "SDG16"],
        "tedarikci": ["SDG6", "SDG7", "SDG9", "SDG12", "SDG13", "SDG17"],
        "yatirimci": ["SDG8", "SDG9", "SDG10", "SDG13", "SDG17"],
        "musteri": ["SDG3", "SDG8", "SDG9", "SDG12"],
        "topluluk": ["SDG1", "SDG3", "SDG10", "SDG11", "SDG16", "SDG17"],
        "devlet": ["SDG6", "SDG7", "SDG9", "SDG11", "SDG13", "SDG16", "SDG17"],
        "ngo": ["SDG1", "SDG5", "SDG10", "SDG13", "SDG15", "SDG16", "SDG17"],
        "medya": ["SDG8", "SDG11", "SDG12", "SDG13", "SDG16", "SDG17"]
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_stakeholder_tables()

    def _init_stakeholder_tables(self) -> None:
        """Paydaş tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Paydaş kayıtları (Migration support)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stakeholders'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE stakeholders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        stakeholder_type TEXT NOT NULL,
                        stakeholder_name TEXT NOT NULL,
                        organization TEXT,
                        contact_email TEXT,
                        contact_phone TEXT,
                        priority_level TEXT DEFAULT 'orta',
                        engagement_frequency TEXT,
                        portal_access_token TEXT UNIQUE,
                        portal_enabled BOOLEAN DEFAULT 0,
                        last_contacted DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (company_id) REFERENCES companies(id)
                    )
                """)
            else:
                # Add missing columns if table exists
                cols_to_add = [
                    ("portal_access_token", "TEXT UNIQUE"),
                    ("portal_enabled", "BOOLEAN DEFAULT 0"),
                    ("last_contacted", "DATE"),
                    ("priority_level", "TEXT DEFAULT 'orta'")
                ]
                for col, type_def in cols_to_add:
                    try:
                        cursor.execute(f"ALTER TABLE stakeholders ADD COLUMN {col} {type_def}")
                    except sqlite3.OperationalError:
                        pass

            # Online anketler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS online_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_title TEXT NOT NULL,
                    survey_description TEXT,
                    survey_type TEXT DEFAULT 'sdg',
                    target_groups TEXT NOT NULL,
                    survey_link TEXT UNIQUE NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    total_questions INTEGER DEFAULT 0,
                    response_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Add survey_type column if not exists
            try:
                cursor.execute("ALTER TABLE online_surveys ADD COLUMN survey_type TEXT DEFAULT 'sdg'")
            except sqlite3.OperationalError:
                pass


            # Anket yanıtları (external)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    response_token TEXT UNIQUE NOT NULL,
                    responses TEXT NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY (survey_id) REFERENCES online_surveys(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            # Gerçek zamanlı feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    feedback_type TEXT NOT NULL,
                    feedback_category TEXT,
                    feedback_text TEXT NOT NULL,
                    rating INTEGER,
                    attachment_path TEXT,
                    status TEXT DEFAULT 'yeni',
                    responded_by INTEGER,
                    response_text TEXT,
                    responded_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            # Paydaş toplantıları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    meeting_title TEXT NOT NULL,
                    meeting_type TEXT NOT NULL,
                    meeting_date DATETIME NOT NULL,
                    duration_minutes INTEGER DEFAULT 60,
                    location TEXT,
                    meeting_link TEXT,
                    agenda TEXT,
                    participants TEXT,
                    minutes_of_meeting TEXT,
                    action_items TEXT,
                    status TEXT DEFAULT 'planlandı',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Eylem planı (commitment tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_commitments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    meeting_id INTEGER,
                    commitment_title TEXT NOT NULL,
                    commitment_description TEXT,
                    responsible_person TEXT,
                    target_stakeholder_group TEXT,
                    due_date DATE,
                    priority TEXT DEFAULT 'orta',
                    status TEXT DEFAULT 'acik',
                    progress_percentage INTEGER DEFAULT 0,
                    completion_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (meeting_id) REFERENCES stakeholder_meetings(id)
                )
            """)

            # Portal erişim logları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portal_access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stakeholder_id INTEGER NOT NULL,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    action_type TEXT,
                    details TEXT,
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            # Eğitim Materyalleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    content_type TEXT, 
                    content_url TEXT NOT NULL,
                    target_groups TEXT, 
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Paydaş Eğitim İlerlemesi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholder_training_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stakeholder_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'assigned', 
                    progress_percentage INTEGER DEFAULT 0,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    score INTEGER,
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id),
                    FOREIGN KEY (material_id) REFERENCES training_materials(id),
                    UNIQUE(stakeholder_id, material_id)
                )
            """)

            conn.commit()
            logging.info("[OK] Paydas etkilesim tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Paydas tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. PAYDAŞ PORTALI (EXTERNAL ACCESS)
    # =====================================================

    def enable_portal_access(self, stakeholder_id: int) -> str:
        """
        Paydaş için portal erişimi aktif et
        
        Returns:
            Portal erişim token'ı
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Güvenli token oluştur
            access_token = secrets.token_urlsafe(32)

            cursor.execute("""
                UPDATE stakeholders
                SET portal_access_token = ?,
                    portal_enabled = 1
                WHERE id = ?
            """, (access_token, stakeholder_id))

            conn.commit()

            # Portal URL'i
            portal_url = f"https://portal.sustainage.com/stakeholder/{access_token}"

            logging.info(f"[OK] Portal erisimi aktif edildi: {stakeholder_id}")
            return portal_url

        except Exception as e:
            logging.error(f"Portal aktifleştirme hatasi: {e}")
            return ""
        finally:
            conn.close()

    def verify_portal_access(self, access_token: str) -> Optional[Dict]:
        """Portal token'ı doğrula"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM stakeholders
                WHERE portal_access_token = ? AND portal_enabled = 1
            """, (access_token,))

            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))

            return None

        except Exception as e:
            logging.error(f"Token dogrulama hatasi: {e}")
            return None
        finally:
            conn.close()

    # =====================================================
    # 2. ONLINE ANKET DAĞITIMI (WEB LINK)
    # =====================================================

    def create_online_survey(self, company_id: int, title: str,
                            description: str, target_groups: List[str],
                            questions: List[Dict], duration_days: int = 30,
                            survey_type: str = "sdg") -> str:
        """
        Online anket oluştur ve web linki üret
        
        Args:
            questions: [
                {'question': 'Memnuniyet?', 'type': 'rating', 'scale': 5},
                {'question': 'Görüş?', 'type': 'text'},
                ...
            ]
            survey_type: 'sdg', 'employee', 'stakeholder'
            
        Returns:
            Anket web linki
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            survey_token = secrets.token_urlsafe(16)
            base_url = os.environ.get("SURVEY_BASE_URL", "https://survey.sustainage.com").rstrip("/")
            survey_link = f"{base_url}/{survey_token}"

            # Anket kaydet
            cursor.execute("""
                INSERT INTO online_surveys
                (company_id, survey_title, survey_description, target_groups,
                 survey_link, start_date, end_date, total_questions, survey_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, title, description,
                json.dumps(target_groups),
                survey_link,
                datetime.now().date(),
                (datetime.now() + timedelta(days=duration_days)).date(),
                len(questions),
                survey_type
            ))

            survey_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Online anket olusturuldu: {survey_id} (Tip: {survey_type})")
            return survey_link

        except Exception as e:
            logging.error(f"Anket olusturma hatasi: {e}")
            return ""
        finally:
            conn.close()

    def create_employee_satisfaction_survey(self, company_id: int, 
                                          title: str = "Çalışan Memnuniyeti Anketi",
                                          duration_days: int = 30) -> str:
        """Çalışan memnuniyeti anketi oluştur"""
        return self.create_online_survey(
            company_id=company_id,
            title=title,
            description="Çalışanlarımızın memnuniyetini ve bağlılığını ölçmek amacıyla hazırlanan anket.",
            target_groups=["calisan"],
            questions=self.EMPLOYEE_SATISFACTION_QUESTIONS,
            duration_days=duration_days,
            survey_type="employee"
        )

    def create_stakeholder_satisfaction_survey(self, company_id: int,
                                             title: str = "Paydaş Memnuniyeti Anketi",
                                             duration_days: int = 30) -> str:
        """Paydaş memnuniyeti anketi oluştur"""
        return self.create_online_survey(
            company_id=company_id,
            title=title,
            description="Değerli paydaşlarımızın görüş ve önerilerini almak için hazırlanan anket.",
            target_groups=["tedarikci", "musteri", "yatirimci", "topluluk"],
            questions=self.STAKEHOLDER_SATISFACTION_QUESTIONS,
            duration_days=duration_days,
            survey_type="stakeholder"
        )

    def get_survey_questions_by_type(self, survey_type: str) -> List[Dict]:
        """Anket tipine göre soruları getir"""
        if survey_type == "employee":
            return list(self.EMPLOYEE_SATISFACTION_QUESTIONS)
        elif survey_type == "stakeholder":
            return list(self.STAKEHOLDER_SATISFACTION_QUESTIONS)
        else:
            # Default SDG
            return list(self.SDG17_QUESTION_SET)

    def get_general_sdg_survey_questions(self) -> List[Dict]:
        return list(self.SDG17_QUESTION_SET)

    def get_demographic_questions(self) -> List[Dict]:
        return list(self.DEMOGRAPHIC_QUESTIONS)

    def get_sdg_survey_questions_for_group(self, group_key: str) -> List[Dict]:
        subset = self.GROUP_SDG_SUBSETS.get(group_key)
        if not subset:
            return self.get_general_sdg_survey_questions()
        questions_map = {q["id"]: q for q in self.SDG17_QUESTION_SET}
        selected = []
        for qid in subset:
            if qid in questions_map:
                selected.append(questions_map[qid])
        if not selected:
            return self.get_general_sdg_survey_questions()
        return selected

    def submit_survey_response(self, survey_link: str, responses: Dict,
                              stakeholder_id: int = None) -> bool:
        """Anket yanıtını kaydet (external)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if "://" in survey_link:
                cursor.execute("""
                    SELECT id FROM online_surveys
                    WHERE survey_link = ? AND is_active = 1
                """, (survey_link,))
            else:
                cursor.execute("""
                    SELECT id FROM online_surveys
                    WHERE survey_link LIKE ? AND is_active = 1
                """, (f"%/{survey_link}",))

            result = cursor.fetchone()
            if not result:
                return False

            survey_id = result[0]
            response_token = secrets.token_urlsafe(16)

            # Yanıtı kaydet
            cursor.execute("""
                INSERT INTO survey_responses
                (survey_id, stakeholder_id, response_token, responses)
                VALUES (?, ?, ?, ?)
            """, (survey_id, stakeholder_id, response_token, json.dumps(responses)))

            # Yanıt sayısını güncelle
            cursor.execute("""
                UPDATE online_surveys
                SET response_count = response_count + 1
                WHERE id = ?
            """, (survey_id,))

            conn.commit()
            logging.info(f"[OK] Anket yaniti kaydedildi: {survey_id}")
            
            # Otomatik analiz tetikle
            self._update_survey_analytics(survey_id, responses)
            
            return True

        except Exception as e:
            logging.error(f"Anket yanit kaydetme hatasi: {e}")
            return False
        finally:
            conn.close()
            
    def _update_survey_analytics(self, survey_id: int, new_response: Dict) -> None:
        """
        Her yeni yanıtta anket istatistiklerini güncelle.
        Bu fonksiyon, raporlamalarda kullanılacak olan 'sdg_survey_analytics' 
        tablosunu besler.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Tablo yoksa oluştur (Basit cache/summary tablosu)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_survey_analytics (
                    survey_id INTEGER,
                    sdg_id TEXT,
                    total_score INTEGER DEFAULT 0,
                    response_count INTEGER DEFAULT 0,
                    average_score REAL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (survey_id, sdg_id)
                )
            """)
            
            # Yanıtlardaki skorları işle
            answers = new_response.get('answers', {})
            for q_id, value in answers.items():
                # Sadece SDG sorularını ve sayısal değerleri al (SDG1, SDG2... formatı)
                if q_id.startswith('SDG') and str(value).isdigit():
                    score = int(value)
                    
                    # Mevcut kaydı kontrol et
                    cursor.execute("""
                        INSERT INTO sdg_survey_analytics (survey_id, sdg_id, total_score, response_count, average_score)
                        VALUES (?, ?, ?, 1, ?)
                        ON CONFLICT(survey_id, sdg_id) DO UPDATE SET
                        total_score = total_score + excluded.total_score,
                        response_count = response_count + 1,
                        average_score = CAST((total_score + excluded.total_score) AS REAL) / (response_count + 1),
                        updated_at = CURRENT_TIMESTAMP
                    """, (survey_id, q_id, score, float(score)))
            
            conn.commit()
            logging.info(f"[OK] Anket analizi guncellendi: Survey {survey_id}")
            
        except Exception as e:
            logging.error(f"Analiz guncelleme hatasi: {e}")
        finally:
            conn.close()

    def get_sdg_performance_scores(self, company_id: int) -> Dict[str, float]:
        """
        Şirketin SDG performans skorlarını getir.
        Raporlama modülü bu fonksiyonu kullanacak.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        scores = {}
        
        try:
            cursor.execute("""
                SELECT ssa.sdg_id, AVG(ssa.average_score) as final_score
                FROM sdg_survey_analytics ssa
                JOIN online_surveys os ON ssa.survey_id = os.id
                WHERE os.company_id = ? AND os.is_active = 1
                GROUP BY ssa.sdg_id
            """, (company_id,))
            
            for row in cursor.fetchall():
                scores[row[0]] = round(row[1], 2)
                
            return scores
        except Exception as e:
            logging.error(f"Skor getirme hatasi: {e}")
            return {}
        finally:
            conn.close()

    # =====================================================
    # 3. GERÇEK ZAMANLI FEEDBACK
    # =====================================================

    def submit_feedback(self, company_id: int, feedback_type: str,
                       category: str, text: str, rating: int = None,
                       stakeholder_id: int = None) -> int:
        """
        Gerçek zamanlı feedback gönder
        
        Args:
            feedback_type: oneri, sikayet, tesekkur, soru
            category: cevre, sosyal, yonetisim, urun
            rating: 1-5 yıldız
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO stakeholder_feedback
                (company_id, stakeholder_id, feedback_type, feedback_category,
                 feedback_text, rating, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, stakeholder_id, feedback_type, category,
                  text, rating, 'yeni'))

            feedback_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Feedback kaydedildi: {feedback_id}")
            return feedback_id

        except Exception as e:
            logging.error(f"Feedback kaydetme hatasi: {e}")
            return 0
        finally:
            conn.close()

    def respond_to_feedback(self, feedback_id: int, responded_by: int,
                           response_text: str) -> bool:
        """Feedback'e yanıt ver"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE stakeholder_feedback
                SET status = 'yanitlandi',
                    responded_by = ?,
                    response_text = ?,
                    responded_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (responded_by, response_text, feedback_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yanit verme hatasi: {e}")
            return False
        finally:
            conn.close()

    # =====================================================
    # 4. TOPLANTI YÖNETİMİ
    # =====================================================

    def schedule_meeting(self, company_id: int, title: str,
                        meeting_type: str, meeting_date: datetime,
                        participants: List[str], agenda: str = "",
                        location: str = "", online_link: str = "") -> int:
        """
        Paydaş toplantısı planla
        
        Args:
            meeting_type: genel_kurul, paydas_toplantisi, odak_grubu, webinar
            participants: Katılımcı email listesi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO stakeholder_meetings
                (company_id, meeting_title, meeting_type, meeting_date,
                 location, meeting_link, agenda, participants, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, title, meeting_type, meeting_date.isoformat(),
                  location, online_link, agenda, json.dumps(participants), 'planlandi'))

            meeting_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Toplanti planlandi: {meeting_id}")
            return meeting_id

        except Exception as e:
            logging.error(f"Toplanti planlama hatasi: {e}")
            return 0
        finally:
            conn.close()

    def add_meeting_minutes(self, meeting_id: int, minutes: str,
                           action_items: List[Dict]) -> bool:
        """Toplantı tutanağı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE stakeholder_meetings
                SET minutes_of_meeting = ?,
                    action_items = ?,
                    status = 'tamamlandi'
                WHERE id = ?
            """, (minutes, json.dumps(action_items), meeting_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Tutanak ekleme hatasi: {e}")
            return False
        finally:
            conn.close()

    # =====================================================
    # 5. EYLEM PLANI TAKİBİ (COMMITMENT TRACKING)
    # =====================================================

    def create_commitment(self, company_id: int, title: str,
                         description: str, responsible: str,
                         target_group: str, due_date: datetime,
                         priority: str = "orta",
                         meeting_id: int = None) -> int:
        """
        Paydaş taahhüdü oluştur
        
        Args:
            title: Taahhüt başlığı
            responsible: Sorumlu kişi/birim
            target_group: Hedef paydaş grubu
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO stakeholder_commitments
                (company_id, meeting_id, commitment_title, commitment_description,
                 responsible_person, target_stakeholder_group, due_date, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, meeting_id, title, description, responsible,
                  target_group, due_date.date(), priority, 'acik'))

            commitment_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Taahhut olusturuldu: {commitment_id}")
            return commitment_id

        except Exception as e:
            logging.error(f"Taahhut olusturma hatasi: {e}")
            return 0
        finally:
            conn.close()

    def update_commitment_progress(self, commitment_id: int,
                                  progress: int, notes: str = "") -> bool:
        """Taahhüt ilerlemesini güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            status = 'tamamlandi' if progress >= 100 else 'devam_ediyor' if progress > 0 else 'acik'

            cursor.execute("""
                UPDATE stakeholder_commitments
                SET progress_percentage = ?,
                    status = ?,
                    completion_notes = ?,
                    completed_at = CASE WHEN ? >= 100 THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE id = ?
            """, (progress, status, notes, progress, commitment_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Ilerleme guncelleme hatasi: {e}")
            return False
        finally:
            conn.close()

    def get_commitment_summary(self, company_id: int) -> Dict:
        """Taahhüt özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            summary = {
                "total_commitments": 0,
                "open": 0,
                "in_progress": 0,
                "completed": 0,
                "overdue": 0,
                "average_progress": 0.0
            }

            cursor.execute("""
                SELECT status, COUNT(*), AVG(progress_percentage)
                FROM stakeholder_commitments
                WHERE company_id = ?
                GROUP BY status
            """, (company_id,))

            for row in cursor.fetchall():
                summary["total_commitments"] += row[1]
                if row[0] == 'acik':
                    summary["open"] = row[1]
                elif row[0] == 'devam_ediyor':
                    summary["in_progress"] = row[1]
                elif row[0] == 'tamamlandi':
                    summary["completed"] = row[1]

            # Genel ortalama ilerleme
            cursor.execute("""
                SELECT AVG(progress_percentage) FROM stakeholder_commitments
                WHERE company_id = ?
            """, (company_id,))

            result = cursor.fetchone()
            summary["average_progress"] = round(result[0], 1) if result[0] else 0.0

            # Vadesi geçenler
            cursor.execute("""
                SELECT COUNT(*) FROM stakeholder_commitments
                WHERE company_id = ? AND due_date < DATE('now')
                AND status != 'tamamlandi'
            """, (company_id,))

            summary["overdue"] = cursor.fetchone()[0]

            return summary

        except Exception as e:
            logging.error(f"Ozet hesaplama hatasi: {e}")
            return summary
        finally:
            conn.close()

    # =====================================================
    # 6. YARDIMCI FONKSİYONLAR
    # =====================================================

    def get_stakeholder_engagement_score(self, company_id: int) -> Dict:
        """Paydaş etkileşim skoru hesapla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            score_data = {
                "total_stakeholders": 0,
                "portal_enabled": 0,
                "survey_participation": 0.0,
                "feedback_response_rate": 0.0,
                "commitment_completion": 0.0,
                "overall_score": 0.0
            }

            # Toplam paydaş
            cursor.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id = ?", (company_id,))
            score_data["total_stakeholders"] = cursor.fetchone()[0]

            # Portal kullanımı
            cursor.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id = ? AND portal_enabled = 1", (company_id,))
            score_data["portal_enabled"] = cursor.fetchone()[0]

            # Anket katılımı
            cursor.execute("""
                SELECT AVG(response_count * 100.0 / total_questions)
                FROM online_surveys WHERE company_id = ?
            """, (company_id,))
            result = cursor.fetchone()
            score_data["survey_participation"] = round(result[0], 1) if result[0] else 0.0

            # Taahhüt tamamlanma
            commitment_summary = self.get_commitment_summary(company_id)
            score_data["commitment_completion"] = commitment_summary["average_progress"]

            # Genel skor (ağırlıklı)
            overall = (
                (score_data["portal_enabled"] / max(score_data["total_stakeholders"], 1)) * 25 +
                (score_data["survey_participation"]) * 0.25 +
                (score_data["commitment_completion"]) * 0.50
            )
            score_data["overall_score"] = round(overall, 1)

            conn.close()
            return score_data

        except Exception as e:
            logging.error(f"Skor hesaplama hatasi: {e}")
            return score_data

    # =====================================================
    # 7. EĞİTİM YÖNETİMİ (TRAINING MANAGEMENT)
    # =====================================================

    def add_training_material(self, company_id: int, title: str, 
                             content_url: str, description: str = "",
                             content_type: str = "video",
                             target_groups: List[str] = []) -> int:
        """Eğitim materyali ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO training_materials
                (company_id, title, description, content_type, content_url, target_groups)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, title, description, content_type, content_url, json.dumps(target_groups)))
            
            material_id = cursor.lastrowid
            conn.commit()
            return material_id
        except Exception as e:
            logging.error(f"Egitim ekleme hatasi: {e}")
            return 0
        finally:
            conn.close()

    def assign_training(self, material_id: int, stakeholder_id: int) -> bool:
        """Paydaşa eğitim ata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO stakeholder_training_progress
                (stakeholder_id, material_id, status)
                VALUES (?, ?, 'assigned')
            """, (stakeholder_id, material_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Egitim atama hatasi: {e}")
            return False
        finally:
            conn.close()

    def update_training_status(self, stakeholder_id: int, material_id: int,
                              status: str, progress: int = 0) -> bool:
        """Eğitim durumunu güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            completed_at = datetime.now() if status == 'completed' or progress >= 100 else None
            cursor.execute("""
                UPDATE stakeholder_training_progress
                SET status = ?, progress_percentage = ?, completed_at = ?
                WHERE stakeholder_id = ? AND material_id = ?
            """, (status, progress, completed_at, stakeholder_id, material_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Egitim guncelleme hatasi: {e}")
            return False
        finally:
            conn.close()

    def get_training_materials(self, company_id: int) -> List[Dict]:
        """Eğitim materyallerini listele"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM training_materials WHERE company_id = ? AND is_active = 1", (company_id,))
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logging.error(f"Egitim listeleme hatasi: {e}")
            return []
        finally:
            conn.close()

    def get_stakeholder_trainings(self, stakeholder_id: int) -> List[Dict]:
        """Paydaşın eğitimlerini listele"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT tm.title, tm.content_type, tm.content_url, stp.*
                FROM stakeholder_training_progress stp
                JOIN training_materials tm ON stp.material_id = tm.id
                WHERE stp.stakeholder_id = ?
            """, (stakeholder_id,))
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description]
            return [dict(zip(cols, row)) for row in rows]
        except Exception as e:
            logging.error(f"Paydas egitim listeleme hatasi: {e}")
            return []
        finally:
            conn.close()

    def get_employee_satisfaction_questions(self) -> List[Dict]:
        return list(self.EMPLOYEE_SATISFACTION_QUESTIONS)

    def get_stakeholder_satisfaction_questions(self) -> List[Dict]:
        return list(self.STAKEHOLDER_SATISFACTION_QUESTIONS)

