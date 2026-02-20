#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Sync Yönetimi Modülü
Bulut senkronizasyonu ve veri yedekleme
"""

import logging
import os
import sqlite3
from typing import Dict, Optional
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager
from config.database import DB_PATH


class CloudSyncManager(BaseTenantManager):
    """Bulut senkronizasyonu ve veri yedekleme"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Cloud sync tablolarını oluştur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cloud_providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    provider_name TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    access_key TEXT,
                    secret_key TEXT,
                    bucket_name TEXT,
                    region TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            self.execute_update("""
                CREATE TABLE IF NOT EXISTS sync_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    job_name TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    sync_frequency TEXT,
                    last_sync TEXT,
                    next_sync TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            self.execute_update("""
                CREATE TABLE IF NOT EXISTS backup_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    backup_name TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    file_size INTEGER,
                    backup_location TEXT,
                    backup_status TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)
            
            logging.info("[OK] Cloud sync yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Cloud sync yonetimi modulu tablo olusturma: {e}")

    def add_cloud_provider(self, company_id: int, provider_name: str, provider_type: str,
                          access_key: str = None, secret_key: str = None,
                          bucket_name: str = None, region: str = None) -> bool:
        """Bulut sağlayıcısı ekle"""
        try:
            self.execute_update("""
                INSERT INTO cloud_providers 
                (company_id, provider_name, provider_type, access_key, secret_key,
                 bucket_name, region)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, provider_name, provider_type, access_key, secret_key,
                  bucket_name, region))
            return True
        except Exception as e:
            logging.error(f"[HATA] Cloud provider ekleme: {e}")
            return False

    def create_sync_job(self, company_id: int, job_name: str, job_type: str,
                       source_path: str, destination_path: str,
                       sync_frequency: str = None) -> bool:
        """Senkronizasyon işi oluştur"""
        try:
            self.execute_update("""
                INSERT INTO sync_jobs 
                (company_id, job_name, job_type, source_path, destination_path, sync_frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, job_name, job_type, source_path, destination_path, sync_frequency))
            return True

        except Exception as e:
            logging.error(f"Senkronizasyon işi oluşturma hatası: {e}")
            return False

    def create_backup_record(self, company_id: int, backup_name: str, backup_type: str,
                           file_size: int = None, backup_location: str = None,
                           backup_status: str = 'completed') -> bool:
        """Yedekleme kaydı oluştur"""
        try:
            self.execute_update("""
                INSERT INTO backup_records 
                (company_id, backup_name, backup_type, file_size, backup_location, backup_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, backup_name, backup_type, file_size, backup_location, backup_status))
            return True

        except Exception as e:
            logging.error(f"Yedekleme kaydı oluşturma hatası: {e}")
            return False

    def get_cloud_sync_summary(self, company_id: int) -> Dict:
        """Cloud sync özeti getir"""
        try:
            # Bulut sağlayıcıları
            # BaseTenantManager execute_query kullanıyoruz
            providers_data = self.execute_query("""
                SELECT provider_name, provider_type, status
                FROM cloud_providers 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            providers = []
            for row in providers_data:
                # Row dictionary olabilir veya tuple olabilir, BaseTenantManager dict dondurur genelde
                # Ama execute_query -> db.execute_query -> row_factory=sqlite3.Row
                # Bu yuzden dict access calisir.
                providers.append({
                    'provider_name': row['provider_name'],
                    'provider_type': row['provider_type'],
                    'status': row['status']
                })

            # Senkronizasyon işleri
            jobs_data = self.execute_query("""
                SELECT job_name, job_type, sync_frequency, last_sync, status
                FROM sync_jobs 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            sync_jobs = []
            for row in jobs_data:
                sync_jobs.append({
                    'job_name': row['job_name'],
                    'job_type': row['job_type'],
                    'sync_frequency': row['sync_frequency'],
                    'last_sync': row['last_sync'],
                    'status': row['status']
                })
            
            # TODO: Backup records count logic was incomplete in original file
            # Let's add basic backup stats if needed or just return what we have
            
            return {
                'providers': providers,
                'sync_jobs': sync_jobs
            }

        except Exception as e:
            logging.error(f"Cloud sync özeti hatası: {e}")
            return {'providers': [], 'sync_jobs': []}

    def schedule_automatic_backup(self, company_id: int, backup_name: str,
                                backup_frequency: str = 'daily') -> bool:
        """Otomatik yedekleme zamanla"""
        # Bu fonksiyon gerçek uygulamada bir cron job veya scheduler ile entegre edilir
        backup_types = {
            'daily': 'Günlük Yedek',
            'weekly': 'Haftalık Yedek',
            'monthly': 'Aylık Yedek'
        }

        backup_type = backup_types.get(backup_frequency, 'Otomatik Yedek')

        return self.create_backup_record(
            company_id=company_id,
            backup_name=backup_name,
            backup_type=backup_type,
            backup_status='scheduled'
        )
