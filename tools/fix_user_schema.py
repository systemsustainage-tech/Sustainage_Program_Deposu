#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı yönetimi şemasını düzelt
Eksik sütunları ekler ve mevcut verileri korur
"""

import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fix_user_schema() -> None:
    """Kullanıcı yönetimi şemasını düzelt"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logging.info("Kullanıcı yönetimi şeması düzeltiliyor...")
        
        # Users tablosuna eksik sütunları ekle
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")
            logging.info("[OK] users.updated_at sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] users.updated_at sütunu zaten mevcut")
        
        # Permissions tablosuna eksik sütunları ekle
        try:
            cursor.execute("ALTER TABLE permissions ADD COLUMN module TEXT")
            logging.info("[OK] permissions.module sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] permissions.module sütunu zaten mevcut")
        
        try:
            cursor.execute("ALTER TABLE permissions ADD COLUMN action TEXT")
            logging.info("[OK] permissions.action sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] permissions.action sütunu zaten mevcut")
        
        try:
            cursor.execute("ALTER TABLE permissions ADD COLUMN resource TEXT")
            logging.info("[OK] permissions.resource sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] permissions.resource sütunu zaten mevcut")
        
        # Departments tablosuna eksik sütunları ekle
        try:
            cursor.execute("ALTER TABLE departments ADD COLUMN manager_id INTEGER")
            logging.info("[OK] departments.manager_id sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] departments.manager_id sütunu zaten mevcut")
        
        # Audit_logs tablosuna eksik sütunları ekle
        try:
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN old_values TEXT")
            logging.info("[OK] audit_logs.old_values sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] audit_logs.old_values sütunu zaten mevcut")
        
        try:
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN new_values TEXT")
            logging.info("[OK] audit_logs.new_values sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] audit_logs.new_values sütunu zaten mevcut")
        
        try:
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN ip_address TEXT")
            logging.info("[OK] audit_logs.ip_address sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] audit_logs.ip_address sütunu zaten mevcut")
        
        # Eksik tabloları oluştur
        create_missing_tables(cursor)
        
        conn.commit()
        logging.info("[SUCCESS] Kullanici yonetimi semasi basariyla duzeltildi!")
        return True
        
    except Exception as e:
        logging.error(f"[ERROR] Sema duzeltilirken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_missing_tables(cursor) -> None:
    """Eksik tabloları oluştur"""
    
    # Users tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            department TEXT,
            position TEXT,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            last_login TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)
    
    # Roles tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            is_system_role INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)
    
    # Permissions tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            description TEXT,
            module TEXT,
            action TEXT,
            resource TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)
    
    # Departments tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            parent_department_id INTEGER,
            manager_id INTEGER,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (parent_department_id) REFERENCES departments(id),
            FOREIGN KEY (manager_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)
    
    # User roles tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            assigned_by INTEGER,
            assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(user_id, role_id)
        )
    """)
    
    # Role permissions tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            granted_by INTEGER,
            granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (permission_id) REFERENCES permissions(id),
            FOREIGN KEY (granted_by) REFERENCES users(id),
            UNIQUE(role_id, permission_id)
        )
    """)
    
    # User permissions tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            granted_by INTEGER,
            granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (permission_id) REFERENCES permissions(id),
            FOREIGN KEY (granted_by) REFERENCES users(id),
            UNIQUE(user_id, permission_id)
        )
    """)
    
    # User profiles tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            language TEXT DEFAULT 'tr',
            timezone TEXT DEFAULT 'Europe/Istanbul',
            theme TEXT DEFAULT 'light',
            notifications_enabled INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Audit logs tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    logging.info("[INFO] Tum tablolar kontrol edildi/olusturuldu")

if __name__ == "__main__":
    fix_user_schema()
