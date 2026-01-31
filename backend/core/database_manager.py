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

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Singleton pattern - tek instance"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = DB_PATH, pool_size: int = 10):
        """
        Args:
            db_path: Veritabanı yolu
            pool_size: Connection pool boyutu (varsayılan: 10)
        """
        # İlk init kontrolü (singleton için)
        if hasattr(self, '_initialized'):
            return

        # Mutlak yol
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._local = threading.local()
        self._initialized = True

        # Pool'u başlat
        self._init_pool()

        logging.info(f" DatabaseManager başlatıldı: {pool_size} bağlantı pool")

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
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache

        # Row factory - dict benzeri erişim
        conn.row_factory = sqlite3.Row

        return conn

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
            # Pool'dan bağlantı al (timeout: 5 saniye)
            conn = self._pool.get(timeout=5)
            yield conn
        except queue.Empty:
            # Pool dolu ise yeni bağlantı oluştur (geçici)
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
            # Bağlantıyı pool'a geri koy
            if conn:
                try:
                    self._pool.put_nowait(conn)
                except queue.Full:
                    conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Basit sorgu çalıştır (SELECT için)
        
        Args:
            query: SQL sorgusu
            params: Parametreler (tuple)
        
        Returns:
            list: Sonuç satırları
        """
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

