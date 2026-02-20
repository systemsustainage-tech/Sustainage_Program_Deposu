#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Audit Trail and Role-Based Authorization - Sprint 5
Denetim izi ve rol bazlı yetkilendirme sistemi
"""

import logging
import json
import os
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

from backend.core.base_manager import BaseTenantManager

class GRIAuditTrail(BaseTenantManager):
    """GRI denetim izi sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        super().__init__(db_path)
        self.create_audit_tables()

    def create_audit_tables(self) -> None:
        """Denetim tablolarını oluştur"""
        try:
            # Kullanıcı rolleri tablosu
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.create_default_permissions()

            logging.info("Denetim tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"Denetim tabloları oluşturulurken hata: {e}")

    def create_default_permissions(self) -> None:
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
            self.execute_update("""
                INSERT OR IGNORE INTO gri_permissions (role, resource, action, allowed, conditions)
                VALUES (?, ?, ?, ?, ?)
            """, (role, resource, action, allowed, conditions))

    def log_action(self, user_id: int, user_name: str, action_type: ActionType,
                   table_name: str, record_id: Optional[int] = None,
                   old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
                   ip_address: str = None, user_agent: str = None, session_id: str = None):
        """Eylem kaydı oluştur"""
        try:
            # skip_tenant_filter=True çünkü gri_audit_log global bir tablo
            self.execute_update("""
                INSERT INTO gri_audit_log 
                (user_id, user_name, action_type, table_name, record_id, old_values, new_values, 
                 ip_address, user_agent, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_name, action_type.value, table_name, record_id,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                ip_address, user_agent, session_id
            ), skip_tenant_filter=True)

            # Last inserted ID'yi almak zor olabilir, şimdilik dönmüyoruz veya ayrı bir sorgu ile alabiliriz
            # execute_update etkilenen satır sayısını döner
            return True

        except Exception as e:
            logging.error(f"Denetim kaydı oluşturulurken hata: {e}")
            return None

    def assign_user_role(self, user_id: int, role: UserRole, permissions: Optional[List[str]] = None) -> None:
        """Kullanıcıya rol ata"""
        try:
            # skip_tenant_filter=True çünkü gri_user_roles global bir tablo
            self.execute_update("""
                INSERT OR REPLACE INTO gri_user_roles (user_id, role, permissions, updated_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, role.value, json.dumps(permissions) if permissions else None,
                  datetime.now().isoformat()), skip_tenant_filter=True)
            return True

        except Exception as e:
            logging.error(f"Kullanıcı rolü atanırken hata: {e}")
            return False

    def check_permission(self, user_id: int, resource: str, action: str,
                        company_id: Optional[int] = None) -> bool:
        """Kullanıcı yetkisini kontrol et"""
        try:
            # Kullanıcının rolünü al - skip_tenant_filter=True
            role_result = self.execute_query("""
                SELECT role FROM gri_user_roles WHERE user_id = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (user_id,), skip_tenant_filter=True)

            if not role_result:
                return False

            user_role = role_result[0]['role']

            # Yetkiyi kontrol et - skip_tenant_filter=True
            permission_result = self.execute_query("""
                SELECT allowed, conditions FROM gri_permissions 
                WHERE role = ? AND resource = ? AND action = ?
            """, (user_role, resource, action), skip_tenant_filter=True)

            if not permission_result:
                return False

            allowed = permission_result[0]['allowed']
            conditions = permission_result[0]['conditions']

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

    def get_audit_log(self, user_id: Optional[int] = None, table_name: Optional[str] = None,
                      action_type: Optional[str] = None, start_date: Optional[str] = None,
                      end_date: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Denetim kayıtlarını getir"""
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

            # skip_tenant_filter=True çünkü gri_audit_log global bir tablo
            rows = self.execute_query(query, tuple(params), skip_tenant_filter=True)

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'user_id': row['user_id'],
                    'user_name': row['user_name'],
                    'action_type': row['action_type'],
                    'table_name': row['table_name'],
                    'record_id': row['record_id'],
                    'old_values': json.loads(row['old_values']) if row['old_values'] else None,
                    'new_values': json.loads(row['new_values']) if row['new_values'] else None,
                    'ip_address': row['ip_address'],
                    'user_agent': row['user_agent'],
                    'timestamp': row['timestamp'],
                    'session_id': row['session_id']
                })

            return results

        except Exception as e:
            logging.error(f"Denetim kayıtları getirilirken hata: {e}")
            return []

    def get_user_activity_summary(self, user_id: int, days: int = 30) -> Dict:
        """Kullanıcı aktivite özetini getir"""
        try:
            # Toplam eylem sayısı
            # skip_tenant_filter=True
            total_actions_result = self.execute_query("""
                SELECT COUNT(*) as count FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
            """.format(days), (user_id,), skip_tenant_filter=True)
            total_actions = total_actions_result[0]['count'] if total_actions_result else 0

            # Eylem türüne göre dağılım
            action_dist_result = self.execute_query("""
                SELECT action_type, COUNT(*) as count FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY action_type
            """.format(days), (user_id,), skip_tenant_filter=True)
            action_distribution = {row['action_type']: row['count'] for row in action_dist_result}

            # Tablo bazında dağılım
            table_dist_result = self.execute_query("""
                SELECT table_name, COUNT(*) as count FROM gri_audit_log 
                WHERE user_id = ? AND timestamp >= date('now', '-{} days')
                GROUP BY table_name
            """.format(days), (user_id,), skip_tenant_filter=True)
            table_distribution = {row['table_name']: row['count'] for row in table_dist_result}

            # Son aktivite
            last_activity_result = self.execute_query("""
                SELECT timestamp FROM gri_audit_log 
                WHERE user_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (user_id,), skip_tenant_filter=True)
            last_activity = last_activity_result[0]['timestamp'] if last_activity_result else None

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
