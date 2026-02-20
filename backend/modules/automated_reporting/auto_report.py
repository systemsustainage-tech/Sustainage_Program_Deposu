#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Otomatik Raporlama"""

from typing import List, Dict, Optional, Any
from backend.core.base_manager import BaseTenantManager

class AutoReportManager(BaseTenantManager):
    """Otomatik rapor yoneticisi"""

    def __init__(self, db_path: str, company_id: Optional[int] = None):
        super().__init__(db_path, company_id)

    def schedule_report(self, company_id: int, report_type: str, frequency: str, email_to: str) -> Dict[str, Any]:
        """Rapor zamanla"""
        try:
            # Tablo yoksa oluştur (Geçici olarak burada, normalde migration ile olmalı)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS scheduled_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    email_to TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """, (), company_id=company_id)

            self.insert('scheduled_reports', {
                'company_id': company_id,
                'report_type': report_type,
                'frequency': frequency,
                'email_to': email_to
            }, company_id=company_id)
            
            return {"status": "scheduled", "message": "Rapor başarıyla zamanlandı"}
        except Exception as e:
            self.logger.error(f"Schedule report error: {e}")
            return {"status": "error", "message": str(e)}

    def generate_report_content(self, company_id: int, report_type: str, year: Optional[int] = None) -> Dict[str, Any]:
        """Rapor içerigi oluştur"""
        content = {"company_id": company_id, "report_type": report_type, "year": year}
        
        try:
            # Karbon verilerini ekle
            if report_type in ['carbon_alert', 'monthly_summary', 'environmental']:
                try:
                    from backend.modules.environmental.carbon_calculator import CarbonCalculator
                    carbon_calc = CarbonCalculator(self.db_path)
                    carbon_summary = carbon_calc.get_company_summary(company_id, year)
                    content['carbon_data'] = carbon_summary
                except ImportError:
                    self.logger.warning("CarbonCalculator module not found")
                except Exception as e:
                    self.logger.error(f"Error fetching carbon data: {e}")
                    content['carbon_error'] = str(e)
            
            return content
        except Exception as e:
            self.logger.error(f"Generate report content error: {e}")
            return {"error": str(e)}

    def send_report_email(self, report_path: str, email_to: str) -> Dict[str, Any]:
        """Rapor email gonder (placeholder)"""
        # Burada e-posta gönderme işlemi yapılacak
        return {"status": "sent", "message": f"Rapor {email_to} adresine gönderildi (simulasyon)"}

    def get_scheduled_reports(self, company_id: int) -> List[Dict[str, Any]]:
        """Zamanlanmis raporlari getir"""
        try:
            return self.select('scheduled_reports', company_id=company_id)
        except Exception:
            return []

