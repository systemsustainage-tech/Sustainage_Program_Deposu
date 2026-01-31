#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Dağıtım (Gerçek SMTP)
- Rapor dosyalarını e-posta ile göndermek için arayüz
- SMTP ortam değişkenleri varsa GERÇEK gönderim yapar; yoksa simülasyon
- SDG_REQUIRE_REAL=1 ise ve SMTP yoksa hata verir (simülasyon devre dışı)
"""

import logging
from typing import List

from services.email_service import EmailService


class Emailer:
    def __init__(self):
        self.service = EmailService()

    def send_report(self, recipients: List[str], subject: str, body: str, attachments: List[str]) -> bool:
        to_list = [r.strip() for r in recipients if r and r.strip()]
        if not to_list:
            return False
        success_list = []
        for to_email in to_list:
            ok = self.service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                attachments=attachments
            )
            success_list.append(ok)
        logging.info(f"[EMAIL] Sent to {sum(1 for x in success_list if x)} of {len(to_list)} recipients via centralized EmailService")
        return all(success_list)
