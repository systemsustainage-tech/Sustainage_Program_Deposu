#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Manager Component
Whitelist and Blacklist management
"""

import ipaddress
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

class IPManager(BaseTenantManager):
    """IP whitelist and blacklist manager"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)

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

            self.execute_update("""
                INSERT INTO ip_whitelist (ip_address, description, added_by, is_active)
                VALUES (?, ?, ?, 1)
            """, (ip_address, description, added_by))

            return {'success': True, 'message': f'IP {ip_address} added to whitelist'}
        except ValueError:
            return {'success': False, 'message': 'Invalid IP address format'}
        except sqlite3.IntegrityError:
            return {'success': False, 'message': 'IP already in whitelist'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
            
    def remove_from_whitelist(self, ip_address: str) -> Dict[str, Any]:
        """Remove IP from whitelist"""
        try:
            self.execute_update("DELETE FROM ip_whitelist WHERE ip_address = ?", (ip_address,))
            return {'success': True, 'message': f'IP {ip_address} removed from whitelist'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
            
    def is_whitelisted(self, ip_address: str) -> bool:
        """Check if IP is whitelisted"""
        try:
            result = self.execute_query(
                "SELECT 1 FROM ip_whitelist WHERE ip_address = ? AND is_active = 1", 
                (ip_address,)
            )
            return len(result) > 0
        except Exception:
            return False
