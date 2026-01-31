#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otomatik Yedekleme ve Kurtarma Sistemi
Veritabanı ve dosya yedekleme, zamanlı otomatik backup, kurtarma
"""

import logging
import json
import os
import shutil
import sqlite3
import threading
import time
import zipfile
from datetime import datetime
from typing import Dict, List, Tuple

import schedule


class BackupRecoveryManager:
    """Yedekleme ve kurtarma yöneticisi"""
    
    def __init__(self, db_path: str, backup_dir: str = "data/backups") -> None:
        """
        Args:
            db_path: Ana veritabanı yolu
            backup_dir: Yedekleme klasörü
        """
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.backup_config_file = os.path.join(backup_dir, 'backup_config.json')
        
        os.makedirs(backup_dir, exist_ok=True)
        self._init_backup_config()
        self._init_backup_tables()
    
    def _init_backup_config(self) -> None:
        """Yedekleme yapılandırması"""
        default_config = {
            'auto_backup_enabled': True,
            'backup_frequency': 'daily',  # daily, weekly, monthly
            'backup_time': '02:00',  # 02:00 AM
            'max_backups': 30,  # En fazla 30 yedek sakla
            'compress_backups': True,
            'include_files': True,  # Dosyaları da yedekle
            'last_backup': None
        }
        
        if not os.path.exists(self.backup_config_file):
            with open(self.backup_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
    
    def _init_backup_tables(self) -> None:
        """Yedekleme log tablosu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_name TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    backup_size INTEGER,
                    backup_path TEXT NOT NULL,
                    backup_date TEXT NOT NULL,
                    status TEXT DEFAULT 'completed',
                    error_message TEXT,
                    created_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recovery_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id INTEGER NOT NULL,
                    recovery_date TEXT NOT NULL,
                    recovery_status TEXT NOT NULL,
                    recovered_by TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (backup_id) REFERENCES backup_history(id)
                )
            """)
            
            conn.commit()
            logging.info("[OK] Backup tabloları hazır")
            
        except Exception as e:
            logging.error(f"[HATA] Backup tablo oluşturma: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def create_backup(self, backup_type: str = 'full', 
                     created_by: str = 'system',
                     include_files: bool = True) -> Tuple[bool, str]:
        """
        Yedekleme oluştur
        
        Args:
            backup_type: 'full', 'database_only', 'files_only'
            created_by: Kim oluşturdu
            include_files: Dosyaları dahil et
        
        Returns:
            Tuple[bool, str]: (Başarı, backup dosya yolu veya hata mesajı)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{backup_type}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            # Zip dosyası oluştur
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # Veritabanını yedekle
                if backup_type in ['full', 'database_only']:
                    if os.path.exists(self.db_path):
                        zipf.write(self.db_path, 'database/sdg_desktop.sqlite')
                        logging.info("[OK] Veritabanı yedeklendi")
                
                # Dosyaları yedekle
                if include_files and backup_type in ['full', 'files_only']:
                    self._backup_files(zipf)
                
                # Konfigurasyon dosyalarını yedekle
                self._backup_config_files(zipf)
            
            # Dosya boyutu
            backup_size = os.path.getsize(backup_path)
            
            # Log kaydet
            self._log_backup(backup_name, backup_type, backup_size, backup_path, 
                           'completed', created_by=created_by)
            
            # Eski yedekleri temizle
            self.cleanup_old_backups()
            
            logging.info(f"[OK] Yedekleme başarılı: {backup_path}")
            return True, backup_path
            
        except Exception as e:
            error_msg = f"Yedekleme hatası: {e}"
            logging.error(f"[HATA] {error_msg}")
            
            # Hata logu
            try:
                self._log_backup(backup_name, backup_type, 0, '', 'failed',
                               error_message=str(e), created_by=created_by)
            except Exception as log_error:
                logging.error(f"[UYARI] Log kaydedilemedi: {log_error}")
            
            return False, error_msg
    
    def _backup_files(self, zipf: zipfile.ZipFile) -> None:
        """Dosyaları yedekle - İzin hatalarını güvenli şekilde işle"""
        file_dirs = ['uploads', 'exports', 'reports', 'resimler']
        backup_errors = []
        
        for dir_name in file_dirs:
            dir_path = os.path.join(os.path.dirname(self.db_path), '..', dir_name)
            if os.path.exists(dir_path):
                try:
                    for root, dirs, files in os.walk(dir_path):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                # Dosya okunabilir mi kontrol et
                                if os.access(file_path, os.R_OK):
                                    arcname = os.path.join('files', dir_name, 
                                                          os.path.relpath(file_path, dir_path))
                                    zipf.write(file_path, arcname)
                                else:
                                    backup_errors.append(f"Okuma izni yok: {file_path}")
                            except (PermissionError, OSError) as e:
                                backup_errors.append(f"İzin hatası {file_path}: {e}")
                                continue
                except (PermissionError, OSError) as e:
                    backup_errors.append(f"Klasör erişim hatası {dir_path}: {e}")
                    continue
        
        if backup_errors:
            logging.error(f"[UYARI] {len(backup_errors)} dosya yedeklenemedi:")
            for error in backup_errors[:10]:  # İlk 10 hatayı göster
                logging.error(f"  - {error}")
            if len(backup_errors) > 10:
                logging.error(f"  ... ve {len(backup_errors) - 10} hata daha")
        else:
            logging.info("[OK] Dosyalar yedeklendi")
    
    def _backup_config_files(self, zipf: zipfile.ZipFile) -> None:
        """Konfigurasyon dosyalarını yedekle"""
        config_dir = os.path.join(os.path.dirname(self.db_path), '..', 'config')
        
        if os.path.exists(config_dir):
            for file in os.listdir(config_dir):
                if file.endswith(('.json', '.txt', '.csv')):
                    file_path = os.path.join(config_dir, file)
                    zipf.write(file_path, f'config/{file}')
        
        logging.info("[OK] Konfigürasyonlar yedeklendi")
    
    def _log_backup(self, backup_name: str, backup_type: str, 
                   backup_size: int, backup_path: str, status: str,
                   error_message: str = None, created_by: str = 'system'):
        """Yedekleme logunu kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO backup_history 
                (backup_name, backup_type, backup_size, backup_path, backup_date,
                 status, error_message, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (backup_name, backup_type, backup_size, backup_path,
                  datetime.now().isoformat(), status, error_message, created_by))
            
            conn.commit()
        except Exception as e:
            logging.error(f"Log kayıt hatası: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def restore_backup(self, backup_path: str, restored_by: str = 'system') -> Tuple[bool, str]:
        """
        Yedekten geri yükle
        
        Args:
            backup_path: Yedek dosya yolu
            restored_by: Kim geri yüklüyor
        
        Returns:
            Tuple[bool, str]: (Başarı, mesaj)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Yedek dosyası bulunamadı"
            
            # Önce mevcut veritabanının yedeğini al
            safety_backup = f"{self.db_path}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(self.db_path, safety_backup)
            
            # Zip'i aç
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Veritabanını geri yükle
                if 'database/sdg_desktop.sqlite' in zipf.namelist():
                    zipf.extract('database/sdg_desktop.sqlite', self.backup_dir)
                    extracted_db = os.path.join(self.backup_dir, 'database', 'sdg_desktop.sqlite')
                    shutil.copy2(extracted_db, self.db_path)
                    logging.info("[OK] Veritabanı geri yüklendi")
                
                # Dosyaları geri yükle (opsiyonel)
                try:
                    file_prefix = 'files/'
                    config_prefix = 'config/'

                    names = zipf.namelist()

                    # Dosya klasörlerini geri yükle (uploads, exports, reports, resimler)
                    for name in names:
                        if name.startswith(file_prefix) and not name.endswith('/'):
                            # files/<dir>/<relative_path>
                            parts = name.split('/')
                            if len(parts) >= 3:
                                dir_name = parts[1]
                                rel_path = '/'.join(parts[2:])

                                # Hedef kök: db_path'in bir üstü (../<dir_name>)
                                target_root = os.path.join(os.path.dirname(self.db_path), '..', dir_name)
                                target_path = os.path.join(target_root, rel_path)

                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                # Zip içinden ilgili dosyayı temp'e çıkarıp kopyala
                                extract_tmp = os.path.join(self.backup_dir, 'restore_tmp')
                                os.makedirs(extract_tmp, exist_ok=True)
                                tmp_out = zipf.extract(name, extract_tmp)
                                shutil.copy2(tmp_out, target_path)
                    logging.info("[OK] Dosyalar geri yüklendi")

                    # Konfigürasyon dosyalarını geri yükle (config/*.json, *.txt, *.csv)
                    config_dir = os.path.join(os.path.dirname(self.db_path), '..', 'config')
                    os.makedirs(config_dir, exist_ok=True)

                    for name in names:
                        if name.startswith(config_prefix) and not name.endswith('/'):
                            # Zipten çıkar ve config altına kopyala
                            extract_tmp = os.path.join(self.backup_dir, 'restore_tmp_cfg')
                            os.makedirs(extract_tmp, exist_ok=True)
                            tmp_out = zipf.extract(name, extract_tmp)
                            base_name = os.path.basename(name)
                            target_path = os.path.join(config_dir, base_name)
                            shutil.copy2(tmp_out, target_path)
                    logging.info("[OK] Konfigürasyonlar geri yüklendi")
                except Exception as fe:
                    # Dosya geri yükleme hataları geri yüklemeyi tamamen bozmasın
                    logging.error(f"[UYARI] Dosya geri yükleme sırasında hata: {fe}")
            
            # Recovery log kaydet
            self._log_recovery(backup_path, 'success', restored_by)
            
            return True, f"Yedek başarıyla geri yüklendi. Güvenlik yedeği: {safety_backup}"
            
        except Exception as e:
            error_msg = f"Geri yükleme hatası: {e}"
            logging.error(f"[HATA] {error_msg}")
            self._log_recovery(backup_path, 'failed', restored_by, notes=str(e))
            return False, error_msg
    
    def _log_recovery(self, backup_path: str, status: str, 
                     restored_by: str, notes: str = None):
        """Kurtarma logunu kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Backup ID bul
            cursor.execute("SELECT id FROM backup_history WHERE backup_path = ?", (backup_path,))
            result = cursor.fetchone()
            backup_id = result[0] if result else 0
            
            cursor.execute("""
                INSERT INTO recovery_history 
                (backup_id, recovery_date, recovery_status, recovered_by, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (backup_id, datetime.now().isoformat(), status, restored_by, notes))
            
            conn.commit()
        except Exception as e:
            logging.error(f"Recovery log hatası: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_backup_list(self, limit: int = 50) -> List[Dict]:
        """Yedek listesini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, backup_name, backup_type, backup_size, backup_path,
                       backup_date, status, created_by
                FROM backup_history
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            
            backups = []
            for row in cursor.fetchall():
                backups.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'size': row[3],
                    'path': row[4],
                    'date': row[5],
                    'status': row[6],
                    'created_by': row[7]
                })
            
            return backups
            
        finally:
            conn.close()
    
    def cleanup_old_backups(self) -> None:
        """Eski yedekleri temizle"""
        try:
            config = self.get_backup_config()
            max_backups = config.get('max_backups', 30)
            
            # Yedek listesini al
            all_backups = sorted(
                [f for f in os.listdir(self.backup_dir) if f.startswith('backup_') and f.endswith('.zip')],
                reverse=True
            )
            
            # Fazla yedekleri sil
            if len(all_backups) > max_backups:
                for backup_file in all_backups[max_backups:]:
                    backup_path = os.path.join(self.backup_dir, backup_file)
                    os.remove(backup_path)
                    logging.info(f"[OK] Eski yedek silindi: {backup_file}")
        
        except Exception as e:
            logging.error(f"[HATA] Yedek temizleme: {e}")
    
    def get_backup_config(self) -> Dict:
        """Yedekleme yapılandırmasını getir"""
        try:
            with open(self.backup_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.info(f"[UYARI] Yedekleme yapılandırması okunamadı, varsayılanlar kullanılıyor: {e}")
            return {
                'auto_backup_enabled': True,
                'backup_frequency': 'daily',
                'backup_time': '02:00',
                'max_backups': 30
            }
    
    def update_backup_config(self, config: Dict) -> bool:
        """Yedekleme yapılandırmasını güncelle"""
        try:
            with open(self.backup_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Config güncelleme hatası: {e}")
            return False
    
    def schedule_automatic_backups(self) -> None:
        """Otomatik yedekleme zamanla"""
        config = self.get_backup_config()
        
        if not config.get('auto_backup_enabled'):
            logging.info("[INFO] Otomatik yedekleme devre dışı")
            return
        
        backup_time = config.get('backup_time', '02:00')
        frequency = config.get('backup_frequency', 'daily')
        
        # Zamanlama
        if frequency == 'daily':
            schedule.every().day.at(backup_time).do(self._scheduled_backup)
            logging.info(f"[OK] Günlük yedekleme zamanlandı: {backup_time}")
        
        elif frequency == 'weekly':
            schedule.every().sunday.at(backup_time).do(self._scheduled_backup)
            logging.info(f"[OK] Haftalık yedekleme zamanlandı: Pazar {backup_time}")
        
        elif frequency == 'monthly':
            # Her ayın 1'i
            schedule.every().day.at(backup_time).do(self._check_monthly_backup)
            logging.info(f"[OK] Aylık yedekleme zamanlandı: Her ay 1'i {backup_time}")
        
        # Background thread başlat
        self.stop_event = threading.Event()
        
        def run_scheduler() -> None:
            while not self.stop_event.is_set():
                schedule.run_pending()
                self.stop_event.wait(60)  # Her dakika kontrol et (interruptible)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        logging.info("[OK] Otomatik yedekleme thread başlatıldı")
    
    def _scheduled_backup(self) -> None:
        """Zamanlanmış yedekleme"""
        logging.info(f"[INFO] Otomatik yedekleme başlatılıyor: {datetime.now()}")
        success, message = self.create_backup(backup_type='full', created_by='auto_scheduler')
        
        if success:
            logging.info(f"[OK] Otomatik yedekleme tamamlandı: {message}")
        else:
            logging.error(f"[HATA] Otomatik yedekleme başarısız: {message}")
    
    def _check_monthly_backup(self) -> None:
        """Aylık yedekleme kontrolü"""
        if datetime.now().day == 1:
            self._scheduled_backup()
    
    def get_backup_statistics(self) -> Dict:
        """Yedekleme istatistikleri"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Toplam yedek sayısı
            cursor.execute("SELECT COUNT(*) FROM backup_history")
            total_backups = cursor.fetchone()[0]
            
            # Başarılı yedekler
            cursor.execute("SELECT COUNT(*) FROM backup_history WHERE status = 'completed'")
            successful_backups = cursor.fetchone()[0]
            
            # Toplam yedek boyutu
            cursor.execute("SELECT SUM(backup_size) FROM backup_history WHERE status = 'completed'")
            total_size = cursor.fetchone()[0] or 0
            
            # Son yedek
            cursor.execute("""
                SELECT backup_name, backup_date FROM backup_history 
                WHERE status = 'completed'
                ORDER BY id DESC LIMIT 1
            """)
            last_backup = cursor.fetchone()
            
            return {
                'total_backups': total_backups,
                'successful_backups': successful_backups,
                'failed_backups': total_backups - successful_backups,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'last_backup_name': last_backup[0] if last_backup else 'N/A',
                'last_backup_date': last_backup[1] if last_backup else 'N/A'
            }
            
        finally:
            conn.close()
    
    def verify_backup(self, backup_path: str) -> Tuple[bool, str]:
        """
        Yedek dosyasını doğrula
        
        Returns:
            Tuple[bool, str]: (Geçerli mi, mesaj)
        """
        try:
            if not os.path.exists(backup_path):
                return False, "Dosya bulunamadı"
            
            # Zip dosyası geçerli mi?
            if not zipfile.is_zipfile(backup_path):
                return False, "Geçersiz zip dosyası"
            
            # İçeriği kontrol et
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                files = zipf.namelist()
                
                # Veritabanı var mı?
                has_db = any('sdg_desktop.sqlite' in f for f in files)
                
                if not has_db:
                    return False, "Veritabanı bulunamadı"
                
                # Zip bozuk mu?
                bad_file = zipf.testzip()
                if bad_file:
                    return False, f"Bozuk dosya bulundu: {bad_file}"
            
            return True, "Yedek dosyası geçerli"
            
        except Exception as e:
            return False, f"Doğrulama hatası: {e}"
    
    def export_backup_report(self) -> str:
        """Yedekleme raporu oluştur"""
        stats = self.get_backup_statistics()
        config = self.get_backup_config()
        backups = self.get_backup_list(20)
        
        report = f"""# YEDEKLEME SİSTEMİ RAPORU

## Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}

## İSTATİSTİKLER

- **Toplam Yedek:** {stats['total_backups']}
- **Başarılı:** {stats['successful_backups']}
- **Başarısız:** {stats['failed_backups']}
- **Toplam Boyut:** {stats['total_size_mb']} MB
- **Son Yedek:** {stats['last_backup_name']}
- **Son Yedek Tarihi:** {stats['last_backup_date']}

## YAPILANDIRMA

- **Otomatik Yedekleme:** {'Aktif' if config.get('auto_backup_enabled') else 'Pasif'}
- **Sıklık:** {config.get('backup_frequency', 'N/A').title()}
- **Zaman:** {config.get('backup_time', 'N/A')}
- **Maksimum Yedek:** {config.get('max_backups', 'N/A')}
- **Sıkıştırma:** {'Evet' if config.get('compress_backups') else 'Hayır'}

## SON 20 YEDEK

"""
        for i, backup in enumerate(backups, 1):
            size_mb = round(backup['size'] / (1024 * 1024), 2) if backup['size'] else 0
            status_icon = '' if backup['status'] == 'completed' else ''
            report += f"{i}. {status_icon} {backup['name']} - {size_mb} MB - {backup['date']}\n"
        
        return report

