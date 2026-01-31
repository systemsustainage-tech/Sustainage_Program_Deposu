#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uygulama Konfigürasyonu
Merkezi ayarlar ve parametreler
"""

import logging
import os
import sqlite3


class AppConfig:
    """Uygulama konfigürasyon yöneticisi"""

    # Varsayılan ayarlar
    DEFAULTS = {
        'excel_data_path': 'SDG_232.xlsx',
        'upload_directory': 'data/uploads',
        'report_directory': 'data/reports',
        'max_file_size_mb': 50,
        'session_timeout_minutes': 30,
        'password_min_length': 6,
        'treeview_page_size': 100,
        'email_daily_reminder_time': '09:00',
        'backup_enabled': True,
        'backup_interval_days': 7
    }

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_settings_table()
        self._load_settings()

    def _ensure_settings_table(self) -> None:
        """Settings tablosunu oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logging.info(f"[UYARI] Settings tablo: {e}")

    def _load_settings(self) -> None:
        """Ayarları yükle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")

            self.settings = dict(self.DEFAULTS)  # Varsayılanlarla başla

            for key, value in cursor.fetchall():
                self.settings[key] = value

            conn.close()
        except Exception as e:
            logging.info(f"[UYARI] Ayarlar yuklenemedi: {e}")
            self.settings = dict(self.DEFAULTS)

    def get(self, key: str, default=None) -> None:
        """Ayar değeri al"""
        return self.settings.get(key, default or self.DEFAULTS.get(key))

    def set(self, key: str, value: str) -> bool:
        """Ayar değeri kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, value))

            conn.commit()
            conn.close()

            self.settings[key] = value
            return True
        except Exception as e:
            logging.error(f"[HATA] Ayar kayit: {e}")
            return False

    def get_excel_path(self) -> str:
        """Excel dosya yolu al (settings veya fallback)"""
        excel_file = self.get('excel_data_path')
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Tam yol oluştur
        excel_path = os.path.join(base_dir, excel_file)

        # Dosya var mı kontrol et
        if os.path.exists(excel_path):
            return excel_path

        # Alternatif konumları dene
        alternatives = [
            os.path.join(base_dir, 'data', excel_file),
            os.path.join(base_dir, 'sdg', excel_file),
            excel_file  # Direkt path
        ]

        for alt_path in alternatives:
            if os.path.exists(alt_path):
                return alt_path

        # Bulunamazsa varsayılan döndür (hata GUI'de gösterilecek)
        return excel_path


# Global instance
_config = None

def get_config(db_path: str = None) -> None:
    """Global config instance al"""
    global _config
    if _config is None:
        _config = AppConfig(db_path)
    return _config

