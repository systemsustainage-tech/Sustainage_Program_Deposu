#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logging Decorator
Tüm işlemleri otomatik audit_logs'a kaydeder
"""

import logging
import json
import os
import sqlite3
from functools import wraps


def audit_log(action: str, module: str = None) -> None:
    """
    Otomatik audit logging decorator
    
    Kullanım:
        @audit_log(action='policy.create', module='PolicyManager')
        def create_policy(self, ...) -> None:
            ...
    """
    def decorator(func) -> None:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            # İşlemi çalıştır
            result = func(*args, **kwargs)

            # Audit log kaydet
            try:
                # Parametreleri topla
                user_id = kwargs.get('user_id') or (args[1] if len(args) > 1 else None)
                kwargs.get('company_id') or (args[2] if len(args) > 2 else None)

                payload = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'result': str(result)[:100] if result else None
                }

                # Veritabanına kaydet
                db_path = os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Resource type belirle (modül adı veya varsayılan)
                resource_type = module if module else 'system'
                resource_id = 0 # Varsayılan

                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource_type, resource_id, payload_json)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, action, resource_type, resource_id, json.dumps(payload)))

                conn.commit()
                conn.close()

            except Exception as e:
                # Audit hatası uygulamayı durdurmasın
                logging.info(f"[UYARI] Audit log: {e}")

            return result

        return wrapper
    return decorator


# Kullanım örneği:
"""
from utils.audit_decorator import audit_log
from typing import Optional, List, Dict, Tuple, Any

class PolicyManager:
    @audit_log(action='policy.create', module='PolicyManager')
    def create_policy(self, user_id, company_id, name, content) -> None:
        # İşlem
        return policy_id
        
    @audit_log(action='policy.update')
    def update_policy(self, policy_id, user_id, **changes) -> None:
        # Güncelleme
        return True

# Her çağrıda otomatik audit_logs'a yazılır!
"""

