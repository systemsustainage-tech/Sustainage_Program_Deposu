#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSO (Single Sign-On) Yönetimi Modülü
Tek oturum açma ve kimlik doğrulama
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict
from config.database import DB_PATH


class SSOManager:
    """SSO yönetimi ve kimlik doğrulama"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """SSO yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sso_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    provider_name TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    client_id TEXT,
                    client_secret TEXT,
                    redirect_uri TEXT,
                    scope TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sso_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    session_token TEXT NOT NULL,
                    provider_name TEXT NOT NULL,
                    external_user_id TEXT,
                    expires_at TEXT NOT NULL,
                    last_activity TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sso_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    user_id INTEGER,
                    provider_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    success TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    error_message TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] SSO yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] SSO yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_sso_provider(self, company_id: int, provider_name: str, provider_type: str,
                        client_id: str = None, client_secret: str = None,
                        redirect_uri: str = None, scope: str = None) -> bool:
        """SSO sağlayıcısı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sso_providers 
                (company_id, provider_name, provider_type, client_id, client_secret,
                 redirect_uri, scope)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, provider_name, provider_type, client_id, client_secret,
                  redirect_uri, scope))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"SSO sağlayıcısı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_sso_session(self, company_id: int, user_id: int, provider_name: str,
                          external_user_id: str, expires_at: str) -> str:
        """SSO oturumu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Session token oluştur
            session_token = f"sso_{company_id}_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cursor.execute("""
                INSERT INTO sso_sessions 
                (company_id, user_id, session_token, provider_name, external_user_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, user_id, session_token, provider_name, external_user_id, expires_at))

            conn.commit()
            return session_token

        except Exception as e:
            logging.error(f"SSO oturumu oluşturma hatası: {e}")
            conn.rollback()
            return ""
        finally:
            conn.close()

    def log_sso_action(self, company_id: int, user_id: int, provider_name: str,
                      action_type: str, success: bool, ip_address: str = None,
                      user_agent: str = None, error_message: str = None) -> bool:
        """SSO aksiyonu logla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO sso_logs 
                (company_id, user_id, provider_name, action_type, success, ip_address,
                 user_agent, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, user_id, provider_name, action_type, str(success).lower(),
                  ip_address, user_agent, error_message, timestamp))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"SSO aksiyon loglama hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_sso_summary(self, company_id: int) -> Dict:
        """SSO özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # SSO sağlayıcıları
            cursor.execute("""
                SELECT provider_name, provider_type, status
                FROM sso_providers 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            providers = []
            for row in cursor.fetchall():
                providers.append({
                    'provider_name': row[0],
                    'provider_type': row[1],
                    'status': row[2]
                })

            # Aktif oturumlar
            cursor.execute("""
                SELECT provider_name, COUNT(*)
                FROM sso_sessions 
                WHERE company_id = ? AND status = 'active' AND expires_at > datetime('now')
                GROUP BY provider_name
            """, (company_id,))

            active_sessions = {}
            total_active_sessions = 0
            for row in cursor.fetchall():
                provider_name, count = row
                active_sessions[provider_name] = count
                total_active_sessions += count

            # SSO logları (son 30 gün)
            cursor.execute("""
                SELECT provider_name, action_type, 
                       SUM(CASE WHEN success = 'true' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN success = 'false' THEN 1 ELSE 0 END)
                FROM sso_logs 
                WHERE company_id = ? AND timestamp >= datetime('now', '-30 days')
                GROUP BY provider_name, action_type
            """, (company_id,))

            sso_activity = {}
            for row in cursor.fetchall():
                provider_name, action_type, success_count, failure_count = row
                if provider_name not in sso_activity:
                    sso_activity[provider_name] = {}
                sso_activity[provider_name][action_type] = {
                    'successful': success_count,
                    'failed': failure_count
                }

            return {
                'providers': providers,
                'active_sessions': active_sessions,
                'total_active_sessions': total_active_sessions,
                'sso_activity_30d': sso_activity,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"SSO özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()
