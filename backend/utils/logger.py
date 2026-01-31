#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merkezi Loglama Sistemi
Tüm hataları ve olayları kayıt altına alır
"""

import logging
import os
import sqlite3
from datetime import datetime


class SDGLogger:
    """Merkezi log yöneticisi"""

    _instance = None

    def __new__(cls, db_path: str = None):
        """Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None) -> None:
        if self._initialized:
            return

        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

        # Python logging
        self.logger = logging.getLogger('SDG')
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # File handler
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'sdg_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self._initialized = True
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Log tablosu"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT,
                    message TEXT NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logging.info(f"[UYARI] Log tablo: {e}")

    def log_error(self, message: str, module: str = None, user_id: int = None, **kwargs) -> None:
        """Hata logla"""
        self.logger.error(f"{module or 'Unknown'}: {message}")
        self._save_to_db('ERROR', message, module, user_id, kwargs.get('company_id'))

    def log_warning(self, message: str, module: str = None, user_id: int = None, **kwargs) -> None:
        """Uyarı logla"""
        self.logger.warning(f"{module or 'Unknown'}: {message}")
        self._save_to_db('WARNING', message, module, user_id, kwargs.get('company_id'))

    def log_info(self, message: str, module: str = None, user_id: int = None, **kwargs) -> None:
        """Bilgi logla"""
        self.logger.info(f"{module or 'Unknown'}: {message}")
        self._save_to_db('INFO', message, module, user_id, kwargs.get('company_id'))

    def log_debug(self, message: str, module: str = None) -> None:
        """Debug logla"""
        self.logger.debug(f"{module or 'Unknown'}: {message}")

    def _save_to_db(self, level: str, message: str, module: str,
                    user_id: int, company_id: int):
        """Veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (level, module, message, user_id, company_id)
                VALUES (?, ?, ?, ?, ?)
            """, (level, module, message, user_id, company_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f'Silent error in logger.py: {str(e)}')  # Log kaydı başarısız olsa bile uygulama durmasın


# Global logger instance
_logger = None

def get_logger(db_path: str = None) -> SDGLogger:
    """Global logger al"""
    global _logger
    if _logger is None:
        _logger = SDGLogger(db_path)
    return _logger


# Kolay kullanım fonksiyonları
def log_error(message: str, module: str = None, **kwargs) -> None:
    """Hata logla"""
    get_logger().log_error(message, module, **kwargs)

def log_warning(message: str, module: str = None, **kwargs) -> None:
    """Uyarı logla"""
    get_logger().log_warning(message, module, **kwargs)

def log_info(message: str, module: str = None, **kwargs) -> None:
    """Bilgi logla"""
    get_logger().log_info(message, module, **kwargs)

