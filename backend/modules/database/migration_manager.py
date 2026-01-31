import sqlite3
import os
import logging
import importlib.util
from datetime import datetime

class MigrationManager:
    """Merkezi veritabanı şema ve versiyon yönetim sınıfı."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        # Migrations klasörü bu dosyanın yanındaki 'migrations' klasörüdür
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        os.makedirs(self.migrations_dir, exist_ok=True)
        self._init_migration_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_migration_table(self):
        """Versiyon takip tablosunu oluştur."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        except Exception as e:
            logging.error(f"Migration tablosu başlatılamadı: {e}")

    def get_applied_migrations(self):
        """Uygulanmış migrasyonların versiyon numaralarını getir."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
                return {row[0] for row in cursor.fetchall()}
        except Exception:
            return set()

    def apply_migrations(self):
        """Bekleyen migrasyonları uygula."""
        applied = self.get_applied_migrations()
        
        # Migrasyon dosyalarını bul (format: 001_xxx.py)
        migration_files = []
        for f in os.listdir(self.migrations_dir):
            if f.endswith('.py') and not f.startswith('__'):
                try:
                    version = int(f.split('_')[0])
                    migration_files.append((version, f))
                except ValueError:
                    logging.warning(f"Geçersiz migrasyon dosya adı: {f}")
        
        # Versiyona göre sırala
        migration_files.sort()
        
        for version, filename in migration_files:
            if version not in applied:
                logging.info(f"Applying migration {version}: {filename}")
                if self._run_migration(version, filename):
                    logging.info(f"Migration {version} applied successfully.")
                else:
                    logging.error(f"Migration {version} failed. Stopping.")
                    return False
        return True

    def _run_migration(self, version, filename):
        """Tek bir migrasyon dosyasını çalıştır."""
        file_path = os.path.join(self.migrations_dir, filename)
        module_name = f"migration_{version}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Modülün 'up' fonksiyonu olmalı
            if hasattr(module, 'up'):
                with self._get_connection() as conn:
                    module.up(conn)
                    conn.execute("INSERT INTO schema_migrations (version, name) VALUES (?, ?)", (version, filename))
                return True
            else:
                logging.error(f"Migration {filename} 'up' fonksiyonu içermiyor.")
                return False
        except Exception as e:
            logging.error(f"Migration hatası ({filename}): {e}")
            return False
