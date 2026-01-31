#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENİŞLETİLMİŞ AUDIT LOGGER SİSTEMİ
- Korrelasyon ID (request tracking)
- Kritik aksiyon izleme
- Standartlaştırılmış loglama
- Performans metrikleri
- Güvenlik event'leri
"""

import logging
import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class AuditLevel(Enum):
    """Audit seviyesi"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"


class AuditCategory(Enum):
    """Audit kategorisi"""
    AUTH = "authentication"
    USER_MGMT = "user_management"
    DATA_ACCESS = "data_access"
    DATA_MODIFY = "data_modification"
    REPORT = "reporting"
    CONFIG = "configuration"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SYSTEM = "system"


# Thread-local storage for correlation ID
_thread_local = threading.local()


class EnhancedAuditLogger:
    """
    Gelişmiş Audit Logger
    
    Özellikler:
    - Korrelasyon ID (request tracking)
    - Kritik aksiyon izleme
    - Performans metrikleri
    - JSON formatında detaylı loglar
    - Thread-safe
    """

    # Kritik aksiyonlar (mutlaka loglanmalı)
    CRITICAL_ACTIONS = {
        'user_create', 'user_delete', 'user_role_change',
        'password_change', 'password_reset',
        'permission_grant', 'permission_revoke',
        'data_export', 'report_generate', 'report_delete',
        'config_change', 'module_enable', 'module_disable',
        'license_change', 'security_breach', 'unauthorized_access',
        'backup_create', 'backup_restore', 'database_schema_change'
    }

    def __init__(self, db_path: str = DB_PATH):
        """Init"""
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        """Genişletilmiş audit tabloları oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Ana audit log tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    datetime_str TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor_id INTEGER,
                    actor_username TEXT,
                    actor_ip TEXT,
                    target_type TEXT,
                    target_id TEXT,
                    details TEXT,
                    is_critical INTEGER DEFAULT 0,
                    duration_ms REAL,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    session_id TEXT,
                    user_agent TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Korrelasyon ID indeksi
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_correlation_id 
                ON enhanced_audit_log(correlation_id)
            """)

            # Actor indeksi
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_actor 
                ON enhanced_audit_log(actor_id, actor_username)
            """)

            # Timestamp indeksi
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON enhanced_audit_log(timestamp DESC)
            """)

            # Kritik aksiyon indeksi
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_critical 
                ON enhanced_audit_log(is_critical, timestamp DESC)
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f" Audit tablo oluşturma hatası: {e}")

    @staticmethod
    def generate_correlation_id() -> str:
        """Yeni korrelasyon ID oluştur"""
        return f"corr-{uuid.uuid4().hex[:16]}"

    @staticmethod
    def set_correlation_id(correlation_id: str) -> None:
        """Thread için korrelasyon ID belirle"""
        _thread_local.correlation_id = correlation_id

    @staticmethod
    def get_correlation_id() -> str:
        """Mevcut thread korrelasyon ID"""
        if not hasattr(_thread_local, 'correlation_id'):
            _thread_local.correlation_id = EnhancedAuditLogger.generate_correlation_id()
        return _thread_local.correlation_id

    @staticmethod
    def clear_correlation_id() -> None:
        """Korrelasyon ID temizle"""
        if hasattr(_thread_local, 'correlation_id'):
            del _thread_local.correlation_id

    def log(self,
            action: str,
            actor_id: Optional[int] = None,
            actor_username: Optional[str] = None,
            level: AuditLevel = AuditLevel.INFO,
            category: AuditCategory = AuditCategory.SYSTEM,
            target_type: Optional[str] = None,
            target_id: Optional[str] = None,
            details: Optional[Dict] = None,
            duration_ms: Optional[float] = None,
            status: str = "success",
            error_message: Optional[str] = None,
            actor_ip: Optional[str] = None,
            session_id: Optional[str] = None) -> bool:
        """
        Audit log kaydı oluştur
        
        Args:
            action: Yapılan işlem (örn: 'user_create', 'report_export')
            actor_id: İşlemi yapan kullanıcı ID
            actor_username: Kullanıcı adı
            level: Log seviyesi
            category: Kategori
            target_type: Hedef obje tipi (örn: 'user', 'report')
            target_id: Hedef obje ID
            details: Ek detaylar (dict)
            duration_ms: İşlem süresi (ms)
            status: Durum ('success', 'failed', 'partial')
            error_message: Hata mesajı (varsa)
            actor_ip: Kullanıcı IP adresi
            session_id: Oturum ID
        
        Returns:
            bool: Başarılı ise True
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Korrelasyon ID al
            correlation_id = self.get_correlation_id()

            # Kritik aksiyon kontrolü
            is_critical = 1 if action in self.CRITICAL_ACTIONS else 0

            # Timestamp
            timestamp = time.time()
            datetime_str = datetime.now().isoformat()

            # Details JSON
            details_json = json.dumps(details or {}, ensure_ascii=False)

            cursor.execute("""
                INSERT INTO enhanced_audit_log (
                    correlation_id, timestamp, datetime_str, level, category, action,
                    actor_id, actor_username, actor_ip, target_type, target_id,
                    details, is_critical, duration_ms, status, error_message, session_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                correlation_id, timestamp, datetime_str, level.value, category.value, action,
                actor_id, actor_username, actor_ip, target_type, target_id,
                details_json, is_critical, duration_ms, status, error_message, session_id
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logging.error(f" Audit log yazma hatası: {e}")
            return False

    def log_critical_action(self, action: str, actor_username: str, **kwargs) -> bool:
        """Kritik aksiyon logla (kısa yol)"""
        return self.log(
            action=action,
            actor_username=actor_username,
            level=AuditLevel.CRITICAL,
            **kwargs
        )

    def log_security(self, event: str, actor_username: str, details: Dict) -> bool:
        """Güvenlik eventi logla (kısa yol)"""
        return self.log(
            action=event,
            actor_username=actor_username,
            level=AuditLevel.SECURITY,
            category=AuditCategory.SECURITY,
            details=details
        )

    def log_security_event(self, event: str, actor_username: str, details: Dict) -> bool:
        """Güvenlik eventi logla (alias)"""
        return self.log_security(event, actor_username, details)

    def get_logs(self,
                 limit: int = 100,
                 correlation_id: Optional[str] = None,
                 actor_username: Optional[str] = None,
                 action: Optional[str] = None,
                 level: Optional[AuditLevel] = None,
                 is_critical_only: bool = False,
                 start_time: Optional[float] = None,
                 end_time: Optional[float] = None) -> List[Dict]:
        """
        Audit loglarını getir (filtrelenmiş)
        
        Args:
            limit: Maksimum kayıt sayısı
            correlation_id: Belirli bir correlation ID
            actor_username: Kullanıcı adı
            action: Aksiyon adı
            level: Log seviyesi
            is_critical_only: Sadece kritik aksiyonlar
            start_time: Başlangıç zamanı (timestamp)
            end_time: Bitiş zamanı (timestamp)
        
        Returns:
            List[Dict]: Log kayıtları
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM enhanced_audit_log WHERE 1=1"
            params = []

            if correlation_id:
                query += " AND correlation_id = ?"
                params.append(correlation_id)

            if actor_username:
                query += " AND actor_username = ?"
                params.append(actor_username)

            if action:
                query += " AND action LIKE ?"
                params.append(f"%{action}%")

            if level:
                query += " AND level = ?"
                params.append(level.value)

            if is_critical_only:
                query += " AND is_critical = 1"

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            logs = []
            for row in cursor.fetchall():
                log_dict = dict(row)
                # JSON parse
                try:
                    log_dict['details'] = json.loads(log_dict['details'])
                except Exception:
                    log_dict['details'] = {}
                logs.append(log_dict)

            conn.close()
            return logs

        except Exception as e:
            logging.error(f" Log getirme hatası: {e}")
            return []

    def get_critical_actions(self, limit: int = 50) -> List[Dict]:
        """Kritik aksiyonları getir"""
        return self.get_logs(limit=limit, is_critical_only=True)

    def get_session_logs(self, correlation_id: str) -> List[Dict]:
        """Belirli bir oturum/request için tüm loglar"""
        return self.get_logs(correlation_id=correlation_id, limit=1000)

    def get_user_activity(self, username: str, limit: int = 100) -> List[Dict]:
        """Kullanıcı aktivite geçmişi"""
        return self.get_logs(actor_username=username, limit=limit)


# ============================================
# KOLAYLıK FONKSİYONLARI
# ============================================

_default_logger: Optional[EnhancedAuditLogger] = None


def get_audit_logger(db_path: str = DB_PATH) -> EnhancedAuditLogger:
    """Global audit logger instance"""
    global _default_logger
    if _default_logger is None:
        _default_logger = EnhancedAuditLogger(db_path)
    return _default_logger


def audit_log(action: str, actor_username: str, **kwargs) -> bool:
    """Kısa yol: Audit log yaz"""
    logger = get_audit_logger()
    return logger.log(action, actor_username=actor_username, **kwargs)


def audit_critical(action: str, actor_username: str, details: Dict) -> bool:
    """Kısa yol: Kritik aksiyon logla"""
    logger = get_audit_logger()
    return logger.log_critical_action(action, actor_username, details=details)


def audit_security(event: str, actor_username: str, details: Dict) -> bool:
    """Kısa yol: Güvenlik eventi logla"""
    logger = get_audit_logger()
    return logger.log_security_event(event, actor_username, details)


# ============================================
# DECORATOR (Otomatik Audit)
# ============================================

def audit_action(action: str, category: AuditCategory = AuditCategory.SYSTEM):
    """
    Decorator: Fonksiyonu otomatik audit logla
    
    Kullanım:
        @audit_action('user_create', AuditCategory.USER_MGMT)
        def create_user(username, email):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_audit_logger()

            # Actor bilgisi (kwargs'dan veya ilk argümandan)
            actor = kwargs.get('actor_username') or kwargs.get('username') or 'system'

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000  # ms

                logger.log(
                    action=action,
                    actor_username=actor,
                    category=category,
                    level=AuditLevel.INFO,
                    duration_ms=duration,
                    status='success'
                )

                return result

            except Exception as e:
                duration = (time.time() - start_time) * 1000

                logger.log(
                    action=action,
                    actor_username=actor,
                    category=category,
                    level=AuditLevel.ERROR,
                    duration_ms=duration,
                    status='failed',
                    error_message=str(e)
                )

                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Test
    logging.info(" Enhanced Audit Logger Test...")

    logger = EnhancedAuditLogger()

    # Korrelasyon ID test
    corr_id = logger.generate_correlation_id()
    logger.set_correlation_id(corr_id)
    logging.info(f" Korrelasyon ID: {corr_id}")

    # Normal log
    logger.log(
        action="user_login",
        actor_username="test_user",
        category=AuditCategory.AUTH,
        details={'ip': '192.168.1.1', 'browser': 'Chrome'}
    )
    logging.info(" Normal log kaydedildi")

    # Kritik aksiyon
    logger.log_critical_action(
        action="user_delete",
        actor_username="admin",
        details={'deleted_user': 'test_user', 'reason': 'Test'}
    )
    logging.info(" Kritik aksiyon kaydedildi")

    # Güvenlik eventi
    logger.log_security(
        event="unauthorized_access_attempt",
        actor_username="unknown",
        details={'resource': '/admin/users', 'ip': '192.168.1.100'}
    )
    logging.info(" Güvenlik eventi kaydedildi")

    # Logları getir
    logs = logger.get_logs(limit=5)
    logging.info(" Son 5 log getirildi")

    # Kritik aksiyonlar
    critical = logger.get_critical_actions(limit=10)
    logging.info(f" Kritik aksiyonlar: {len(critical)} adet")

    # Korrelasyon ID ile loglar
    session_logs = logger.get_session_logs(corr_id)
    logging.info(f" Oturum logları: {len(session_logs)} adet")

    logging.info(" Test tamamlandı!")

