#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MERKEZI VERİTABANI YÖNETİCİSİ
- Connection pool
- Thread-safe bağlantılar
- Context manager desteği
- Otomatik cleanup
- Performans optimizasyonu
"""

import logging
import os
import queue
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Generator, Optional
from config.database import DB_PATH
from backend.core.database import inject_tenant_filter
from flask import g, has_request_context

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseManager:
    """
    Merkezi veritabanı yöneticisi - Singleton pattern
    
    Özellikler:
    - Connection pooling (varsayılan: 5 bağlantı)
    - Thread-safe operasyonlar
    - Context manager (with statement)
    - Otomatik bağlantı yönetimi
    - WAL modu (Write-Ahead Logging)
    """

    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, db_path: str = DB_PATH, *args, **kwargs):
        """Multiton pattern - her db_path için tek instance"""
        if not os.path.isabs(db_path):
            cwd_candidate = os.path.abspath(db_path)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            root_candidate = os.path.join(project_root, db_path)
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            backend_candidate = os.path.join(backend_dir, db_path)

            if os.path.exists(cwd_candidate):
                db_path = cwd_candidate
            elif os.path.exists(root_candidate):
                db_path = root_candidate
            else:
                db_path = backend_candidate

        with cls._lock:
            if db_path not in cls._instances:
                cls._instances[db_path] = super().__new__(cls)
        return cls._instances[db_path]

    def __init__(self, db_path: str = DB_PATH, pool_size: int = None):
        """
        Args:
            db_path: Veritabanı yolu
            pool_size: Connection pool boyutu (varsayılan: Env veya 50)
        """
        # İlk init kontrolü (singleton/multiton için)
        if hasattr(self, '_initialized'):
            return

        if not os.path.isabs(db_path):
            cwd_candidate = os.path.abspath(db_path)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            root_candidate = os.path.join(project_root, db_path)
            backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            backend_candidate = os.path.join(backend_dir, db_path)

            if os.path.exists(cwd_candidate):
                db_path = cwd_candidate
            elif os.path.exists(root_candidate):
                db_path = root_candidate
            else:
                db_path = backend_candidate

        # Performance Tuning based on Load Test
        # 50 users -> 50 conn is okay
        # 200 users -> might need more or handle queue better
        # Let's make it dynamic based on env or default to optimized value
        if pool_size is None:
            # Increased pool size for load handling (200 concurrent users)
            # Default to 200 to match max concurrent users
            pool_size = int(os.environ.get('DB_POOL_SIZE', 200))

        self.db_path = db_path
        self._use_pool = not os.path.basename(self.db_path).lower().startswith('test_')
        self.pool_size = pool_size if self._use_pool else 0
        self._pool = queue.Queue(maxsize=self.pool_size) if self._use_pool else None
        self._local = threading.local()
        self._initialized = True

        if self._use_pool:
            self._init_pool()

        logging.info(f" DatabaseManager başlatıldı: {db_path} ({self.pool_size} bağlantı)")

    def _init_pool(self) -> None:
        """Connection pool'u başlat"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self._pool.put(conn)

    def _create_connection(self) -> sqlite3.Connection:
        """
        Yeni veritabanı bağlantısı oluştur
        
        Optimizasyonlar:
        - WAL modu (Write-Ahead Logging)
        - Foreign keys aktif
        - Journal mode
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)

        # Performans optimizasyonları
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Daha hızlı yazma
        conn.execute("PRAGMA foreign_keys=ON")  # Foreign key kontrolü
        conn.execute("PRAGMA temp_store=MEMORY")  # Geçici veriler RAM'de
        conn.execute("PRAGMA cache_size=-128000")  # Increased to 128MB cache
        conn.execute("PRAGMA mmap_size=268435456") # 256MB mmap for faster reads
        
        # Row factory
        conn.row_factory = sqlite3.Row
        
        return conn

    def close(self):
        """Tüm bağlantıları kapat ve instance'ı temizle"""
        try:
            if self._use_pool and self._pool is not None:
                while not self._pool.empty():
                    try:
                        conn = self._pool.get_nowait()
                        conn.close()
                    except:
                        pass
            
            # Instance listesinden çıkar
            with self._lock:
                if self.db_path in self._instances:
                    del self._instances[self.db_path]
            
            logging.info(f"DatabaseManager kapatıldı: {self.db_path}")
        except Exception as e:
            logging.error(f"DatabaseManager kapatılırken hata: {e}")

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager ile bağlantı al
        
        Kullanım:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = None
        try:
            if not self._use_pool:
                conn = self._create_connection()
                yield conn
                return

            conn = self._pool.get(timeout=5)
            yield conn
        except queue.Empty:
            logging.info("️ Pool dolu, geçici bağlantı oluşturuluyor...")
            temp_conn = self._create_connection()
            try:
                yield temp_conn
            finally:
                temp_conn.close()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if not self._use_pool:
                if conn:
                    conn.close()
                return

            if conn and self._pool is not None:
                try:
                    self._pool.put_nowait(conn)
                except queue.Full:
                    conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Sorgu çalıştır (SELECT)
        
        Args:
            query: SQL sorgusu
            params: Parametreler
        
        Returns:
            list: Sonuç satırları (Row factory ile)
        """
        # Inject tenant filter if applicable
        if has_request_context() and hasattr(g, 'user') and g.user and 'company_id' in g.user:
            query, params = inject_tenant_filter(query, params, g.user['company_id'])
        elif has_request_context() and hasattr(g, 'license') and g.license and 'company_id' in g.license:
             # Fallback for license-based auth
             query, params = inject_tenant_filter(query, params, g.license['company_id'])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Güncelleme sorgusu (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL sorgusu
            params: Parametreler
        
        Returns:
            int: Etkilenen satır sayısı veya lastrowid
        """
        # Inject tenant filter if applicable
        if has_request_context() and hasattr(g, 'user') and g.user and 'company_id' in g.user:
            query, params = inject_tenant_filter(query, params, g.user['company_id'])
        elif has_request_context() and hasattr(g, 'license') and g.license and 'company_id' in g.license:
             query, params = inject_tenant_filter(query, params, g.license['company_id'])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def execute_many(self, query: str, params_list: list) -> int:
        """
        Toplu işlem (batch insert/update)
        
        Args:
            query: SQL sorgusu
            params_list: Parametre listesi
        
        Returns:
            int: İşlem sayısı
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

    def execute_script(self, script: str) -> None:
        """
        SQL scripti çalıştır (executescript)
        
        Args:
            script: SQL script içeriği
        """
        with self.get_connection() as conn:
            conn.executescript(script)

    def transaction(self, func: callable, *args, **kwargs) -> Any:
        """
        Transaction içinde fonksiyon çalıştır
        
        Args:
            func: Çalıştırılacak fonksiyon (conn parametresi almalı)
            *args, **kwargs: Fonksiyon parametreleri
        
        Returns:
            Fonksiyon dönüş değeri
        """
        with self.get_connection() as conn:
            try:
                result = func(conn, *args, **kwargs)
                conn.commit()
                return result
            except Exception:
                conn.rollback()
                raise

    def close_all(self) -> None:
        """Tüm pool bağlantılarını kapat"""
        closed = 0
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
                closed += 1
            except queue.Empty:
                break
        logging.info(f" {closed} bağlantı kapatıldı")

    def get_stats(self) -> dict:
        """Pool istatistikleri"""
        return {
            'db_path': self.db_path,
            'pool_size': self.pool_size,
            'available': self._pool.qsize(),
            'in_use': self.pool_size - self._pool.qsize()
        }


# ============================================
# GLOBAL INSTANCE (Singleton)
# ============================================

# Varsayılan instance
_default_manager: Optional[DatabaseManager] = None
_manager_lock = threading.Lock()


def get_db_manager(db_path: str = DB_PATH, pool_size: int = 10) -> DatabaseManager:
    """
    Global DatabaseManager instance'ını al
    
    Args:
        db_path: Veritabanı yolu
        pool_size: Pool boyutu
    
    Returns:
        DatabaseManager instance
    """
    global _default_manager

    if _default_manager is None:
        with _manager_lock:
            if _default_manager is None:
                _default_manager = DatabaseManager(db_path, pool_size)

    return _default_manager


# ============================================
# KOLAYLIKFONKSİYONLARI (Kısa yol)
# ============================================

def execute_query(query: str, params: tuple = (), db_path: str = None) -> list:
    """Kısa yol: SELECT sorgusu"""
    manager = get_db_manager(db_path) if db_path else get_db_manager()
    return manager.execute_query(query, params)


def execute_update(query: str, params: tuple = (), db_path: str = None) -> int:
    """Kısa yol: UPDATE/INSERT/DELETE"""
    manager = get_db_manager(db_path) if db_path else get_db_manager()
    return manager.execute_update(query, params)


def get_connection(db_path: str = None):
    """Kısa yol: Connection context manager"""
    manager = get_db_manager(db_path) if db_path else get_db_manager()
    return manager.get_connection()


# ============================================
# GERIYE DÖNÜK UYUMLULUK WRAPPER
# ============================================

class LegacyDatabaseWrapper:
    """
    Eski kodlarla uyumluluk için wrapper
    
    Kullanım (Eski kod):
        conn = sqlite3.connect(DB_PATH)
    
    Yeni kod:
        from core.database_manager import get_connection
        with get_connection() as conn:
            ...
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.manager = get_db_manager(db_path)

    def get_connection(self):
        """Geriye dönük uyumlu connection"""
        return self.manager.get_connection()


if __name__ == "__main__":
    # Test
    logging.info(" DatabaseManager Test...")

    # Manager oluştur
    manager = get_db_manager(DB_PATH, pool_size=5)

    # Stats
    stats = manager.get_stats()
    logging.info(f" Stats: {stats}")

    # Test sorgu
    with manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
        tables = cursor.fetchall()
        logging.info(f" İlk 5 tablo: {[t[0] for t in tables]}")

    # Kısa yol test
    result = execute_query("SELECT COUNT(*) as count FROM users")
    logging.info(f" Toplam kullanıcı: {result[0]['count'] if result else 0}")

    # Stats (sonra)
    stats = manager.get_stats()
    logging.info(f" Stats (sonra): {stats}")

    logging.info(" Test tamamlandı!")

