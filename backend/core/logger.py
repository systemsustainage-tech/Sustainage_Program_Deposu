"""
Merkezi Loglama Sistemi
Hata yönetimi ve audit logları
"""

import json
import logging
import logging.handlers
import os
import sqlite3
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDGLogger:
    """Merkezi loglama sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Logger konfigürasyonu"""
        logger = logging.getLogger('SDG_Platform')
        logger.setLevel(logging.DEBUG)

        # Eğer zaten handler'lar varsa temizle
        if logger.handlers:
            logger.handlers.clear()

        # Log dizini oluştur
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File handler - günlük rotasyon
        file_handler = logging.handlers.RotatingFileHandler(
            f"{log_dir}/sdg_platform.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Handler'ları ekle
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def log_error(self, error: Exception, context: str = "", user_id: Optional[int] = None,
                  module: str = "", additional_data: Dict[str, Any] = None):
        """
        Hata logla ve audit_logs'a kaydet
        """
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "module": module,
            "user_id": user_id,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
            "additional_data": additional_data or {}
        }

        # Logger'a yaz
        self.logger.error(f"HATA [{module}] {context}: {error}", exc_info=True)

        # Audit logs'a kaydet
        self._write_to_audit_logs("error", error_info)

    def log_info(self, message: str, module: str = "", user_id: Optional[int] = None,
                 additional_data: Dict[str, Any] = None):
        """Bilgi logla"""
        log_info = {
            "message": message,
            "module": module,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "additional_data": additional_data or {}
        }

        self.logger.info(f"[{module}] {message}")
        self._write_to_audit_logs("info", log_info)

    def log_warning(self, message: str, module: str = "", user_id: Optional[int] = None,
                    additional_data: Dict[str, Any] = None):
        """Uyarı logla"""
        warning_info = {
            "message": message,
            "module": module,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "additional_data": additional_data or {}
        }

        self.logger.warning(f"[{module}] {message}")
        self._write_to_audit_logs("warning", warning_info)

    def log_user_action(self, action: str, user_id: int, module: str = "",
                        details: Dict[str, Any] = None, success: bool = True):
        """
        Kullanıcı aksiyonunu logla
        """
        action_info = {
            "action": action,
            "user_id": user_id,
            "module": module,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }

        level = "info" if success else "warning"
        message = f"Kullanıcı aksiyonu: {action} - {'Başarılı' if success else 'Başarısız'}"

        if success:
            self.logger.info(f"[{module}] {message} - User: {user_id}")
        else:
            self.logger.warning(f"[{module}] {message} - User: {user_id}")

        self._write_to_audit_logs(level, action_info)

    def _write_to_audit_logs(self, level: str, data: Dict[str, Any]) -> None:
        """
        Audit logs tablosuna yaz
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # audit_logs tablosu yoksa oluştur
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        level TEXT NOT NULL,
                        module TEXT,
                        user_id INTEGER,
                        action TEXT,
                        message TEXT,
                        details TEXT,
                        timestamp TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Log kaydet
                cursor.execute("""
                    INSERT INTO audit_logs (level, module, user_id, action, message, details, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    level,
                    data.get("module", ""),
                    data.get("user_id"),
                    data.get("action", ""),
                    data.get("message", ""),
                    json.dumps(data.get("additional_data", {})),
                    data.get("timestamp", datetime.now().isoformat())
                ))

                conn.commit()

        except Exception as e:
            # Audit log hatası - console'a yaz
            logging.error(f"AUDIT LOG HATASI: {e}")

    def get_audit_logs(self, user_id: Optional[int] = None, module: Optional[str] = None,
                      level: Optional[str] = None, limit: int = 100) -> list:
        """
        Audit logları getir
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM audit_logs WHERE 1=1"
                params = []

                if user_id:
                    query += " AND user_id = ?"
                    params.append(user_id)

                if module:
                    query += " AND module = ?"
                    params.append(module)

                if level:
                    query += " AND level = ?"
                    params.append(level)

                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                return cursor.fetchall()

        except Exception as e:
            self.logger.error(f"Audit log getirme hatası: {e}")
            return []

    def cleanup_old_logs(self, days: int = 30) -> None:
        """
        Eski logları temizle
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM audit_logs 
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days))

                deleted_count = cursor.rowcount
                conn.commit()

                self.logger.info(f"{deleted_count} eski audit log temizlendi")

        except Exception as e:
            self.logger.error(f"Log temizleme hatası: {e}")

# Global logger instance
sdg_logger = SDGLogger()

# Kullanım örnekleri:
"""
# Hata logla
try:
    risky_operation()
except Exception as e:
    sdg_logger.log_error(e, "Veri kaydetme", user_id=123, module="user_manager")

# Kullanıcı aksiyonu
sdg_logger.log_user_action("login", user_id=123, module="auth", success=True)

# Bilgi logla
sdg_logger.log_info("Rapor oluşturuldu", module="reporting", user_id=123)

# Audit logları getir
logs = sdg_logger.get_audit_logs(user_id=123, limit=50)
"""
