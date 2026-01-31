#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rapor Email Gönderim Sistemi
Otomatik email ile rapor gönderimi
"""

import logging
import os
from typing import Any, Dict, List, Optional

from services.email_service import EmailService


class ReportEmailSender:
    """Rapor email gönderim yöneticisi"""

    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Args:
            smtp_config: Deprecated. Uses central EmailService config.
        """
        self.email_service = EmailService()

    def send_report(self, recipients: List[str], subject: str,
                   body: str, report_path: str,
                   company_name: str = "Şirketiniz") -> bool:
        """
        Raporu email ile gönder
        
        Args:
            recipients: Alıcı email listesi
            subject: Email konusu
            body: Email metni
            report_path: Rapor dosya yolu
            company_name: Şirket adı
        """
        try:
            if not os.path.exists(report_path):
                logging.info(f"Rapor dosyasi bulunamadi: {report_path}")
                return False

            # Email metni (EmailService zaten HTML wrap yapıyor)
            email_body = f"""
                <h2 style="color: #6A1B9A;">{company_name} - Sürdürülebilirlik Raporu</h2>
                <p>{body}</p>
            """

            # Email gönder
            success = True
            for recipient in recipients:
                if not self.email_service.send_email(
                    to_email=recipient,
                    subject=subject,
                    body=email_body,
                    attachments=[report_path]
                ):
                    success = False
                    logging.error(f"Failed to send email to {recipient}")

            return success

        except Exception as e:
            logging.error(f"Email sending error: {e}")
            return False
