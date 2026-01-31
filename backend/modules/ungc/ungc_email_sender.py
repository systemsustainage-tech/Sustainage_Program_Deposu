#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Email Sender
Send COP reports via email
"""
import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from modules.ungc.ungc_cop_generator import UNGCCOPGenerator
from config.database import DB_PATH


class UNGCEmailSender:
    """Send UNGC reports via email"""

    def __init__(self, db_path: str, smtp_config: Optional[Dict[str, Any]] = None):
        self.db_path = db_path
        self.smtp_config = smtp_config or self._load_smtp_config()

    def _load_smtp_config(self) -> Dict[str, Any]:
        """Load SMTP configuration"""
        try:
            import json
            # Use backend config path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'smtp_config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Map keys to expected format
                    return {
                        'server': data.get('smtp_server', 'smtp.gmail.com'),
                        'port': data.get('smtp_port', 587),
                        'use_tls': data.get('use_tls', True),
                        'username': data.get('sender_email', ''),
                        'password': data.get('sender_password', '')
                    }
        except Exception as e:
            logging.error(f"SMTP config load error: {e}")

        # Default config
        return {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_tls': True,
            'username': '',
            'password': ''
        }

    def send_cop_report(self, company_id: int, period: str, to_emails: List[str],
                       subject: Optional[str] = None, message: Optional[str] = None, ceo_statement: str = "") -> bool:
        """
        Send COP report via email
        
        Args:
            company_id: Company ID
            period: Reporting period
            to_emails: List of recipient emails
            subject: Email subject
            message: Email body
            ceo_statement: CEO statement for report
            
        Returns:
            Success status
        """
        try:
            # Generate COP report
            generator = UNGCCOPGenerator(self.db_path)
            pdf_path = generator.generate_report(company_id, period, ceo_statement=ceo_statement)

            if not os.path.exists(pdf_path):
                logging.info("PDF not generated")
                return False

            # Get company name
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            result = cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,)).fetchone()
            company_name = result[0] if result else "Company"
            conn.close()

            # Email content
            if subject is None:
                subject = f"UNGC Communication on Progress (COP) - {company_name} - {period}"

            if message is None:
                message = f"""
Dear Stakeholder,

Please find attached our Communication on Progress (COP) report for the period {period}.

This report demonstrates our continued commitment to the Ten Principles of the United Nations Global Compact.

Best regards,
{company_name}
"""

            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('username', '')
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject

            # Email body
            msg.attach(MIMEText(message, 'plain'))

            # Attach PDF
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment',
                                        filename=os.path.basename(pdf_path))
                msg.attach(pdf_attachment)

            # Send email
            server = smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port'])
            if self.smtp_config.get('use_tls'):
                server.starttls()

            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()

            logging.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True

        except Exception as e:
            logging.error(f"Email send error: {e}")
            return False


if __name__ == '__main__':
    # Test
    sender = UNGCEmailSender(DB_PATH)

    # Note: Configure SMTP settings in backend/config/smtp_config.json
    # success = sender.send_cop_report(
    #     company_id=1,
    #     period='2024',
    #     to_emails=['stakeholder@example.com']
    # )
    logging.info("Email module ready. Configure SMTP settings to send emails.")

