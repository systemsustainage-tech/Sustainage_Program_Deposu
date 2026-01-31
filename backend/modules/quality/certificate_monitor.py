#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sertifika Takip Sistemi
Süresi dolacak sertifikalar için uyarı
"""

import logging
import os
import sqlite3
from typing import Dict, List


class CertificateMonitor:
    """Sertifika süresi takip ve uyarı"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

    def check_expiring_certificates(self, company_id: int, days_ahead: int = 30) -> List[Dict]:
        """
        Süresi dolacak sertifikalar
        
        Args:
            company_id: Firma ID
            days_ahead: Kaç gün sonrasına kadar (varsayılan: 30)
        
        Returns:
            List[Dict]: Süresi dolacak sertifikalar
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # expiry_date yakın olanlar
            cursor.execute("""
                SELECT id, certificate_name, expiry_date, 
                       julianday(expiry_date) - julianday('now') as days_left
                FROM quality_certifications
                WHERE company_id = ?
                AND expiry_date IS NOT NULL
                AND julianday(expiry_date) - julianday('now') <= ?
                AND julianday(expiry_date) - julianday('now') > 0
                ORDER BY expiry_date
            """, (company_id, days_ahead))

            expiring = []
            for row in cursor.fetchall():
                days_left = int(row[3])
                urgency = 'Kritik' if days_left <= 7 else 'Yüksek' if days_left <= 15 else 'Orta'

                expiring.append({
                    'id': row[0],
                    'name': row[1],
                    'expiry_date': row[2],
                    'days_left': days_left,
                    'urgency': urgency
                })

            return expiring

        finally:
            conn.close()

    def send_expiry_notifications(self, company_id: int) -> int:
        """Sertifika uyarılarını gönder"""
        expiring = self.check_expiring_certificates(company_id, days_ahead=30)

        if not expiring:
            return 0

        # Bildirim gönder
        try:
            from tasks.notification_manager import NotificationManager
            nm = NotificationManager()

            for cert in expiring:
                # Admin'lere bildirim
                nm.create_notification(
                    user_id=1,  # Admin (gerçekte tüm admin'ler)
                    title=f"️ Sertifika Süresi Doluyor: {cert['name']}",
                    message=f"Sertifika {cert['days_left']} gün içinde sona erecek!\n"
                           f"Son tarih: {cert['expiry_date']}\n"
                           f"Lütfen yenileme işlemini başlatın.",
                    type='warning'
                )

            return len(expiring)

        except Exception as e:
            logging.error(f"[HATA] Sertifika bildirimi: {e}")
            return 0

