#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı Connection Pool
Bağlantı yeniden kullanımı ile performans artışı
"""

import sqlite3
import threading
from contextlib import contextmanager


class ConnectionPool:
    """SQLite connection pool (thread-safe)"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = None):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = None) -> None:
        if self._initialized:
            return

        import os
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._local = threading.local()
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Thread-safe bağlantı al"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Row factory (dict-like access)
            self._local.connection.row_factory = sqlite3.Row

        return self._local.connection

    @contextmanager
    def get_cursor(self) -> None:
        """Context manager ile cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def close_all(self) -> None:
        """Tüm bağlantıları kapat"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# Global pool instance
_pool = None

def get_pool(db_path: str = None) -> ConnectionPool:
    """Global pool al"""
    global _pool
    if _pool is None:
        _pool = ConnectionPool(db_path)
    return _pool


@contextmanager
def get_db_cursor(db_path: str = None) -> None:
    """
    Kolay kullanım için context manager
    
    Kullanım:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            # Auto-commit
    """
    pool = get_pool(db_path)
    with pool.get_cursor() as cursor:
        yield cursor

