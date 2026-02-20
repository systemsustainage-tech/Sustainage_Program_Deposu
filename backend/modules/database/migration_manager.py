import sqlite3
import os
import logging
import importlib.util
from datetime import datetime
from typing import Optional

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

class MigrationManager(BaseTenantManager):
    """Merkezi veritabanı şema ve versiyon yönetim sınıfı."""
    
    def __init__(self, db_path, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)
        # Migrations klasörü bu dosyanın yanındaki 'migrations' klasörüdür
        self.migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        os.makedirs(self.migrations_dir, exist_ok=True)
        self._init_migration_table()

    def _init_migration_table(self):
        """Versiyon takip tablosunu oluştur."""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """, skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"Migration tablosu başlatılamadı: {e}")

    def get_applied_migrations(self):
        """Uygulanmış migrasyonların versiyon numaralarını getir."""
        try:
            rows = self.execute_query("SELECT version FROM schema_migrations ORDER BY version", skip_tenant_filter=True)
            return {row['version'] for row in rows}
        except Exception:
            return set()

    def apply_migrations(self):
        """Bekleyen migrasyonları uygula."""
        applied = self.get_applied_migrations()
        
        # Migrasyon dosyalarını bul (format: 001_xxx.py)
        migration_files = []
        if os.path.exists(self.migrations_dir):
            for f in os.listdir(self.migrations_dir):
                if f.endswith('.py') and f[0:3].isdigit():
                    migration_files.append(f)
        
        migration_files.sort()
        
        applied_count = 0
        for f in migration_files:
            try:
                version = int(f.split('_')[0])
                if version in applied:
                    continue
                    
                logging.info(f"Applying migration: {f}")
                
                # Modülü dinamik olarak yükle
                spec = importlib.util.spec_from_file_location("migration_module", os.path.join(self.migrations_dir, f))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # up() fonksiyonunu çalıştır
                if hasattr(module, 'up'):
                    # Migrasyonlara connection nesnesi yerine db manager'ı veya path'i versek daha iyi
                    # Ama mevcut yapı connection bekliyor olabilir.
                    # Eğer module.up(conn) bekliyorsa:
                    # self.db.get_connection() kullanabiliriz ama context manager gerektirir.
                    # BaseTenantManager'da get_connection yok.
                    # Geçici olarak sqlite3.connect kullanalım ama migration mantığı genelde globaldir.
                    
                    with sqlite3.connect(self.db_path) as conn:
                        module.up(conn)
                        
                    # Kayıt at
                    self.execute_update(
                        "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                        (version, f),
                        skip_tenant_filter=True
                    )
                    applied_count += 1
                    logging.info(f"Migration applied: {f}")
            except Exception as e:
                logging.error(f"Migration hatası ({f}): {e}")
                # Hata durumunda durmalı mıyız? Evet.
                break
                
        return applied_count
