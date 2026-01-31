#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çok Dilli Raporlama Modülü
Çoklu dil desteği ve çeviri yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional
from config.database import DB_PATH


class MultilingualManager:
    """Çok dilli raporlama ve çeviri yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()
        self._init_default_translations()

    def _init_db_tables(self) -> None:
        """Çok dilli modülü tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    text_key TEXT NOT NULL,
                    language_code TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    context TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS supported_languages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language_code TEXT UNIQUE NOT NULL,
                    language_name TEXT NOT NULL,
                    native_name TEXT NOT NULL,
                    is_rtl TEXT DEFAULT 'false',
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] Cok dilli modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Cok dilli modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _init_default_translations(self) -> None:
        """Varsayılan çevirileri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Desteklenen diller
            languages = [
                ('tr', 'Turkish', 'Türkçe', 'false'),
                ('en', 'English', 'English', 'false'),
                ('de', 'German', 'Deutsch', 'false'),
                ('fr', 'French', 'Français', 'false'),
                ('es', 'Spanish', 'Español', 'false'),
                ('ar', 'Arabic', 'العربية', 'true'),
                ('zh', 'Chinese', '中文', 'false'),
                ('ja', 'Japanese', '日本語', 'false')
            ]

            for lang_code, lang_name, native_name, is_rtl in languages:
                cursor.execute("""
                    INSERT OR IGNORE INTO supported_languages 
                    (language_code, language_name, native_name, is_rtl)
                    VALUES (?, ?, ?, ?)
                """, (lang_code, lang_name, native_name, is_rtl))

            # Varsayılan çeviriler
            default_translations = [
                # Genel terimler
                ('sustainability_report', 'tr', 'Sürdürülebilirlik Raporu'),
                ('sustainability_report', 'en', 'Sustainability Report'),
                ('sustainability_report', 'de', 'Nachhaltigkeitsbericht'),
                ('sustainability_report', 'fr', 'Rapport de Durabilité'),

                ('environmental_performance', 'tr', 'Çevresel Performans'),
                ('environmental_performance', 'en', 'Environmental Performance'),
                ('environmental_performance', 'de', 'Umweltleistung'),
                ('environmental_performance', 'fr', 'Performance Environnementale'),

                ('social_performance', 'tr', 'Sosyal Performans'),
                ('social_performance', 'en', 'Social Performance'),
                ('social_performance', 'de', 'Soziale Leistung'),
                ('social_performance', 'fr', 'Performance Sociale'),

                ('economic_performance', 'tr', 'Ekonomik Performans'),
                ('economic_performance', 'en', 'Economic Performance'),
                ('economic_performance', 'de', 'Wirtschaftliche Leistung'),
                ('economic_performance', 'fr', 'Performance Économique'),

                ('governance', 'tr', 'Yönetişim'),
                ('governance', 'en', 'Governance'),
                ('governance', 'de', 'Governance'),
                ('governance', 'fr', 'Gouvernance'),

                # KPI'lar
                ('carbon_footprint', 'tr', 'Karbon Ayak İzi'),
                ('carbon_footprint', 'en', 'Carbon Footprint'),
                ('carbon_footprint', 'de', 'CO2-Fußabdruck'),
                ('carbon_footprint', 'fr', 'Empreinte Carbone'),

                ('energy_consumption', 'tr', 'Enerji Tüketimi'),
                ('energy_consumption', 'en', 'Energy Consumption'),
                ('energy_consumption', 'de', 'Energieverbrauch'),
                ('energy_consumption', 'fr', 'Consommation d\'Énergie'),

                ('water_consumption', 'tr', 'Su Tüketimi'),
                ('water_consumption', 'en', 'Water Consumption'),
                ('water_consumption', 'de', 'Wasserverbrauch'),
                ('water_consumption', 'fr', 'Consommation d\'Eau'),

                ('waste_generation', 'tr', 'Atık Üretimi'),
                ('waste_generation', 'en', 'Waste Generation'),
                ('waste_generation', 'de', 'Abfallerzeugung'),
                ('waste_generation', 'fr', 'Génération de Déchets'),

                ('employee_satisfaction', 'tr', 'Çalışan Memnuniyeti'),
                ('employee_satisfaction', 'en', 'Employee Satisfaction'),
                ('employee_satisfaction', 'de', 'Mitarbeiterzufriedenheit'),
                ('employee_satisfaction', 'fr', 'Satisfaction des Employés'),
            ]

            for text_key, lang_code, translated_text in default_translations:
                cursor.execute("""
                    INSERT OR IGNORE INTO translations 
                    (company_id, text_key, language_code, translated_text)
                    VALUES (0, ?, ?, ?)
                """, (text_key, lang_code, translated_text))

            conn.commit()
            logging.info("[OK] Varsayilan ceviriler eklendi")

        except Exception as e:
            logging.error(f"[HATA] Varsayilan ceviriler ekleme: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_translation(self, company_id: int, text_key: str, language_code: str,
                       translated_text: str, context: Optional[str] = None) -> bool:
        """Çeviri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO translations 
                (company_id, text_key, language_code, translated_text, context)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, text_key, language_code, translated_text, context))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çeviri ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_translation(self, text_key: str, language_code: str, company_id: int = 0) -> str:
        """Çeviri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Önce şirket özel çeviriyi ara, sonra genel çeviriyi ara
            cursor.execute("""
                SELECT translated_text FROM translations 
                WHERE text_key = ? AND language_code = ? AND company_id = ? AND status = 'active'
                UNION
                SELECT translated_text FROM translations 
                WHERE text_key = ? AND language_code = ? AND company_id = 0 AND status = 'active'
                LIMIT 1
            """, (text_key, language_code, company_id, text_key, language_code))

            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return text_key  # Çeviri bulunamazsa orijinal metni döndür

        except Exception as e:
            logging.error(f"Çeviri getirme hatası: {e}")
            return text_key
        finally:
            conn.close()

    def get_supported_languages(self) -> List[Dict]:
        """Desteklenen dilleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT language_code, language_name, native_name, is_rtl
                FROM supported_languages 
                WHERE status = 'active'
                ORDER BY language_name
            """)

            languages = []
            for row in cursor.fetchall():
                languages.append({
                    'language_code': row[0],
                    'language_name': row[1],
                    'native_name': row[2],
                    'is_rtl': row[3] == 'true'
                })

            return languages

        except Exception as e:
            logging.error(f"Desteklenen diller getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def translate_report_content(self, content: str, target_language: str, company_id: int = 0) -> str:
        """Rapor içeriğini çevir"""
        # Basit çeviri - gerçek uygulamada daha gelişmiş çeviri servisi kullanılabilir
        translated_content = content

        # Yaygın terimleri çevir
        translations = {
            'tr': {
                'Sustainability Report': 'Sürdürülebilirlik Raporu',
                'Environmental Performance': 'Çevresel Performans',
                'Social Performance': 'Sosyal Performans',
                'Economic Performance': 'Ekonomik Performans',
                'Governance': 'Yönetişim'
            },
            'en': {
                'Sürdürülebilirlik Raporu': 'Sustainability Report',
                'Çevresel Performans': 'Environmental Performance',
                'Sosyal Performans': 'Social Performance',
                'Ekonomik Performans': 'Economic Performance',
                'Yönetişim': 'Governance'
            }
        }

        if target_language in translations:
            for original, translated in translations[target_language].items():
                translated_content = translated_content.replace(original, translated)

        return translated_content
