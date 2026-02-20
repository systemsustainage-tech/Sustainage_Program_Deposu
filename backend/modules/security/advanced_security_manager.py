#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Güvenlik Özellikleri
Multi-factor authentication, IP whitelist, session recording, threat detection
"""

import os
import secrets
import sqlite3
import ipaddress
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# İsteğe bağlı bağımlılıklar — eksikse belirli özellikler devre dışı
try:
    import qrcode
except Exception:
    qrcode = None

try:
    import pyotp
except Exception:
    pyotp = None

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager


class AdvancedSecurityManager(BaseTenantManager):
    """Gelişmiş Güvenlik Özellikleri Yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_advanced_security_tables()
        self._setup_logging()

    def _setup_logging(self):
        # Configure logging if not already configured
        pass

    def _init_advanced_security_tables(self) -> None:
        """Gelişmiş güvenlik tablolarını oluştur"""
        try:
            # Multi-factor authentication tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS mfa_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    company_id INTEGER, -- Optional, user might belong to multiple or none
                    secret_key TEXT NOT NULL,
                    backup_codes TEXT,
                    is_enabled BOOLEAN DEFAULT 0,
                    method TEXT DEFAULT 'totp', -- totp, sms, email
                    last_used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """, skip_tenant_filter=True)
            
            # ... other tables creation would go here using self.execute_update ...
            
        except Exception as e:
            logging.error(f"Gelişmiş güvenlik tabloları oluşturulamadı: {e}")
