#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versiyon Kontrol Yönetimi Modülü
Veri versiyonlama ve değişiklik takibi
"""

import logging
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class VersionControlManager:
    """Veri versiyonlama ve değişiklik takibi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Versiyon kontrol tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
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
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    version_id INTEGER NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    change_type TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (version_id) REFERENCES data_versions(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Versiyon kontrol yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Versiyon kontrol yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def create_data_version(self, company_id: int, version_number: str,
                          version_date: str, version_type: str, data_category: str,
                          change_description: str = None, changed_by: str = None) -> int:
        """Veri versiyonu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_versions 
                (company_id, version_number, version_date, version_type, data_category,
                 change_description, changed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, version_number, version_date, version_type, data_category,
                  change_description, changed_by))

            version_id = cursor.lastrowid
            conn.commit()
            return version_id

        except Exception as e:
            logging.error(f"Veri versiyonu oluşturma hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def add_data_change(self, company_id: int, version_id: int, table_name: str,
                       change_type: str, old_value: str = None, new_value: str = None,
                       record_id: int = None, change_reason: str = None) -> bool:
        """Veri değişikliği ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_changes 
                (company_id, version_id, table_name, record_id, change_type,
                 old_value, new_value, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, version_id, table_name, record_id, change_type,
                  old_value, new_value, change_reason))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri değişikliği ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_version_history(self, company_id: int, data_category: str = None) -> List[Dict]:
        """Versiyon geçmişi getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if data_category:
                cursor.execute("""
                    SELECT id, version_number, version_date, version_type, data_category,
                           change_description, changed_by, approval_status
                    FROM data_versions 
                    WHERE company_id = ? AND data_category = ?
                    ORDER BY version_date DESC
                """, (company_id, data_category))
            else:
                cursor.execute("""
                    SELECT id, version_number, version_date, version_type, data_category,
                           change_description, changed_by, approval_status
                    FROM data_versions 
                    WHERE company_id = ?
                    ORDER BY version_date DESC
                """, (company_id,))

            versions = []
            for row in cursor.fetchall():
                versions.append({
                    'id': row[0],
                    'version_number': row[1],
                    'version_date': row[2],
                    'version_type': row[3],
                    'data_category': row[4],
                    'change_description': row[5],
                    'changed_by': row[6],
                    'approval_status': row[7]
                })

            return versions

        except Exception as e:
            logging.error(f"Versiyon geçmişi getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_version_changes(self, company_id: int, version_id: int) -> List[Dict]:
        """Versiyon değişikliklerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT table_name, record_id, change_type, old_value, new_value, change_reason
                FROM data_changes 
                WHERE company_id = ? AND version_id = ?
                ORDER BY table_name, record_id
            """, (company_id, version_id))

            changes = []
            for row in cursor.fetchall():
                changes.append({
                    'table_name': row[0],
                    'record_id': row[1],
                    'change_type': row[2],
                    'old_value': row[3],
                    'new_value': row[4],
                    'change_reason': row[5]
                })

            return changes

        except Exception as e:
            logging.error(f"Versiyon değişiklikleri getirme hatası: {e}")
            return []
        finally:
            conn.close()
