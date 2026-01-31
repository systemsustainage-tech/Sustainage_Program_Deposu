#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 2025 Revizyon Senkronizasyon Aracı (Remote Server)
2025 SDG gösterge revizyonu ile mevcut verilerin senkronizasyonu
"""

import os
import sqlite3
import sys
import logging
from datetime import datetime
from typing import Dict, List

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class SDG2025SyncRemote:
    """SDG 2025 senkronizasyon yöneticisi (Remote)"""
    
    def __init__(self) -> None:
        self.db_path = self._find_db_path()
        
        # 2025 revizyonu değişiklikleri (Masaüstü sürümünden alındı)
        self.revision_2025 = {
            'added_indicators': [
                {
                    'code': '1.1.2',
                    'goal_id': 1,
                    'target': '1.1',
                    'description': 'Ulusal yoksulluk sınırının altında yaşayan nüfusun oranı',
                    'revision_note': '2025 revizyonunda eklendi',
                    'status': 'new'
                },
                {
                    'code': '13.2.3',
                    'goal_id': 13,
                    'target': '13.2',
                    'description': 'İklim değişikliği uyum planlarının uygulanma durumu',
                    'revision_note': '2025 revizyonunda eklendi',
                    'status': 'new'
                }
            ],
            'modified_indicators': [
                {
                    'code': '6.3.1',
                    'old_description': 'Güvenli arıtılmış atık su oranı',
                    'new_description': 'Güvenli arıtılmış evsel ve endüstriyel atık su oranı',
                    'revision_note': 'Tanım genişletildi - 2025',
                    'status': 'modified'
                },
                {
                    'code': '12.3.1',
                    'old_description': 'Küresel gıda kaybı endeksi',
                    'new_description': 'Gıda kaybı ve israfı endeksi (üretimden tüketime)',
                    'revision_note': 'Kapsam genişletildi - 2025',
                    'status': 'modified'
                }
            ],
            'deprecated_indicators': [
                {
                    'code': '17.18.2',
                    'reason': '17.18.1 ile birleştirildi',
                    'replacement': '17.18.1',
                    'revision_note': '2025 revizyonunda birleştirildi',
                    'status': 'deprecated'
                }
            ],
            'tier_changes': [
                {
                    'code': '11.6.2',
                    'old_tier': 'III',
                    'new_tier': 'II',
                    'reason': 'Veri metodolojisi geliştirildi',
                    'status': 'tier_upgraded'
                }
            ]
        }
    
    def _find_db_path(self) -> str:
        """Olası veritabanı yollarını kontrol et"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidates = [
            os.path.join(base_dir, 'backend', 'data', 'sdg_desktop.sqlite'),
            os.path.join(base_dir, 'instance', 'sustainage.sqlite'),
            os.path.join(base_dir, 'sustainage.db'),
            '/var/www/sustainage/backend/data/sdg_desktop.sqlite',
            '/var/www/sustainage/instance/sustainage.sqlite'
        ]
        
        for path in candidates:
            if os.path.exists(path):
                logging.info(f"Veritabanı bulundu: {path}")
                return path
        
        logging.error("Veritabanı bulunamadı!")
        sys.exit(1)

    def get_connection(self):
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def backup_database(self) -> str:
        """Veritabanını yedekle"""
        try:
            import shutil
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_path = os.path.join(backup_dir, f'sdg_pre_2025_sync_{timestamp}.sqlite')
            shutil.copy2(self.db_path, backup_path)
            
            logging.info(f"Veritabanı yedeklendi: {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"Yedekleme hatası: {e}")
            return None

    def _get_target_id(self, cursor, target_code: str) -> int:
        """Target kodundan ID bul"""
        cursor.execute("SELECT id FROM sdg_targets WHERE code = ?", (target_code,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None

    def apply_2025_revision(self, dry_run: bool = False) -> None:
        """2025 revizyonunu uygula"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Yeni göstergeler
            for item in self.revision_2025['added_indicators']:
                logging.info(f"Eklenecek: {item['code']}")
                if not dry_run:
                    # Target ID bul
                    target_id = self._get_target_id(cursor, item['target'])
                    if not target_id:
                        logging.warning(f"-> Target bulunamadı: {item['target']} (Gösterge: {item['code']})")
                        continue

                    # Gösterge var mı kontrol et
                    cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (item['code'],))
                    if not cursor.fetchone():
                        # Şemaya uygun INSERT (title_tr kullanılıyor, description değil)
                        cursor.execute("""
                            INSERT INTO sdg_indicators (target_id, code, title_tr, created_at)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        """, (target_id, item['code'], item['description']))
                        logging.info(f"-> Eklendi: {item['code']} (Target ID: {target_id})")
                    else:
                        logging.info(f"-> Zaten mevcut: {item['code']}")

            # 2. Güncellenen göstergeler
            for item in self.revision_2025['modified_indicators']:
                logging.info(f"Güncellenecek: {item['code']}")
                if not dry_run:
                    # description yerine title_tr kullanıyoruz
                    cursor.execute("""
                        UPDATE sdg_indicators 
                        SET title_tr = ? 
                        WHERE code = ?
                    """, (item['new_description'], item['code']))
                    if cursor.rowcount > 0:
                        logging.info(f"-> Güncellendi: {item['code']}")
                    else:
                        logging.warning(f"-> Bulunamadı: {item['code']}")

            # 3. Kaldırılan göstergeler (Soft delete veya işaretleme)
            for item in self.revision_2025['deprecated_indicators']:
                logging.info(f"Kaldırılacak (Deprecated): {item['code']}")
                if not dry_run:
                    cursor.execute("""
                        UPDATE sdg_indicators 
                        SET title_tr = title_tr || ' (DEPRECATED: ' || ? || ')'
                        WHERE code = ? AND title_tr NOT LIKE '%(DEPRECATED%'
                    """, (item['reason'], item['code']))
                    if cursor.rowcount > 0:
                        logging.info(f"-> İşaretlendi: {item['code']}")

            conn.commit()
            logging.info("2025 Revizyonu başarıyla uygulandı.")
            
        except Exception as e:
            logging.error(f"Uygulama hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    try:
        syncer = SDG2025SyncRemote()
        
        # Önce yedekle
        if syncer.backup_database():
            # Uygula
            syncer.apply_2025_revision(dry_run=False)
        else:
            logging.error("Yedekleme başarısız olduğu için işlem iptal edildi.")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Kritik hata: {e}")
        sys.exit(1)
