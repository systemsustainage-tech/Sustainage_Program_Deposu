#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OTOMATİK RAPOR GÖNDERİMİ SİSTEMİ
=================================

Zaman aralığı raporları ve paydaş bildirimleri için otomatik sistem
"""

import logging
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from services.email_service import EmailService

@dataclass
class ReportSchedule:
    """Rapor zamanlaması veri yapısı"""
    id: str
    company_id: int
    report_type: str  # sdg, gri, tsrs, carbon, etc.
    frequency: str  # daily, weekly, monthly, quarterly, yearly
    day_of_week: int  # 0-6 (Monday-Sunday)
    day_of_month: int  # 1-31
    hour: int  # 0-23
    minute: int  # 0-59
    recipients: List[str]
    subject_template: str
    body_template: str
    is_active: bool
    last_sent: Optional[datetime]
    next_send: Optional[datetime]

@dataclass
class Stakeholder:
    """Paydaş veri yapısı"""
    id: str
    company_id: int
    name: str
    email: str
    role: str  # investor, customer, supplier, employee, etc.
    report_preferences: List[str]  # report types they want
    language: str
    timezone: str
    is_active: bool

class AutomatedReportingSystem:
    """Otomatik rapor gönderimi sistemi"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or 'data/sdg_desktop.db'
        self.email_service = EmailService(self.db_path)
        self._create_tables()

    def _create_tables(self):
        """Otomatik raporlama tablolarını oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Rapor zamanlamaları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_schedules (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    day_of_week INTEGER DEFAULT 1,
                    day_of_month INTEGER DEFAULT 1,
                    hour INTEGER DEFAULT 9,
                    minute INTEGER DEFAULT 0,
                    recipients TEXT NOT NULL,
                    subject_template TEXT NOT NULL,
                    body_template TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    last_sent TEXT,
                    next_send TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # Paydaşlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stakeholders (
                    id TEXT PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    report_preferences TEXT NOT NULL,
                    language TEXT DEFAULT 'tr',
                    timezone TEXT DEFAULT 'Europe/Istanbul',
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # Rapor geçmişi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_history (
                    id TEXT PRIMARY KEY,
                    schedule_id TEXT NOT NULL,
                    company_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    recipients TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    status TEXT DEFAULT 'sent',
                    error_message TEXT,
                    file_path TEXT,
                    FOREIGN KEY(schedule_id) REFERENCES report_schedules(id),
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """)

            # E-posta şablonları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id TEXT PRIMARY KEY,
                    template_name TEXT NOT NULL,
                    language TEXT DEFAULT 'tr',
                    subject_template TEXT NOT NULL,
                    body_template TEXT NOT NULL,
                    report_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Otomatik raporlama tabloları oluşturulamadı: {e}")

    def _load_smtp_config(self) -> Dict[str, Any]:
        """SMTP yapılandırmasını yükle"""
        try:
            # backend/config/smtp_config.json yolunu kullan
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'smtp_config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Varsayılan yapılandırma
                return {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'use_tls': True,
                    'from_email': '',
                    'from_name': 'SUSTAINAGE SDG'
                }
        except Exception as e:
            logging.error(f"[HATA] SMTP yapılandırması yüklenemedi: {e}")
            return {}

    def create_report_schedule(self, company_id: int, report_type: str,
                             frequency: str, recipients: List[str],
                             day_of_week: int = 1, day_of_month: int = 1,
                             hour: int = 9, minute: int = 0) -> str:
        """Rapor zamanlaması oluştur"""
        try:
            schedule_id = f"schedule_{company_id}_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Şablonları yükle
            subject_template, body_template = self._get_email_templates(report_type)

            # Sonraki gönderim zamanını hesapla
            next_send = self._calculate_next_send(frequency, day_of_week, day_of_month, hour, minute)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO report_schedules
                (id, company_id, report_type, frequency, day_of_week, day_of_month,
                 hour, minute, recipients, subject_template, body_template,
                 is_active, next_send)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule_id, company_id, report_type, frequency, day_of_week,
                day_of_month, hour, minute, json.dumps(recipients),
                subject_template, body_template, 1, next_send.isoformat()
            ))

            conn.commit()
            conn.close()

            logging.info(f"[OK] Rapor zamanlaması oluşturuldu: {schedule_id}")
            return schedule_id

        except Exception as e:
            logging.error(f"[HATA] Rapor zamanlaması oluşturulamadı: {e}")
            return ""

    def _get_email_templates(self, report_type: str) -> Tuple[str, str]:
        """E-posta şablonlarını getir"""
        templates = {
            'sdg': {
                'subject': 'SDG İlerleme Raporu - {date}',
                'body': '''
Merhaba,

{company_name} için SDG ilerleme raporunuz hazırlandı.

 Rapor Özeti:
• Toplam {total_indicators} gösterge
• Ortalama ilerleme: %{avg_progress}
• Tamamlanan: {completed_count} gösterge
• Devam eden: {in_progress_count} gösterge

 Rapor ektedir.

Saygılarımızla,
SUSTAINAGE SDG Ekibi
                '''
            },
            'gri': {
                'subject': 'GRI Raporu - {date}',
                'body': '''
Merhaba,

{company_name} için GRI raporunuz hazırlandı.

 Rapor Özeti:
• GRI Standartları uyumluluğu: %{compliance_rate}
• Raporlanan konular: {reported_topics}
• Kanıt belgeleri: {evidence_count} adet

 Rapor ektedir.

Saygılarımızla,
SUSTAINAGE SDG Ekibi
                '''
            },
            'carbon': {
                'subject': 'Karbon Ayak İzi Raporu - {date}',
                'body': '''
Merhaba,

{company_name} için karbon ayak izi raporunuz hazırlandı.

 Rapor Özeti:
• Toplam emisyon: {total_emissions} tCO2e
• Scope 1: {scope1_emissions} tCO2e
• Scope 2: {scope2_emissions} tCO2e
• Scope 3: {scope3_emissions} tCO2e

 Rapor ektedir.

Saygılarımızla,
SUSTAINAGE SDG Ekibi
                '''
            }
        }

        template = templates.get(report_type, templates['sdg'])
        return template['subject'], template['body']

    def _calculate_next_send(self, frequency: str, day_of_week: int,
                           day_of_month: int, hour: int, minute: int) -> datetime:
        """Sonraki gönderim zamanını hesapla"""
        now = datetime.now()

        if frequency == 'daily':
            next_send = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send += timedelta(days=1)

        elif frequency == 'weekly':
            days_ahead = day_of_week - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_send = now + timedelta(days=days_ahead)
            next_send = next_send.replace(hour=hour, minute=minute, second=0, microsecond=0)

        elif frequency == 'monthly':
            next_send = now.replace(day=day_of_month, hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                if now.month == 12:
                    next_send = next_send.replace(year=now.year + 1, month=1)
                else:
                    next_send = next_send.replace(month=now.month + 1)

        elif frequency == 'quarterly':
            quarter = (now.month - 1) // 3 + 1
            if quarter == 4:
                next_send = now.replace(year=now.year + 1, month=1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                next_send = now.replace(month=quarter * 3, day=1, hour=hour, minute=minute, second=0, microsecond=0)

        elif frequency == 'yearly':
            next_send = now.replace(month=1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
            if next_send <= now:
                next_send = next_send.replace(year=now.year + 1)

        else:
            next_send = now + timedelta(days=1)

        return next_send

    def add_stakeholder(self, company_id: int, name: str, email: str,
                       role: str, report_preferences: List[str],
                       language: str = 'tr', timezone: str = 'Europe/Istanbul') -> str:
        """Paydaş ekle"""
        try:
            stakeholder_id = f"stakeholder_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO stakeholders
                (id, company_id, name, email, role, report_preferences, language, timezone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stakeholder_id, company_id, name, email, role,
                json.dumps(report_preferences), language, timezone
            ))

            conn.commit()
            conn.close()

            logging.info(f"[OK] Paydaş eklendi: {name}")
            return stakeholder_id

        except Exception as e:
            logging.error(f"[HATA] Paydaş eklenemedi: {e}")
            return ""

    def generate_and_send_report(self, schedule_id: str) -> bool:
        """Rapor oluştur ve gönder"""
        try:
            # Zamanlamayı al
            schedule_data = self._get_schedule_data(schedule_id)
            if not schedule_data:
                return False

            # Rapor oluştur
            report_file = self._generate_report_file(
                schedule_data['company_id'],
                schedule_data['report_type']
            )

            if not report_file:
                return False

            # E-posta gönder
            success = self._send_email(
                schedule_data['recipients'],
                schedule_data['subject_template'],
                schedule_data['body_template'],
                report_file,
                schedule_data['company_id']
            )

            # Geçmişe kaydet
            self._save_report_history(schedule_id, schedule_data, success)

            # Sonraki gönderim zamanını güncelle
            if success:
                self._update_next_send_time(schedule_id)

            return success

        except Exception as e:
            logging.error(f"[HATA] Rapor gönderilemedi: {e}")
            return False

    def _get_schedule_data(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Zamanlama verilerini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM report_schedules WHERE id = ?
            """, (schedule_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    'id': row[0],
                    'company_id': row[1],
                    'report_type': row[2],
                    'frequency': row[3],
                    'recipients': json.loads(row[8]),
                    'subject_template': row[9],
                    'body_template': row[10],
                    'is_active': bool(row[11])
                }
            return None

        except Exception as e:
            logging.error(f"[HATA] Zamanlama verisi alınamadı: {e}")
            return None

    def _generate_report_file(self, company_id: int, report_type: str) -> Optional[str]:
        """Rapor dosyası oluştur"""
        try:
            # Rapor oluşturma mantığı (gerçek uygulamada AI modülü kullanılacak)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report_type}_report_{company_id}_{timestamp}.pdf"
            filepath = f"raporlar/{report_type}/{filename}"

            # Klasörü oluştur
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Test raporu oluştur (gerçek uygulamada AI ile oluşturulacak)
            with open(filepath, 'w') as f:
                f.write(f"Test {report_type} raporu - {datetime.now()}")

            logging.info(f"[OK] Rapor oluşturuldu: {filepath}")
            return filepath

        except Exception as e:
            logging.error(f"[HATA] Rapor oluşturulamadı: {e}")
            return None

    def _send_email(self, recipients: List[str], subject_template: str,
                   body_template: str, report_file: str, company_id: int) -> bool:
        """E-posta gönder"""
        try:
            # Şirket bilgilerini al
            company_info = self._get_company_info(company_id)

            # Şablonları doldur
            subject = subject_template.format(
                date=datetime.now().strftime('%d.%m.%Y'),
                company_name=company_info.get('name', 'Şirket')
            )

            body = body_template.format(
                company_name=company_info.get('name', 'Şirket'),
                date=datetime.now().strftime('%d.%m.%Y'),
                total_indicators=50,  # Test verisi
                avg_progress=75.5,   # Test verisi
                completed_count=30,  # Test verisi
                in_progress_count=20 # Test verisi
            )

            # Email gönder
            success = True
            for recipient in recipients:
                if not self.email_service.send_email(
                    to_email=recipient,
                    subject=subject,
                    body=body,
                    attachments=[report_file] if report_file and os.path.exists(report_file) else None
                ):
                    success = False
                    logging.error(f"Failed to send email to {recipient}")
            
            if success:
                logging.info(f"[OK] E-posta gönderildi: {len(recipients)} alıcı")
            
            return success

        except Exception as e:
            logging.error(f"[HATA] E-posta gönderilemedi: {e}")
            return False

    def _get_company_info(self, company_id: int) -> Dict[str, Any]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COALESCE(ticari_unvan, sirket_adi), email, telefon FROM company_info WHERE company_id = ?",
                (company_id,),
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    'name': row[0] or '',
                    'email': row[1] or '',
                    'phone': row[2] or ''
                }
            return {}
        except Exception as e:
            logging.error(f"[HATA] Şirket bilgileri alınamadı: {e}")
            return {}

    def _save_report_history(self, schedule_id: str, schedule_data: Dict[str, Any], success: bool):
        """Rapor geçmişini kaydet"""
        try:
            history_id = f"history_{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO report_history
                (id, schedule_id, company_id, report_type, sent_at, recipients, subject, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                history_id, schedule_id, schedule_data['company_id'],
                schedule_data['report_type'], datetime.now().isoformat(),
                json.dumps(schedule_data['recipients']),
                schedule_data['subject_template'],
                'sent' if success else 'failed'
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Rapor geçmişi kaydedilemedi: {e}")

    def _update_next_send_time(self, schedule_id: str):
        """Sonraki gönderim zamanını güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Mevcut zamanlamayı al
            cursor.execute("""
                SELECT frequency, day_of_week, day_of_month, hour, minute
                FROM report_schedules WHERE id = ?
            """, (schedule_id,))

            row = cursor.fetchone()
            if row:
                frequency, day_of_week, day_of_month, hour, minute = row
                next_send = self._calculate_next_send(frequency, day_of_week, day_of_month, hour, minute)

                # Güncelle
                cursor.execute("""
                    UPDATE report_schedules 
                    SET last_sent = ?, next_send = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), next_send.isoformat(), schedule_id))

                conn.commit()

            conn.close()

        except Exception as e:
            logging.error(f"[HATA] Sonraki gönderim zamanı güncellenemedi: {e}")

    def get_pending_reports(self) -> List[Dict[str, Any]]:
        """Bekleyen raporları getir"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, company_id, report_type, recipients, next_send
                FROM report_schedules
                WHERE is_active = 1 AND next_send <= ?
                ORDER BY next_send ASC
            """, (datetime.now().isoformat(),))

            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'company_id': row[1],
                    'report_type': row[2],
                    'recipients': json.loads(row[3]),
                    'next_send': row[4]
                })

            conn.close()
            return reports

        except Exception as e:
            logging.error(f"[HATA] Bekleyen raporlar alınamadı: {e}")
            return []

    def start_scheduler(self):
        """Zamanlayıcıyı başlat"""
        try:
            # Bekleyen raporları kontrol et
            pending_reports = self.get_pending_reports()

            for report in pending_reports:
                logging.info(f"[SCHEDULER] Rapor gönderiliyor: {report['id']}")
                self.generate_and_send_report(report['id'])

            logging.info(f"[OK] Zamanlayıcı çalıştırıldı: {len(pending_reports)} rapor işlendi")

        except Exception as e:
            logging.error(f"[HATA] Zamanlayıcı çalıştırılamadı: {e}")


if __name__ == "__main__":
    # Test
    logging.info("[TEST] Otomatik Rapor Gönderimi...")

    system = AutomatedReportingSystem()

    # Test zamanlaması oluştur
    schedule_id = system.create_report_schedule(
        company_id=1,
        report_type='sdg',
        frequency='weekly',
        recipients=['test@example.com'],
        day_of_week=1,  # Pazartesi
        hour=9,
        minute=0
    )

    logging.info(f"Zamanlama oluşturuldu: {schedule_id}")

    # Test paydaş ekle
    stakeholder_id = system.add_stakeholder(
        company_id=1,
        name="Test Paydaş",
        email="stakeholder@example.com",
        role="investor",
        report_preferences=['sdg', 'gri']
    )

    logging.info(f"Paydaş eklendi: {stakeholder_id}")

    # Bekleyen raporları kontrol et
    pending = system.get_pending_reports()
    logging.info(f"Bekleyen raporlar: {len(pending)} adet")

    logging.info("[OK] Test tamamlandı")
