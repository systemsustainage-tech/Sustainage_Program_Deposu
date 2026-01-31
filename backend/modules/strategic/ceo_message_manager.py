#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO/Genel Müdür Mesajı Yöneticisi
Sürdürülebilirlik raporları için yönetici mesajları
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List


class CEOMessageManager:
    """CEO/Genel Müdür mesaj yöneticisi"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # CEO mesajları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ceo_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message_type TEXT NOT NULL, -- 'annual', 'quarterly', 'sustainability', 'emergency'
                    year INTEGER NOT NULL,
                    quarter INTEGER, -- 1-4, NULL for annual
                    content TEXT NOT NULL,
                    key_achievements TEXT, -- JSON array
                    challenges TEXT, -- JSON array
                    future_commitments TEXT, -- JSON array
                    signature_name TEXT,
                    signature_title TEXT,
                    signature_date TEXT,
                    is_published INTEGER DEFAULT 0,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                )
            """)

            # Mesaj şablonları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    template_content TEXT NOT NULL, -- JSON template
                    variables TEXT, -- JSON array of variable names
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Mesaj değişkenleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS message_variables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    variable_name TEXT NOT NULL,
                    variable_value TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES ceo_messages(id)
                )
            """)

            conn.commit()
            logging.info("[OK] CEO mesaj tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Tablo oluşturma hatası: {e}")
        finally:
            conn.close()

    def create_message(self, company_id: int, title: str, message_type: str, year: int,
                      quarter: int = None, content: str = "", key_achievements: List[str] = None,
                      challenges: List[str] = None, future_commitments: List[str] = None,
                      signature_name: str = "", signature_title: str = "", created_by: int = None) -> int:
        """
        Yeni CEO mesajı oluştur
        
        Args:
            company_id: Şirket ID
            title: Mesaj başlığı
            message_type: Mesaj türü ('annual', 'quarterly', 'sustainability', 'emergency')
            year: Yıl
            quarter: Çeyrek (1-4, None for annual)
            content: Mesaj içeriği
            key_achievements: Ana başarılar listesi
            challenges: Zorluklar listesi
            future_commitments: Gelecek taahhütleri listesi
            signature_name: İmza adı
            signature_title: İmza unvanı
            created_by: Oluşturan kullanıcı ID
        
        Returns:
            Oluşturulan mesaj ID'si
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Aynı dönem için mesaj kontrolü
            if quarter:
                cursor.execute("""
                    SELECT id FROM ceo_messages 
                    WHERE company_id = ? AND message_type = ? AND year = ? AND quarter = ?
                """, (company_id, message_type, year, quarter))
            else:
                cursor.execute("""
                    SELECT id FROM ceo_messages 
                    WHERE company_id = ? AND message_type = ? AND year = ? AND quarter IS NULL
                """, (company_id, message_type, year))

            existing = cursor.fetchone()
            if existing:
                raise ValueError(f"Bu dönem için mesaj zaten mevcut (ID: {existing[0]})")

            cursor.execute("""
                INSERT INTO ceo_messages 
                (company_id, title, message_type, year, quarter, content, 
                 key_achievements, challenges, future_commitments, signature_name, 
                 signature_title, signature_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, title, message_type, year, quarter, content,
                json.dumps(key_achievements or []),
                json.dumps(challenges or []),
                json.dumps(future_commitments or []),
                signature_name, signature_title,
                datetime.now().strftime('%Y-%m-%d'),
                created_by
            ))

            message_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] CEO mesajı oluşturuldu: {title} (ID: {message_id})")
            return message_id

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] CEO mesajı oluşturma hatası: {e}")
            raise
        finally:
            conn.close()

    def get_messages(self, company_id: int, message_type: str = None, year: int = None) -> List[Dict]:
        """CEO mesajlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT * FROM ceo_messages 
                WHERE company_id = ?
            """
            params = [company_id]

            if message_type:
                query += " AND message_type = ?"
                params.append(message_type)

            if year:
                query += " AND year = ?"
                params.append(year)

            query += " ORDER BY year DESC, quarter DESC, created_at DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            messages = []
            for row in results:
                messages.append({
                    'id': row[0], 'company_id': row[1], 'title': row[2], 'message_type': row[3],
                    'year': row[4], 'quarter': row[5], 'content': row[6], 'key_achievements': json.loads(row[7] or '[]'),
                    'challenges': json.loads(row[8] or '[]'), 'future_commitments': json.loads(row[9] or '[]'),
                    'signature_name': row[10], 'signature_title': row[11], 'signature_date': row[12],
                    'is_published': row[13], 'created_by': row[14], 'created_at': row[15], 'updated_at': row[16]
                })

            return messages

        except Exception as e:
            logging.error(f"[HATA] CEO mesajları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def update_message(self, message_id: int, **kwargs) -> bool:
        """CEO mesajını güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Güncellenebilir alanlar
            allowed_fields = ['title', 'content', 'key_achievements', 'challenges',
                            'future_commitments', 'signature_name', 'signature_title', 'is_published']

            update_fields = []
            params = []

            for field, value in kwargs.items():
                if field in allowed_fields:
                    if field in ['key_achievements', 'challenges', 'future_commitments']:
                        value = json.dumps(value) if isinstance(value, list) else value
                    update_fields.append(f"{field} = ?")
                    params.append(value)

            if not update_fields:
                return False

            update_fields.append("updated_at = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            params.append(message_id)

            cursor.execute(f"""
                UPDATE ceo_messages 
                SET {', '.join(update_fields)}
                WHERE id = ?
            """, params)

            conn.commit()

            if cursor.rowcount > 0:
                logging.info(f"[OK] CEO mesajı güncellendi: ID {message_id}")
                return True
            else:
                logging.info(f"[UYARI] CEO mesajı bulunamadı: ID {message_id}")
                return False

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] CEO mesajı güncelleme hatası: {e}")
            return False
        finally:
            conn.close()

    def create_default_templates(self) -> None:
        """Varsayılan mesaj şablonları oluştur"""
        templates = [
            {
                'name': 'Yıllık Sürdürülebilirlik Mesajı',
                'message_type': 'annual',
                'template_content': {
                    'greeting': 'Değerli Paydaşlarımız,',
                    'intro': '{year} yılı sürdürülebilirlik performansımız hakkında sizleri bilgilendirmekten mutluluk duyuyorum.',
                    'achievements_section': 'ANA BAŞARILARIMIZ',
                    'challenges_section': 'KARŞILAŞTIĞIMIZ ZORLUKLAR',
                    'commitments_section': 'GELECEK TAAHHÜTLERİMİZ',
                    'closing': 'Sürdürülebilir bir gelecek için birlikte çalışmaya devam edeceğiz.',
                    'signature': 'Saygılarımla,'
                },
                'variables': ['year', 'company_name', 'ceo_name', 'ceo_title']
            },
            {
                'name': 'Çeyreklik Performans Mesajı',
                'message_type': 'quarterly',
                'template_content': {
                    'greeting': 'Değerli Ekibimiz,',
                    'intro': '{year} yılının {quarter}. çeyreği performansımızı değerlendirme fırsatı buldum.',
                    'achievements_section': 'ÇEYREK BAŞARILARI',
                    'challenges_section': 'ZORLUKLAR VE ÇÖZÜMLER',
                    'commitments_section': 'SONRAKİ ÇEYREK HEDEFLERİ',
                    'closing': 'Birlikte daha güçlü bir gelecek inşa ediyoruz.',
                    'signature': 'Teşekkürler,'
                },
                'variables': ['year', 'quarter', 'company_name', 'ceo_name', 'ceo_title']
            },
            {
                'name': 'Acil Durum Mesajı',
                'message_type': 'emergency',
                'template_content': {
                    'greeting': 'Değerli Tüm Paydaşlarımız,',
                    'intro': '{situation_description} karşısında aldığımız önlemler ve pozisyonumuz.',
                    'achievements_section': 'ALINAN ÖNLEMLER',
                    'challenges_section': 'MEVCUT DURUM',
                    'commitments_section': 'GELECEK PLANLARI',
                    'closing': 'Güçlü ve dayanıklı bir şirket olarak bu zorluğu da aşacağız.',
                    'signature': 'Güvenle,'
                },
                'variables': ['situation_description', 'company_name', 'ceo_name', 'ceo_title']
            }
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for template in templates:
                # Mevcut şablonu kontrol et
                cursor.execute("""
                    SELECT id FROM message_templates 
                    WHERE name = ? AND message_type = ?
                """, (template['name'], template['message_type']))

                if cursor.fetchone():
                    continue  # Zaten mevcut

                cursor.execute("""
                    INSERT INTO message_templates 
                    (name, message_type, template_content, variables)
                    VALUES (?, ?, ?, ?)
                """, (
                    template['name'], template['message_type'],
                    json.dumps(template['template_content']),
                    json.dumps(template['variables'])
                ))

            conn.commit()
            logging.info(f"[OK] {len(templates)} mesaj şablonu oluşturuldu")

        except Exception as e:
            conn.rollback()
            logging.error(f"[HATA] Şablon oluşturma hatası: {e}")
        finally:
            conn.close()

    def get_templates(self, message_type: str = None) -> List[Dict]:
        """Mesaj şablonlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if message_type:
                cursor.execute("""
                    SELECT * FROM message_templates 
                    WHERE message_type = ? AND is_active = 1
                    ORDER BY name
                """, (message_type,))
            else:
                cursor.execute("""
                    SELECT * FROM message_templates 
                    WHERE is_active = 1
                    ORDER BY message_type, name
                """)

            results = cursor.fetchall()
            templates = []

            for row in results:
                templates.append({
                    'id': row[0], 'name': row[1], 'message_type': row[2],
                    'template_content': json.loads(row[3]), 'variables': json.loads(row[4] or '[]'),
                    'is_active': row[5], 'created_at': row[6]
                })

            return templates

        except Exception as e:
            logging.error(f"[HATA] Şablon getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def generate_message_from_template(self, template_id: int, variables: Dict[str, str]) -> str:
        """Şablondan mesaj oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT template_content, variables FROM message_templates 
                WHERE id = ? AND is_active = 1
            """, (template_id,))

            result = cursor.fetchone()
            if not result:
                raise ValueError("Şablon bulunamadı")

            template_content, required_variables = result
            template_content = json.loads(template_content)
            required_variables = json.loads(required_variables)

            # Eksik değişkenleri kontrol et
            missing_vars = [var for var in required_variables if var not in variables]
            if missing_vars:
                raise ValueError(f"Eksik değişkenler: {', '.join(missing_vars)}")

            # Mesajı oluştur
            message_parts = []

            if 'greeting' in template_content:
                message_parts.append(template_content['greeting'])
                message_parts.append("")

            if 'intro' in template_content:
                intro = template_content['intro']
                for var, value in variables.items():
                    intro = intro.replace(f'{{{var}}}', str(value))
                message_parts.append(intro)
                message_parts.append("")

            if 'achievements_section' in template_content:
                message_parts.append(f"## {template_content['achievements_section']}")
                message_parts.append("")
                # Burada key_achievements listesi eklenebilir

            if 'challenges_section' in template_content:
                message_parts.append(f"## {template_content['challenges_section']}")
                message_parts.append("")
                # Burada challenges listesi eklenebilir

            if 'commitments_section' in template_content:
                message_parts.append(f"## {template_content['commitments_section']}")
                message_parts.append("")
                # Burada future_commitments listesi eklenebilir

            if 'closing' in template_content:
                closing = template_content['closing']
                for var, value in variables.items():
                    closing = closing.replace(f'{{{var}}}', str(value))
                message_parts.append(closing)
                message_parts.append("")

            if 'signature' in template_content:
                message_parts.append(template_content['signature'])
                message_parts.append("")
                if 'ceo_name' in variables:
                    message_parts.append(variables['ceo_name'])
                if 'ceo_title' in variables:
                    message_parts.append(variables['ceo_title'])

            return '\n'.join(message_parts)

        except Exception as e:
            logging.error(f"[HATA] Mesaj oluşturma hatası: {e}")
            raise
        finally:
            conn.close()


if __name__ == "__main__":
    # Test
    manager = CEOMessageManager()
    manager.create_default_templates()

    # Test mesajı oluştur
    message_id = manager.create_message(
        company_id=1,
        title="2024 Yıllık Sürdürülebilirlik Mesajı",
        message_type="annual",
        year=2024,
        content="Sürdürülebilir bir gelecek için çalışmaya devam ediyoruz.",
        key_achievements=["%20 enerji tasarrufu", "Sıfır atık hedefine ulaştık"],
        challenges=["Tedarik zinciri sorunları", "İklim değişikliği etkileri"],
        future_commitments=["%100 yenilenebilir enerji", "Karbon nötr olma"],
        signature_name="Ahmet Yılmaz",
        signature_title="Genel Müdür",
        created_by=1
    )

    logging.info(f"Test mesajı oluşturuldu: ID {message_id}")

    # Mesajları listele
    messages = manager.get_messages(company_id=1)
    logging.info(f"Toplam {len(messages)} mesaj bulundu")
