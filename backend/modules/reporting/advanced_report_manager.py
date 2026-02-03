#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Rapor Yönetim Sistemi - TAM VE EKSİKSİZ
Zamanlanmış raporlar, email gönderimi, rapor merkezi
"""

import logging
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config.database import DB_PATH


class AdvancedReportManager:
    """Gelişmiş rapor yönetimi"""

    # Modül bazlı rapor klasörleri
    MODULE_REPORT_FOLDERS = {
        "sdg": "reports/sdg",
        "gri": "reports/gri",
        "tcfd": "reports/tcfd",
        "sasb": "reports/sasb",
        "ungc": "reports/ungc",
        "cdp": "reports/cdp",
        "iirc": "reports/iirc",
        "issb": "reports/issb",
        "ifrs": "reports/ifrs",
        "tsrs": "reports/tsrs",
        "esrs": "reports/esrs",
        "csrd": "reports/csrd",
        "ai": "reports/ai",
        "esg": "reports/esg",
        "karbon": "reports/karbon",
        "enerji": "reports/enerji",
        "su": "reports/su",
        "atik": "reports/atik",
        "sosyal": "reports/sosyal",
        "genel": "reports/genel"
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.base_dir = os.path.dirname(db_path)

        # Rapor klasörlerini oluştur
        self._create_report_folders()
        self._init_report_tables()

    def _create_report_folders(self) -> None:
        """Modül bazlı rapor klasörlerini oluştur"""
        for module_code, folder_path in self.MODULE_REPORT_FOLDERS.items():
            full_path = os.path.join(self.base_dir, folder_path)
            os.makedirs(full_path, exist_ok=True)

    def _init_report_tables(self) -> None:
        """Rapor tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Rapor kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    reporting_period TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    tags TEXT,
                    description TEXT
                )
            """)

            # Zamanlanmış raporlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    schedule_frequency TEXT NOT NULL,
                    schedule_day INTEGER,
                    schedule_time TEXT,
                    last_generated TIMESTAMP,
                    next_generation TIMESTAMP,
                    email_recipients TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Email rapor geçmişi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_email_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    recipient_email TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'gonderildi',
                    error_message TEXT,
                    FOREIGN KEY (report_id) REFERENCES report_registry(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Rapor yonetim tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Rapor tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    def save_report(self, company_id: int, module_code: str, report_name: str,
                   report_type: str, source_file: str, reporting_period: str = "",
                   tags: Optional[List[str]] = None, description: str = "") -> Optional[int]:
        """
        Raporu kaydet
        
        Args:
            company_id: Şirket ID
            module_code: Modül kodu (sdg, gri, vb.)
            report_name: Rapor adı
            report_type: Rapor türü (pdf, excel, word, ppt)
            source_file: Kaynak dosya yolu
            reporting_period: Raporlama dönemi
            tags: Etiketler
            description: Açıklama
            
        Returns:
            Rapor ID
        """
        try:
            # Hedef klasörü belirle
            if module_code not in self.MODULE_REPORT_FOLDERS:
                module_code = "genel"

            folder_path = os.path.join(self.base_dir, self.MODULE_REPORT_FOLDERS[module_code])

            # Dosya adı oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(source_file)[1]
            safe_name = report_name.replace(' ', '_').replace('/', '_')
            dest_filename = f"{safe_name}_{timestamp}{file_ext}"
            dest_path = os.path.join(folder_path, dest_filename)

            # Dosyayı kopyala
            shutil.copy2(source_file, dest_path)

            # Dosya boyutu
            file_size = os.path.getsize(dest_path)

            # Veritabanına kaydet
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            tags_json = json.dumps(tags) if tags else None

            cursor.execute("""
                INSERT INTO report_registry
                (company_id, module_code, report_name, report_type, file_path,
                 file_size, reporting_period, tags, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, module_code, report_name, report_type, dest_path,
                  file_size, reporting_period, tags_json, description))

            report_id = cursor.lastrowid

            conn.commit()
            conn.close()

            logging.info(f"[OK] Rapor kaydedildi: {dest_filename}")
            return report_id

        except Exception as e:
            logging.error(f"Rapor kaydetme hatasi: {e}")
            return None

    def get_module_reports(self, company_id: int, module_code: str) -> List[Dict]:
        """Modül raporlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM report_registry
                WHERE company_id = ? AND module_code = ?
                ORDER BY created_at DESC
            """, (company_id, module_code))

            columns = [col[0] for col in cursor.description]
            reports = []

            for row in cursor.fetchall():
                report = dict(zip(columns, row))
                # Dosya varlığını kontrol et
                if os.path.exists(report['file_path']):
                    reports.append(report)

            return reports

        except Exception as e:
            logging.error(f"Raporlar getirme hatasi: {e}")
            return []
        finally:
            conn.close()

    def delete_reports(self, report_ids: List[int], company_id: int) -> Tuple[int, int]:
        """
        Raporları sil (toplu silme destekli)
        
        Args:
            report_ids: Silinecek rapor ID'leri
            company_id: Şirket ID (Güvenlik için zorunlu)
            
        Returns:
            (silinen_sayisi, hata_sayisi)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        deleted_count = 0
        error_count = 0

        try:
            for report_id in report_ids:
                try:
                    # Rapor bilgisini al (Sadece ilgili şirketin raporu)
                    cursor.execute("""
                        SELECT file_path FROM report_registry WHERE id = ? AND company_id = ?
                    """, (report_id, company_id))

                    result = cursor.fetchone()
                    if result:
                        file_path = result[0]

                        # Dosyayı sil
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except OSError:
                                pass # Dosya yoksa veya silinemezse devam et

                        # Veritabanından sil
                        cursor.execute("""
                            DELETE FROM report_registry WHERE id = ? AND company_id = ?
                        """, (report_id, company_id))

                        deleted_count += 1
                    else:
                        # Rapor bulunamadı veya şirkete ait değil
                        error_count += 1

                except Exception as e:
                    logging.error(f"Rapor silme hatasi (ID: {report_id}): {e}")
                    error_count += 1

            conn.commit()
            return (deleted_count, error_count)

        except Exception as e:
            logging.error(f"Toplu silme hatasi: {e}")
            return (deleted_count, error_count)
        finally:
            conn.close()

    def register_existing_file(self, company_id: int, module_code: str, report_name: str,
                               report_type: str, file_path: str, reporting_period: str = "",
                               tags: Optional[List[str]] = None, description: str = "") -> Optional[int]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if not os.path.exists(file_path):
                return None
            file_size = os.path.getsize(file_path)
            tags_json = json.dumps(tags) if tags else None
            if module_code not in self.MODULE_REPORT_FOLDERS:
                module_code = "genel"
            cursor.execute(
                """
                INSERT INTO report_registry
                (company_id, module_code, report_name, report_type, file_path,
                 file_size, reporting_period, tags, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (company_id, module_code, report_name, report_type, file_path,
                 file_size, reporting_period, tags_json, description)
            )
            report_id = cursor.lastrowid
            conn.commit()
            return report_id
        except Exception:
            return None
        finally:
            conn.close()

    def schedule_report(self, company_id: int, module_code: str,
                       report_type: str, frequency: str,
                       schedule_time: str = "09:00",
                       email_recipients: Optional[List[str]] = None) -> bool:
        """
        Rapor zamanla
        
        Args:
            frequency: gunluk, haftalik, aylik, ceyreklik, yillik
            schedule_time: Saat (HH:MM)
            email_recipients: Email adresleri
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Bir sonraki oluşturma zamanını hesapla
            next_gen = self._calculate_next_generation(frequency, schedule_time)

            recipients_json = json.dumps(email_recipients) if email_recipients else None

            cursor.execute("""
                INSERT INTO scheduled_reports
                (company_id, module_code, report_type, schedule_frequency,
                 schedule_time, next_generation, email_recipients)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, module_code, report_type, frequency,
                  schedule_time, next_gen, recipients_json))

            conn.commit()
            logging.info(f"[OK] Rapor zamanlandı: {frequency}")
            return True

        except Exception as e:
            logging.error(f"Rapor zamanlama hatasi: {e}")
            return False
        finally:
            conn.close()

    def _calculate_next_generation(self, frequency: str,
                                   schedule_time: str) -> datetime:
        """Bir sonraki oluşturma zamanını hesapla"""
        now = datetime.now()
        hour, minute = map(int, schedule_time.split(':'))

        next_gen = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if frequency == "gunluk":
            if next_gen <= now:
                next_gen += timedelta(days=1)
        elif frequency == "haftalik":
            days_ahead = 7 - now.weekday()  # Pazartesi
            next_gen += timedelta(days=days_ahead)
        elif frequency == "aylik":
            # Ayın ilk günü
            if now.day > 1:
                next_month = now.month + 1 if now.month < 12 else 1
                next_year = now.year if now.month < 12 else now.year + 1
                next_gen = next_gen.replace(year=next_year, month=next_month, day=1)
        elif frequency == "ceyreklik":
            # Çeyrek başı
            current_quarter = (now.month - 1) // 3
            next_quarter_month = (current_quarter + 1) * 3 + 1
            if next_quarter_month > 12:
                next_quarter_month = 1
                next_gen = next_gen.replace(year=now.year + 1, month=1, day=1)
            else:
                next_gen = next_gen.replace(month=next_quarter_month, day=1)
        elif frequency == "yillik":
            # Yılbaşı
            next_gen = next_gen.replace(year=now.year + 1, month=1, day=1)

        return next_gen
