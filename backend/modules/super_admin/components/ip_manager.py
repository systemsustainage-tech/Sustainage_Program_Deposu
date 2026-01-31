#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Manager Component
Whitelist and Blacklist management
"""

import ipaddress
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from config.database import DB_PATH


class IPManager:
    """IP whitelist and blacklist manager"""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def add_to_whitelist(
        self,
        ip_address: str,
        description: str,
        added_by: str
    ) -> Dict[str, Any]:
        """Add IP to whitelist"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ip_whitelist (ip_address, description, added_by, is_active)
                VALUES (?, ?, ?, 1)
            """, (ip_address, description, added_by))

            conn.commit()
            conn.close()

            return {'success': True, 'message': f'IP {ip_address} added to whitelist'}
        except ValueError:
            return {'success': False, 'message': 'Invalid IP address format'}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'IP already in whitelist'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def add_to_blacklist(
        self,
        ip_address: str,
        reason: str,
        blocked_by: str,
        block_type: str = 'manual',
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add IP to blacklist"""
        try:
            # Validate IP address
            ipaddress.ip_address(ip_address)

            expires_at = None
            if duration_minutes:
                expires_at = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ip_blacklist (ip_address, reason, blocked_by, block_type, expires_at, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (ip_address, reason, blocked_by, block_type, expires_at))

            conn.commit()
            conn.close()

            return {'success': True, 'message': f'IP {ip_address} blacklisted'}
        except ValueError:
            return {'success': False, 'message': 'Invalid IP address format'}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'IP already blacklisted'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def remove_from_whitelist(self, ip_address: str) -> bool:
        """Remove IP from whitelist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ip_whitelist WHERE ip_address = ?", (ip_address,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def remove_from_blacklist(self, ip_address: str) -> bool:
        """Remove IP from blacklist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ip_blacklist WHERE ip_address = ?", (ip_address,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def is_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ip_whitelist 
                WHERE ip_address = ? AND is_active = 1
            """, (ip_address,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False

    def is_blacklisted(self, ip_address: str) -> bool:
        """Check if IP is blacklisted and not expired"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ip_blacklist 
                WHERE ip_address = ? 
                AND is_active = 1
                AND (expires_at IS NULL OR expires_at > datetime('now'))
            """, (ip_address,))
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False

    def check_ip_access(self, ip_address: str) -> Dict[str, bool]:
        """Check if IP has access"""
        whitelisted = self.is_whitelisted(ip_address)
        blacklisted = self.is_blacklisted(ip_address)

        # If there are any whitelist entries, only whitelisted IPs can access
        has_whitelist = self._has_whitelist_entries()

        if has_whitelist:
            allowed = whitelisted and not blacklisted
        else:
            allowed = not blacklisted

        return {
            'allowed': allowed,
            'whitelisted': whitelisted,
            'blacklisted': blacklisted
        }

    def get_whitelist(self) -> List[Dict[str, Any]]:
        """Get all whitelisted IPs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip_address, description, added_by, created_at, is_active
                FROM ip_whitelist
                ORDER BY created_at DESC
            """)
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'ip': row[1],
                    'description': row[2],
                    'added_by': row[3],
                    'created_at': row[4],
                    'active': bool(row[5])
                })
            conn.close()
            return results
        except Exception:
            return []

    def get_blacklist(self) -> List[Dict[str, Any]]:
        """Get all blacklisted IPs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip_address, reason, blocked_by, block_type, created_at, expires_at, is_active
                FROM ip_blacklist
                ORDER BY created_at DESC
            """)
            results = []
            for row in cursor.fetchall():
                expires = row[6]
                status = 'Active'
                if expires:
                    if datetime.fromisoformat(expires) < datetime.now():
                        status = 'Expired'

                results.append({
                    'id': row[0],
                    'ip': row[1],
                    'reason': row[2],
                    'blocked_by': row[3],
                    'block_type': row[4],
                    'created_at': row[5],
                    'expires_at': expires if expires else 'Permanent',
                    'active': bool(row[7]),
                    'status': status
                })
            conn.close()
            return results
        except Exception:
            return []

    def _has_whitelist_entries(self) -> bool:
        """Check if there are any whitelist entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ip_whitelist WHERE is_active = 1")
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except Exception:
            return False

    def get_ip_statistics(self) -> Dict[str, int]:
        """Get IP management statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM ip_whitelist WHERE is_active = 1")
            whitelist_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM ip_blacklist WHERE is_active = 1")
            blacklist_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM ip_blacklist 
                WHERE block_type = 'automatic' AND is_active = 1
            """)
            auto_blocked = cursor.fetchone()[0]

            conn.close()

            return {
                'whitelist_count': whitelist_count,
                'blacklist_count': blacklist_count,
                'auto_blocked': auto_blocked
            }
        except Exception:
            return {
                'whitelist_count': 0,
                'blacklist_count': 0,
                'auto_blocked': 0
            }

