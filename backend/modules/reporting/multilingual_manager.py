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

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

class MultilingualManager(BaseTenantManager):
    """Çok dilli raporlama ve çeviri yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_db_tables()
        self._init_default_translations()

    def _init_db_tables(self) -> None:
        """Çok dilli modülü tablolarını oluştur"""
        try:
            self.execute_update("""
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
            """, skip_tenant_filter=True)

            self.execute_update("""
                CREATE TABLE IF NOT EXISTS supported_languages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language_code TEXT UNIQUE NOT NULL,
                    language_name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_default BOOLEAN DEFAULT 0
                )
            """, skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Çok dilli modül tabloları oluşturulamadı: {e}")

    def _init_default_translations(self) -> None:
        """Varsayılan dilleri ekle"""
        try:
            # Check if languages exist
            count = self.execute_query("SELECT COUNT(*) as count FROM supported_languages", skip_tenant_filter=True)
            if count and count[0]['count'] == 0:
                self.execute_update("""
                    INSERT INTO supported_languages (language_code, language_name, is_default)
                    VALUES 
                    ('tr', 'Türkçe', 1),
                    ('en', 'English', 0),
                    ('de', 'Deutsch', 0),
                    ('fr', 'Français', 0)
                """, skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"Varsayılan diller eklenemedi: {e}")
