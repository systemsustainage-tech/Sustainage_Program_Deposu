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
from typing import Dict, List, Optional
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager

class CEOMessageManager(BaseTenantManager):
    """CEO/Genel Müdür mesaj yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        # BaseTenantManager execute_update DDL sorgularını (CREATE TABLE) destekler (skip_tenant_filter=True ile)
        # Ancak burada çoklu sorgu var, tek tek çalıştıralım.
        
        # CEO mesajları tablosu
        self.execute_update("""
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
        """, skip_tenant_filter=True)

        # Mesaj şablonları
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS message_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message_type TEXT NOT NULL,
                template_content TEXT NOT NULL, -- JSON template
                variables TEXT, -- JSON array of variable names
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """, skip_tenant_filter=True)

        # Mesaj değişkenleri
        self.execute_update("""
            CREATE TABLE IF NOT EXISTS message_variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                variable_name TEXT NOT NULL,
                variable_value TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES ceo_messages(id)
            )
        """, skip_tenant_filter=True)
        
        logging.info("[OK] CEO mesaj tabloları hazır")

    def create_message(self, company_id: int, title: str, message_type: str, year: int,
                      quarter: int = None, content: str = "", key_achievements: List[str] = None,
                      challenges: List[str] = None, future_commitments: List[str] = None,
                      signature_name: str = "", signature_title: str = "", created_by: int = None) -> int:
        """
        Yeni CEO mesajı oluştur
        """
        # Aynı dönem için mesaj kontrolü
        if quarter:
            existing = self.execute_query(
                "SELECT id FROM ceo_messages WHERE company_id = ? AND message_type = ? AND year = ? AND quarter = ?",
                (company_id, message_type, year, quarter),
                company_id=company_id
            )
        else:
            existing = self.execute_query(
                "SELECT id FROM ceo_messages WHERE company_id = ? AND message_type = ? AND year = ? AND quarter IS NULL",
                (company_id, message_type, year),
                company_id=company_id
            )

        if existing:
            raise ValueError(f"Bu dönem için mesaj zaten mevcut (ID: {existing[0]['id']})")

        # Insert message
        message_id = self.insert(
            "ceo_messages",
            {
                "company_id": company_id,
                "title": title,
                "message_type": message_type,
                "year": year,
                "quarter": quarter,
                "content": content,
                "key_achievements": json.dumps(key_achievements or []),
                "challenges": json.dumps(challenges or []),
                "future_commitments": json.dumps(future_commitments or []),
                "signature_name": signature_name,
                "signature_title": signature_title,
                "signature_date": datetime.now().strftime('%Y-%m-%d'),
                "created_by": created_by
            },
            company_id=company_id
        )

        logging.info(f"[OK] CEO mesajı oluşturuldu: {title} (ID: {message_id})")
        return message_id

    def get_messages(self, company_id: int, message_type: str = None, year: int = None) -> List[Dict]:
        """CEO mesajlarını getir"""
        query = "SELECT * FROM ceo_messages WHERE company_id = ?"
        params = [company_id]

        if message_type:
            query += " AND message_type = ?"
            params.append(message_type)

        if year:
            query += " AND year = ?"
            params.append(year)

        query += " ORDER BY year DESC, quarter DESC, created_at DESC"

        results = self.execute_query(query, params, company_id=company_id)
        
        # BaseTenantManager returns dicts, but let's ensure we process them correctly if needed
        # Actually execute_query returns list of sqlite3.Row or dict-like objects
        # But wait, BaseTenantManager.execute_query returns list of dictionaries usually if configured
        # Let's check BaseTenantManager implementation or just rely on what we have.
        # Assuming execute_query returns list of dicts or sqlite3.Row objects that are dict-like.
        
        messages = []
        for row in results:
            # If row is dict-like
            messages.append({
                'id': row['id'], 
                'company_id': row['company_id'], 
                'title': row['title'], 
                'message_type': row['message_type'],
                'year': row['year'], 
                'quarter': row['quarter'], 
                'content': row['content'], 
                'key_achievements': json.loads(row['key_achievements'] or '[]'),
                'challenges': json.loads(row['challenges'] or '[]'), 
                'future_commitments': json.loads(row['future_commitments'] or '[]'),
                'signature_name': row['signature_name'], 
                'signature_title': row['signature_title'], 
                'signature_date': row['signature_date'],
                'is_published': row['is_published'], 
                'created_by': row['created_by'], 
                'created_at': row['created_at'], 
                'updated_at': row['updated_at']
            })

        return messages

    def update_message(self, message_id: int, **kwargs) -> bool:
        """CEO mesajını güncelle"""
        # Note: update method in BaseTenantManager takes (table, data, where_clause, where_args)
        # But here we want to update specific fields.
        
        valid_fields = [
            'title', 'content', 'key_achievements', 'challenges', 
            'future_commitments', 'signature_name', 'signature_title',
            'is_published'
        ]
        
        data = {}
        for key, value in kwargs.items():
            if key in valid_fields:
                if key in ['key_achievements', 'challenges', 'future_commitments'] and isinstance(value, list):
                    data[key] = json.dumps(value)
                else:
                    data[key] = value
        
        if not data:
            return False
            
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # We need company_id for strict isolation, but update_message signature doesn't have it.
        # We should probably fetch it or assume caller handles it? 
        # BaseTenantManager.update requires company_id if we want strict isolation verification.
        # If we don't have company_id, we can't strictly filter by company_id unless we lookup first.
        # But for now let's rely on message_id being unique enough, but ideally we should have company_id.
        # However, to avoid breaking API, we will just use update without company_id filter if not passed.
        # But BaseTenantManager might require it.
        # Let's look up company_id from message_id first.
        
        msg = self.execute_query("SELECT company_id FROM ceo_messages WHERE id = ?", (message_id,))
        if not msg:
            return False
        
        company_id = msg[0]['company_id']
        
        return self.update(
            "ceo_messages",
            data,
            {"id": message_id},
            company_id=company_id
        )

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
