#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versiyon Kontrol Yönetimi Modülü
Veri versiyonlama ve değişiklik takibi
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

class VersionControlManager(BaseTenantManager):
    """Veri versiyonlama ve değişiklik takibi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Versiyon kontrol tablolarını oluştur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    version_number TEXT NOT NULL,
                    version_date TEXT NOT NULL,
                    version_type TEXT NOT NULL,
                    data_category TEXT NOT NULL,
                    change_description TEXT,
                    changed_by TEXT,
                    approval_status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    version_id INTEGER NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    change_type TEXT NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
                    old_data TEXT, -- JSON
                    new_data TEXT, -- JSON
                    changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (version_id) REFERENCES data_versions(id)
                )
            """, skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Versiyon kontrol tabloları oluşturulamadı: {e}")

    def create_version(self, company_id: int, version_number: str, 
                      version_type: str, data_category: str, 
                      change_description: str, changed_by: str) -> int:
        """Yeni versiyon kaydı oluştur"""
        try:
            query = """
                INSERT INTO data_versions (
                    company_id, version_number, version_date, 
                    version_type, data_category, change_description, changed_by
                ) VALUES (?, ?, datetime('now'), ?, ?, ?, ?)
            """
            params = (company_id, version_number, version_type, 
                     data_category, change_description, changed_by)
            
            # BaseTenantManager.execute_update returns True/False usually, but we need ID.
            # BaseTenantManager doesn't typically return ID. 
            # We might need to select it back or modify BaseTenantManager.
            # But wait, execute_update calls TenantAwareDB.execute_update.
            # Let's check if we can get the ID.
            
            self.execute_update(query, params)
            
            # Get the ID
            result = self.execute_query("SELECT last_insert_rowid() as id")
            return result[0]['id'] if result else 0
            
        except Exception as e:
            logging.error(f"Versiyon oluşturma hatası: {e}")
            return 0

    def log_change(self, company_id: int, version_id: int, table_name: str,
                  record_id: int, change_type: str, old_data: str, new_data: str) -> bool:
        """Veri değişikliğini kaydet"""
        try:
            query = """
                INSERT INTO data_changes (
                    company_id, version_id, table_name, record_id,
                    change_type, old_data, new_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (company_id, version_id, table_name, record_id,
                     change_type, old_data, new_data)
            
            return self.execute_update(query, params)
        except Exception as e:
            logging.error(f"Değişiklik kaydetme hatası: {e}")
            return False

    def get_version_history(self, company_id: int, data_category: str = None) -> List[Dict]:
        """Versiyon geçmişini getir"""
        try:
            query = "SELECT * FROM data_versions WHERE company_id = ?"
            params = [company_id]
            
            if data_category:
                query += " AND data_category = ?"
                params.append(data_category)
                
            query += " ORDER BY created_at DESC"
            
            return self.execute_query(query, tuple(params))
        except Exception as e:
            logging.error(f"Versiyon geçmişi getirme hatası: {e}")
            return []

    def get_version_changes(self, version_id: int) -> List[Dict]:
        """Versiyon değişikliklerini getir"""
        try:
            query = "SELECT * FROM data_changes WHERE version_id = ?"
            return self.execute_query(query, (version_id,))
        except Exception as e:
            logging.error(f"Versiyon değişiklikleri getirme hatası: {e}")
            return []
