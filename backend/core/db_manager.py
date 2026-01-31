"""
Veritabanı Bağlantı Yöneticisi
Performans optimizasyonu ve bağlantı havuzu yönetimi
"""

import logging
import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator, Optional
from config.database import DB_PATH


class DatabaseManager:
    """Veritabanı bağlantı yöneticisi - singleton pattern"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not self._initialized:
            self.db_path = db_path
            self._initialized = True
            self.logger = logging.getLogger(__name__)

            # Bağlantı ayarları
            self.connection_timeout = 30
            self.max_connections = 10
            self._active_connections = 0

    @contextmanager
    def get_connection(self, read_only: bool = False) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager ile güvenli veritabanı bağlantısı
        """
        conn = None
        try:
            # Bağlantı oluştur
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.connection_timeout,
                check_same_thread=False
            )

            # Optimizasyonlar
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            conn.execute("PRAGMA temp_store = MEMORY")

            if read_only:
                conn.execute("PRAGMA query_only = ON")

            self._active_connections += 1
            self.logger.debug(f"DB bağlantısı açıldı. Aktif: {self._active_connections}")

            yield conn

        except sqlite3.Error as e:
            self.logger.error(f"Veritabanı hatası: {e}")
            if conn:
                conn.rollback()
            raise
        except Exception as e:
            self.logger.error(f"Beklenmeyen hata: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                self._active_connections -= 1
                self.logger.debug(f"DB bağlantısı kapandı. Aktif: {self._active_connections}")

    def execute_query(self, query: str, params: tuple = (), fetch: str = "all") -> Optional[list]:
        """
        Güvenli sorgu çalıştırma
        """
        with self.get_connection(read_only=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()
            elif fetch == "many":
                return cursor.fetchmany()
            return None

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Güvenli güncelleme işlemi
        """
        with self.get_connection(read_only=False) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_batch(self, queries: list, params_list: list = None) -> bool:
        """
        Toplu işlem (transaction)
        """
        if params_list is None:
            params_list = [()] * len(queries)

        try:
            with self.get_connection(read_only=False) as conn:
                cursor = conn.cursor()
                for query, params in zip(queries, params_list):
                    cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Toplu işlem hatası: {e}")
            return False

    def get_table_info(self, table_name: str) -> list:
        """
        Tablo yapısını getir
        """
        return self.execute_query(
            "PRAGMA table_info(?)",
            (table_name,),
            fetch="all"
        )

    def table_exists(self, table_name: str) -> bool:
        """
        Tablo var mı kontrol et
        """
        result = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
            fetch="one"
        )
        return result is not None

    def get_connection_stats(self) -> dict:
        """
        Bağlantı istatistikleri
        """
        return {
            "active_connections": self._active_connections,
            "max_connections": self.max_connections,
            "db_path": self.db_path,
            "timeout": self.connection_timeout
        }

# Global instance
db_manager = DatabaseManager()

# Kullanım örnekleri:
"""
# Basit sorgu
users = db_manager.execute_query("SELECT * FROM users WHERE active = ?", (1,))

# Güncelleme
affected = db_manager.execute_update("UPDATE users SET last_login = ? WHERE id = ?", (now(), user_id))

# Context manager ile
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    # Otomatik commit/rollback
"""
