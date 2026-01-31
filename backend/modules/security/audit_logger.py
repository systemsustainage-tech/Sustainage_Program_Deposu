#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Log Modülü
Sistem aktiviteleri ve kullanıcı işlemleri loglama
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class AuditLogger:
    """Audit log yönetimi ve güvenlik takibi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Audit log tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    user_id INTEGER,
                    username TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id INTEGER,
                    details TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success TEXT DEFAULT 'true',
                    error_message TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    severity_level TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    source_ip TEXT,
                    affected_user TEXT,
                    resolution_status TEXT DEFAULT 'open',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Audit log modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Audit log modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def log_action(self, company_id: int, user_id: int, username: str, action_type: str,
                  resource_type: str, action_description: str, resource_id: int = None,
                  ip_address: str = None, user_agent: str = None, success: bool = True,
                  error_message: str = None) -> bool:
        """Aksiyon logla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO audit_logs 
                (company_id, user_id, username, action, resource_type, resource_id,
                 details, ip_address, user_agent, success, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, user_id, username, action_type, resource_type, resource_id,
                  action_description, ip_address, user_agent, str(success).lower(), error_message, timestamp))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Audit log ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def log_security_event(self, company_id: int, event_type: str, severity_level: str,
                          event_description: str, source_ip: str = None,
                          affected_user: str = None) -> bool:
        """Güvenlik olayı logla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO security_events 
                (company_id, event_type, severity_level, event_description, source_ip, affected_user)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, event_type, severity_level, event_description, source_ip, affected_user))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Güvenlik olayı loglama hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_audit_logs(self, company_id: int, start_date: str = None, end_date: str = None,
                      action_type: str = None, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Audit logları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, user_id, username, action, resource_type, resource_id,
                       details, ip_address, success, error_message, timestamp
                FROM audit_logs 
                WHERE company_id = ?
            """
            params = [company_id]

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            if action_type:
                query += " AND action = ?"
                params.append(action_type)

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'id': row[0],
                    'user_id': row[1],
                    'username': row[2],
                    'action_type': row[3],
                    'resource_type': row[4],
                    'resource_id': row[5],
                    'action_description': row[6],
                    'ip_address': row[7],
                    'success': row[8] == 'true',
                    'error_message': row[9],
                    'timestamp': row[10]
                })

            return logs

        except Exception as e:
            logging.error(f"Audit logları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_security_events(self, company_id: int, severity_level: str = None,
                           resolution_status: str = None, limit: int = 100) -> List[Dict]:
        """Güvenlik olaylarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, event_type, severity_level, event_description, source_ip,
                       affected_user, resolution_status, created_at
                FROM security_events 
                WHERE company_id = ?
            """
            params = [company_id]

            if severity_level:
                query += " AND severity_level = ?"
                params.append(severity_level)

            if resolution_status:
                query += " AND resolution_status = ?"
                params.append(resolution_status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'event_type': row[1],
                    'severity_level': row[2],
                    'event_description': row[3],
                    'source_ip': row[4],
                    'affected_user': row[5],
                    'resolution_status': row[6],
                    'created_at': row[7]
                })

            return events

        except Exception as e:
            logging.error(f"Güvenlik olayları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def generate_audit_report(self, company_id: int, start_date: str, end_date: str) -> Dict:
        """Audit raporu oluştur"""
        logs = self.get_audit_logs(company_id, start_date, end_date, limit=1000)
        events = self.get_security_events(company_id, limit=100)

        # İstatistikler
        total_actions = len(logs)
        successful_actions = len([log for log in logs if log['success']])
        failed_actions = total_actions - successful_actions

        # Kullanıcı aktiviteleri
        user_activities = {}
        for log in logs:
            user = log['username'] or f"User_{log['user_id']}"
            if user not in user_activities:
                user_activities[user] = 0
            user_activities[user] += 1

        # Aksiyon türleri
        action_types = {}
        for log in logs:
            action_type = log['action_type']
            if action_type not in action_types:
                action_types[action_type] = 0
            action_types[action_type] += 1

        # Güvenlik olayları
        security_events_by_severity = {}
        for event in events:
            severity = event['severity_level']
            if severity not in security_events_by_severity:
                security_events_by_severity[severity] = 0
            security_events_by_severity[severity] += 1

        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_actions': total_actions,
                'successful_actions': successful_actions,
                'failed_actions': failed_actions,
                'success_rate': (successful_actions / total_actions * 100) if total_actions > 0 else 0,
                'security_events': len(events)
            },
            'user_activities': user_activities,
            'action_types': action_types,
            'security_events_by_severity': security_events_by_severity,
            'recent_logs': logs[:10],  # Son 10 log
            'recent_security_events': events[:10]  # Son 10 güvenlik olayı
        }
