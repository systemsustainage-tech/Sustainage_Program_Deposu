#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Sync Yönetimi Modülü
Bulut senkronizasyonu ve veri yedekleme
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class CloudSyncManager:
    """Bulut senkronizasyonu ve veri yedekleme"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Cloud sync tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            cursor.execute("""
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
            """)

            conn.commit()
            logging.info("[OK] Cloud sync yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Cloud sync yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_cloud_provider(self, company_id: int, provider_name: str, provider_type: str,
                          access_key: str = None, secret_key: str = None,
                          bucket_name: str = None, region: str = None) -> bool:
        """Bulut sağlayıcısı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO cloud_providers 
                (company_id, provider_name, provider_type, access_key, secret_key,
                 bucket_name, region)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, provider_name, provider_type, access_key, secret_key,
                  bucket_name, region))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Bulut sağlayıcısı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_sync_job(self, company_id: int, job_name: str, job_type: str,
                       source_path: str, destination_path: str,
                       sync_frequency: str = None) -> bool:
        """Senkronizasyon işi oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sync_jobs 
                (company_id, job_name, job_type, source_path, destination_path, sync_frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, job_name, job_type, source_path, destination_path, sync_frequency))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Senkronizasyon işi oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_backup_record(self, company_id: int, backup_name: str, backup_type: str,
                           file_size: int = None, backup_location: str = None,
                           backup_status: str = 'completed') -> bool:
        """Yedekleme kaydı oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO backup_records 
                (company_id, backup_name, backup_type, file_size, backup_location, backup_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, backup_name, backup_type, file_size, backup_location, backup_status))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yedekleme kaydı oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_cloud_sync_summary(self, company_id: int) -> Dict:
        """Cloud sync özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Bulut sağlayıcıları
            cursor.execute("""
                SELECT provider_name, provider_type, status
                FROM cloud_providers 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            providers = []
            for row in cursor.fetchall():
                providers.append({
                    'provider_name': row[0],
                    'provider_type': row[1],
                    'status': row[2]
                })

            # Senkronizasyon işleri
            cursor.execute("""
                SELECT job_name, job_type, sync_frequency, last_sync, status
                FROM sync_jobs 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            sync_jobs = []
            for row in cursor.fetchall():
                sync_jobs.append({
                    'job_name': row[0],
                    'job_type': row[1],
                    'sync_frequency': row[2],
                    'last_sync': row[3],
                    'status': row[4]
                })

            # Yedekleme kayıtları
            cursor.execute("""
                SELECT backup_type, COUNT(*), SUM(file_size), 
                       SUM(CASE WHEN backup_status = 'completed' THEN 1 ELSE 0 END)
                FROM backup_records 
                WHERE company_id = ? AND created_at >= datetime('now', '-30 days')
                GROUP BY backup_type
            """, (company_id,))

            backup_summary = {}
            total_backups = 0
            total_size = 0
            successful_backups = 0

            for row in cursor.fetchall():
                backup_type, count, size, successful = row
                backup_summary[backup_type] = {
                    'count': count,
                    'size': size or 0,
                    'successful': successful
                }
                total_backups += count
                total_size += size or 0
                successful_backups += successful

            return {
                'providers': providers,
                'sync_jobs': sync_jobs,
                'backup_summary': backup_summary,
                'total_backups_30d': total_backups,
                'total_backup_size': total_size,
                'successful_backups': successful_backups,
                'backup_success_rate': (successful_backups / total_backups * 100) if total_backups > 0 else 0,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Cloud sync özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

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
