#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Audit Trail and Role-Based Authorization - Sprint 5
Denetim izi ve rol bazlı yetkilendirme sistemi
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from config.database import DB_PATH


class UserRole(Enum):
    """Kullanıcı rolleri"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    AUDITOR = "auditor"

class ActionType(Enum):
    """Eylem türleri"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"

class GRIAuditTrail:
    """GRI denetim izi sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.create_audit_tables()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_audit_tables(self) -> None:
        """Denetim tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Kullanıcı rolleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_user_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Denetim izi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT,
                    action_type TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                )
            """)

            # Yetki matrisi tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    allowed BOOLEAN DEFAULT 1,
                    conditions TEXT
                )
            """)

            # Varsayılan yetkileri oluştur
            self.create_default_permissions(cursor)

            conn.commit()
            logging.info("Denetim tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"Denetim tabloları oluşturulurken hata: {e}")
            conn.rollback()
        finally:
            conn.close()

    def create_default_permissions(self, cursor) -> None:
        """Varsayılan yetkileri oluştur"""
        permissions = [
            # Admin yetkileri
            ("admin", "gri_standards", "create", True, None),
            ("admin", "gri_standards", "update", True, None),
            ("admin", "gri_standards", "delete", True, None),
            ("admin", "gri_indicators", "create", True, None),
            ("admin", "gri_indicators", "update", True, None),
            ("admin", "gri_indicators", "delete", True, None),
            ("admin", "gri_responses", "create", True, None),
            ("admin", "gri_responses", "update", True, None),
            ("admin", "gri_responses", "delete", True, None),
            ("admin", "gri_reports", "export", True, None),

            # Manager yetkileri
            ("manager", "gri_standards", "view", True, None),
            ("manager", "gri_indicators", "view", True, None),
            ("manager", "gri_indicators", "update", True, None),
            ("manager", "gri_responses", "create", True, None),
            ("manager", "gri_responses", "update", True, None),
            ("manager", "gri_reports", "export", True, None),
            ("manager", "gri_reports", "approve", True, None),

            # Analyst yetkileri
            ("analyst", "gri_standards", "view", True, None),
            ("analyst", "gri_indicators", "view", True, None),
            ("analyst", "gri_responses", "create", True, None),
            ("analyst", "gri_responses", "update", True, "company_id = user_company"),
            ("analyst", "gri_reports", "export", True, "company_id = user_company"),

            # Viewer yetkileri
            ("viewer", "gri_standards", "view", True, None),
            ("viewer", "gri_indicators", "view", True, None),
            ("viewer", "gri_responses", "view", True, "company_id = user_company"),

            # Auditor yetkileri
            ("auditor", "gri_standards", "view", True, None),
            ("auditor", "gri_indicators", "view", True, None),
            ("auditor", "gri_responses", "view", True, None),
            ("auditor", "gri_audit_log", "view", True, None),
            ("auditor", "gri_reports", "export", True, None),
        ]

        for role, resource, action, allowed, conditions in permissions:
            cursor.execute("""
                INSERT OR IGNORE INTO gri_permissions (role, resource, action, allowed, conditions)
                VALUES (?, ?, ?, ?, ?)
            """, (role, resource, action, allowed, conditions))

    def log_action(self, user_id: int, user_name: str, action_type: ActionType,
                   table_name: str, record_id: Optional[int] = None,
                   old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                   ip_address: str = None, user_agent: str = None, session_id: str = None):
        """Eylem kaydı oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO gri_audit_log 
                (user_id, user_name, action_type, table_name, record_id, old_values, new_values, 
                 ip_address, user_agent, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_name, action_type.value, table_name, record_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                ip_address, user_agent, session_id
            ))

            conn.commit()
            return cursor.lastrowid

        except Exception as e:
            logging.error(f"Denetim kaydı oluşturulurken hata: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def assign_user_role(self, user_id: int, role: UserRole, permissions: Optional[List[str]] = None) -> None:
        """Kullanıcıya rol ata"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO gri_user_roles (user_id, role, permissions, updated_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, role.value, json.dumps(permissions) if permissions else None,
                  datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Kullanıcı rolü atanırken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def check_permission(self, user_id: int, resource: str, action: str,
                        company_id: Optional[int] = None) -> bool:
        """Kullanıcı yetkisini kontrol et"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Kullanıcının rolünü al
            cursor.execute("""
                SELECT role FROM gri_user_roles WHERE user_id = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (user_id,))

            role_result = cursor.fetchone()
            if not role_result:
                return False

            user_role = role_result[0]

            # Yetkiyi kontrol et
            cursor.execute("""
                SELECT allowed, conditions FROM gri_permissions 
                WHERE role = ? AND resource = ? AND action = ?
            """, (user_role, resource, action))

            permission_result = cursor.fetchone()
            if not permission_result:
                return False

            allowed, conditions = permission_result

            if not allowed:
                return False

            # Koşullu yetki kontrolü
            if conditions and company_id:
                # Basit koşul kontrolü (gerçek uygulamada daha karmaşık olabilir)
                if "company_id = user_company" in conditions:
                    # Bu durumda kullanıcının şirket ID'sini kontrol etmek gerekir
                    # Şimdilik True döndürüyoruz
                    pass

            return True

        except Exception as e:
            logging.error(f"Yetki kontrolü yapılırken hata: {e}")
            return False
        finally:
            conn.close()

    def get_audit_log(self, user_id: Optional[int] = None, table_name: Optional[str] = None,
                      action_type: Optional[str] = None, start_date: Optional[str] = None,
                      end_date: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Denetim kayıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, user_id, user_name, action_type, table_name, record_id,
                       old_values, new_values, ip_address, user_agent, timestamp, session_id
                FROM gri_audit_log
                WHERE 1=1
            """
            params = []

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if table_name:
                query += " AND table_name = ?"
                params.append(table_name)

            if action_type:
                query += " AND action_type = ?"
                params.append(action_type)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'user_id': row[1],
                    'user_name': row[2],
                    'action_type': row[3],
                    'table_name': row[4],
                    'record_id': row[5],
                    'old_values': json.loads(row[6]) if row[6] else None,
                    'new_values': json.loads(row[7]) if row[7] else None,
                    'ip_address': row[8],
                    'user_agent': row[9],
                    'timestamp': row[10],
                    'session_id': row[11]
                })

            return results

        except Exception as e:
            logging.error(f"Denetim kayıtları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict:
        """Kullanıcı aktivite özetini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam eylem sayısı
            cursor.execute("""
                SELECT COUNT(*) FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
            """.format(days), (user_id,))
            total_actions = cursor.fetchone()[0]

            # Eylem türüne göre dağılım
            cursor.execute("""
                SELECT action_type, COUNT(*) FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY action_type
            """.format(days), (user_id,))
            action_distribution = dict(cursor.fetchall())

            # Tablo bazında dağılım
            cursor.execute("""
                SELECT table_name, COUNT(*) FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY table_name
            """.format(days), (user_id,))
            table_distribution = dict(cursor.fetchall())

            # Son aktivite
            cursor.execute("""
                SELECT timestamp FROM gri_audit_log 
                WHERE user_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,))
            last_activity = cursor.fetchone()
            last_activity = last_activity[0] if last_activity else None

            return {
                'user_id': user_id,
                'period_days': days,
                'total_actions': total_actions,
                'action_distribution': action_distribution,
                'table_distribution': table_distribution,
                'last_activity': last_activity
            }

        except Exception as e:
            logging.error(f"Kullanıcı aktivite özeti getirilirken hata: {e}")
            return {}
        finally:
            conn.close()

def create_audit_trail() -> None:
    """Denetim izi sistemini oluştur"""
    audit_trail = GRIAuditTrail()

    # Varsayılan kullanıcı rolleri oluştur
    audit_trail.assign_user_role(1, UserRole.ADMIN)
    audit_trail.assign_user_role(2, UserRole.MANAGER)
    audit_trail.assign_user_role(3, UserRole.ANALYST)
    audit_trail.assign_user_role(4, UserRole.VIEWER)
    audit_trail.assign_user_role(5, UserRole.AUDITOR)

    logging.info("Denetim izi sistemi başarıyla oluşturuldu")

if __name__ == "__main__":
    create_audit_trail()
