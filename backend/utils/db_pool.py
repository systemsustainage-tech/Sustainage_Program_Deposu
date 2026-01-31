#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Connection Pool
Performance optimizasyonu için veritabanı bağlantı havuzu
"""

import logging
import queue
import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional


class DatabaseConnectionPool:
    """SQLite veritabanı bağlantı havuzu"""

    def __init__(self, db_path: str, max_connections: int = 10, timeout: int = 30) -> None:
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool = queue.Queue(maxsize=max_connections)
        self._created_connections = 0
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # İlk bağlantıyı oluştur
        self._create_initial_connections()

    def _create_initial_connections(self) -> None:
        """İlk bağlantıları oluştur"""
        for _ in range(min(3, self.max_connections)):
            conn = self._create_connection()
            if conn:
                self._pool.put(conn)

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Yeni veritabanı bağlantısı oluştur"""
        try:
            with self._lock:
                if self._created_connections >= self.max_connections:
                    return None

                conn = sqlite3.connect(
                    self.db_path,
                    timeout=self.timeout,
                    check_same_thread=False
                )

                # Performance ayarları
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA cache_size=10000")
                conn.execute("PRAGMA temp_store=MEMORY")
                conn.execute("PRAGMA mmap_size=268435456")  # 256MB

                self._created_connections += 1
                self.logger.debug(f"Yeni bağlantı oluşturuldu. Toplam: {self._created_connections}")
                return conn

        except Exception as e:
            self.logger.error(f"Bağlantı oluşturma hatası: {e}")
            return None

    @contextmanager
    def get_connection(self) -> None:
        """Bağlantı havuzundan bağlantı al"""
        conn = None
        try:
            # Havuzdan bağlantı al
            try:
                conn = self._pool.get(timeout=5)
            except queue.Empty:
                # Havuz boşsa yeni bağlantı oluştur
                conn = self._create_connection()
                if not conn:
                    raise Exception("Bağlantı havuzu dolu ve yeni bağlantı oluşturulamadı")

            # Bağlantıyı test et
            conn.execute("SELECT 1")

            yield conn

        except Exception as e:
            self.logger.error(f"Bağlantı hatası: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            raise
        finally:
            # Bağlantıyı havuzuna geri ver
            if conn:
                try:
                    # Bağlantıyı temizle
                    conn.execute("PRAGMA optimize")
                    self._pool.put(conn)
                except Exception:
                    # Bağlantı bozuksa yeni oluştur
                    try:
                        conn.close()
                    except Exception as e:
                        logging.error(f"Silent error caught: {str(e)}")
                    self._created_connections -= 1

    def close_all(self) -> None:
        """Tüm bağlantıları kapat"""
        with self._lock:
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            self._created_connections = 0

    def get_stats(self) -> dict:
        """Havuz istatistiklerini al"""
        return {
            "max_connections": self.max_connections,
            "created_connections": self._created_connections,
            "available_connections": self._pool.qsize(),
            "db_path": self.db_path
        }

# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None

def init_connection_pool(db_path: str, max_connections: int = 10) -> None:
    """Global bağlantı havuzunu başlat"""
    global _connection_pool
    _connection_pool = DatabaseConnectionPool(db_path, max_connections)

def get_connection_pool() -> Optional[DatabaseConnectionPool]:
    """Global bağlantı havuzunu al"""
    return _connection_pool

@contextmanager
def get_db_connection() -> None:
    """Global bağlantı havuzundan bağlantı al"""
    if not _connection_pool:
        raise Exception("Bağlantı havuzu başlatılmamış. init_connection_pool() çağırın.")

    with _connection_pool.get_connection() as conn:
        yield conn

def close_connection_pool() -> None:
    """Global bağlantı havuzunu kapat"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.close_all()
        _connection_pool = None
