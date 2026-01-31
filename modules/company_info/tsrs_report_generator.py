#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS Rapor Generator
Şirket bilgilerini kullanarak TSRS raporları oluştur
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from config.database import DB_PATH


class TSRSReportGenerator:
    """TSRS rapor generator"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_company_info(self, company_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA table_info(company_info)")
            cols = [col[1] for col in cursor.fetchall()]
            cursor.execute("SELECT * FROM company_info WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if not row:
                return {}
            return dict(zip(cols, row))
        except Exception as e:
            logging.error(f"Şirket bilgisi alma hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_tsrs_header(self, company_id: int, output_path: str) -> bool:
        """TSRS rapor başlığı oluştur"""
        try:
            company_info = self.get_company_info(company_id)
            if not company_info:
                logging.info("Şirket bilgileri bulunamadı!")
                return False

            # PDF oluştur
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []

            # Stiller
            styles = getSampleStyleSheet()

            # Türkçe PDF yardımcı importu (opsiyonel)
            try:
                from modules.reporting.turkish_pdf_utils import turkish_pdf
            except Exception:
                turkish_pdf = None
            tf = turkish_pdf.get_turkish_font() if turkish_pdf else 'Helvetica'
            bold_tf = f"{tf}-Bold"

            # Başlık stili
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=1,  # Center
                fontName=bold_tf
            )

            # Alt başlık stili
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=15,
                spaceBefore=20,
                fontName=bold_tf
            )

            # Normal metin stili
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.black,
                spaceAfter=6,
                fontName=tf
            )

            # Ana başlık
            story.append(Paragraph("SUSTAINABILITY REPORTING STANDARD (TSRS)", title_style))
            story.append(Paragraph("COMPANY INFORMATION", title_style))
            story.append(Spacer(1, 20))

            # Şirket Bilgileri
            story.append(Paragraph("COMPANY INFORMATION", subtitle_style))

            company_data = [
                ["Company Name:", company_info.get('legal_name', 'N/A')],
                ["Trading Name:", company_info.get('trading_name', company_info.get('name', 'N/A'))],
                ["Registration Number:", company_info.get('registration_number', 'N/A')],
                ["Tax Number:", company_info.get('tax_number', 'N/A')],
                ["Legal Form:", company_info.get('legal_form', 'N/A')],
                ["Establishment Date:", company_info.get('establishment_date', 'N/A')],
                ["Ownership Type:", company_info.get('ownership_type', 'N/A')],
                ["Parent Company:", company_info.get('parent_company', 'N/A')],
                ["Subsidiaries:", company_info.get('subsidiaries', 'N/A')]
            ]

            company_table = Table(company_data, colWidths=[2*inch, 4*inch])
            company_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), bold_tf),
                ('FONTNAME', (1, 0), (1, -1), tf),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            story.append(company_table)
            story.append(Spacer(1, 20))

            # Adres Bilgileri
            story.append(Paragraph("HEADQUARTERS ADDRESS", subtitle_style))

            address_text = f"""
            {company_info.get('headquarters_address', 'N/A')}<br/>
            {company_info.get('city', 'N/A')} {company_info.get('postal_code', 'N/A')}<br/>
            {company_info.get('country', 'N/A')}
            """
            story.append(Paragraph(address_text, normal_style))
            story.append(Spacer(1, 20))

            # İletişim Bilgileri
            story.append(Paragraph("CONTACT INFORMATION", subtitle_style))

            contact_data = [
                ["Phone:", company_info.get('phone', 'N/A')],
                ["Email:", company_info.get('email', 'N/A')],
                ["Website:", company_info.get('website', 'N/A')],
                ["Sustainability Contact:", company_info.get('sustainability_contact', 'N/A')]
            ]

            contact_table = Table(contact_data, colWidths=[2*inch, 4*inch])
            contact_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), bold_tf),
                ('FONTNAME', (1, 0), (1, -1), tf),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            story.append(contact_table)
            story.append(Spacer(1, 20))

            # İş Bilgileri
            story.append(Paragraph("BUSINESS INFORMATION", subtitle_style))

            business_data = [
                ["Sector:", company_info.get('sector', 'N/A')],
                ["Industry Code (NACE):", company_info.get('industry_code', 'N/A')],
                ["Industry Description:", company_info.get('industry_description', 'N/A')],
                ["Company Size:", company_info.get('company_size', 'N/A')],
                ["Employee Count:", str(company_info.get('employee_count', 'N/A'))],
                ["Annual Revenue:", f"{company_info.get('annual_revenue', 'N/A')} {company_info.get('currency', 'TRY')}"],
                ["ISIC Code:", company_info.get('isic_code', 'N/A')]
            ]

            business_table = Table(business_data, colWidths=[2*inch, 4*inch])
            business_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), bold_tf),
                ('FONTNAME', (1, 0), (1, -1), tf),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            story.append(business_table)
            story.append(Spacer(1, 20))

            # Borsa Bilgileri
            story.append(Paragraph("STOCK EXCHANGE INFORMATION", subtitle_style))

            stock_data = [
                ["Stock Exchange:", company_info.get('stock_exchange', 'N/A')],
                ["Ticker Symbol:", company_info.get('ticker_symbol', 'N/A')],
                ["Fiscal Year End:", company_info.get('fiscal_year_end', 'N/A')],
                ["Reporting Period:", company_info.get('reporting_period', 'N/A')],
                ["Auditor:", company_info.get('auditor', 'N/A')]
            ]

            stock_table = Table(stock_data, colWidths=[2*inch, 4*inch])
            stock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), bold_tf),
                ('FONTNAME', (1, 0), (1, -1), tf),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            story.append(stock_table)
            story.append(Spacer(1, 20))

            # Sürdürülebilirlik Bilgileri
            story.append(Paragraph("SUSTAINABILITY INFORMATION", subtitle_style))

            sustainability_data = [
                ["Sustainability Strategy:", company_info.get('sustainability_strategy', 'N/A')],
                ["Material Topics:", company_info.get('material_topics', 'N/A')],
                ["Stakeholder Groups:", company_info.get('stakeholder_groups', 'N/A')],
                ["ESG Rating Agency:", company_info.get('esg_rating_agency', 'N/A')],
                ["ESG Rating:", company_info.get('esg_rating', 'N/A')],
                ["Certifications:", company_info.get('certifications', 'N/A')],
                ["Memberships:", company_info.get('memberships', 'N/A')]
            ]

            sustainability_table = Table(sustainability_data, colWidths=[2*inch, 4*inch])
            sustainability_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), bold_tf),
                ('FONTNAME', (1, 0), (1, -1), tf),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            story.append(sustainability_table)
            story.append(Spacer(1, 20))

            # Açıklama
            if company_info.get('description'):
                story.append(Paragraph("COMPANY DESCRIPTION", subtitle_style))
                story.append(Paragraph(company_info['description'], normal_style))
                story.append(Spacer(1, 20))

            # Ana ürün/hizmetler
            if company_info.get('key_products_services'):
                story.append(Paragraph("KEY PRODUCTS AND SERVICES", subtitle_style))
                story.append(Paragraph(company_info['key_products_services'], normal_style))
                story.append(Spacer(1, 20))

            # Pazar bilgileri
            if company_info.get('markets_served'):
                story.append(Paragraph("MARKETS SERVED", subtitle_style))
                story.append(Paragraph(company_info['markets_served'], normal_style))
                story.append(Spacer(1, 20))

            # Rapor tarihi
            story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            story.append(Paragraph(f"Last Updated: {company_info.get('updated_at', 'N/A')}", normal_style))

            # PDF oluştur
            doc.build(story)
            return True

        except Exception as e:
            logging.error(f"TSRS rapor oluşturma hatası: {e}")
            return False

    def generate_company_summary_html(self, company_id: int) -> str:
        """Şirket özeti HTML formatında oluştur"""
        company_info = self.get_company_info(company_id)
        if not company_info:
            return "<p>Şirket bilgileri bulunamadı!</p>"

        html = f"""
        <div class="company-info-header">
            <h1>SUSTAINABILITY REPORTING STANDARD (TSRS) - COMPANY INFORMATION</h1>
            
            <div class="company-section">
                <h2>COMPANY INFORMATION</h2>
                <table class="info-table">
                    <tr><td><strong>Company Name:</strong></td><td>{company_info.get('legal_name', 'N/A')}</td></tr>
                    <tr><td><strong>Trading Name:</strong></td><td>{company_info.get('trading_name', company_info.get('name', 'N/A'))}</td></tr>
                    <tr><td><strong>Registration Number:</strong></td><td>{company_info.get('registration_number', 'N/A')}</td></tr>
                    <tr><td><strong>Tax Number:</strong></td><td>{company_info.get('tax_number', 'N/A')}</td></tr>
                    <tr><td><strong>Legal Form:</strong></td><td>{company_info.get('legal_form', 'N/A')}</td></tr>
                    <tr><td><strong>Establishment Date:</strong></td><td>{company_info.get('establishment_date', 'N/A')}</td></tr>
                    <tr><td><strong>Ownership Type:</strong></td><td>{company_info.get('ownership_type', 'N/A')}</td></tr>
                </table>
            </div>
            
            <div class="company-section">
                <h2>HEADQUARTERS ADDRESS</h2>
                <p>{company_info.get('headquarters_address', 'N/A')}<br/>
                {company_info.get('city', 'N/A')} {company_info.get('postal_code', 'N/A')}<br/>
                {company_info.get('country', 'N/A')}</p>
            </div>
            
            <div class="company-section">
                <h2>CONTACT INFORMATION</h2>
                <table class="info-table">
                    <tr><td><strong>Phone:</strong></td><td>{company_info.get('phone', 'N/A')}</td></tr>
                    <tr><td><strong>Email:</strong></td><td>{company_info.get('email', 'N/A')}</td></tr>
                    <tr><td><strong>Website:</strong></td><td>{company_info.get('website', 'N/A')}</td></tr>
                    <tr><td><strong>Sustainability Contact:</strong></td><td>{company_info.get('sustainability_contact', 'N/A')}</td></tr>
                </table>
            </div>
            
            <div class="company-section">
                <h2>BUSINESS INFORMATION</h2>
                <table class="info-table">
                    <tr><td><strong>Sector:</strong></td><td>{company_info.get('sector', 'N/A')}</td></tr>
                    <tr><td><strong>Industry Code (NACE):</strong></td><td>{company_info.get('industry_code', 'N/A')}</td></tr>
                    <tr><td><strong>Company Size:</strong></td><td>{company_info.get('company_size', 'N/A')}</td></tr>
                    <tr><td><strong>Employee Count:</strong></td><td>{company_info.get('employee_count', 'N/A')}</td></tr>
                    <tr><td><strong>Annual Revenue:</strong></td><td>{company_info.get('annual_revenue', 'N/A')} {company_info.get('currency', 'TRY')}</td></tr>
                </table>
            </div>
            
            <div class="company-section">
                <h2>SUSTAINABILITY INFORMATION</h2>
                <table class="info-table">
                    <tr><td><strong>Sustainability Strategy:</strong></td><td>{company_info.get('sustainability_strategy', 'N/A')}</td></tr>
                    <tr><td><strong>Material Topics:</strong></td><td>{company_info.get('material_topics', 'N/A')}</td></tr>
                    <tr><td><strong>ESG Rating Agency:</strong></td><td>{company_info.get('esg_rating_agency', 'N/A')}</td></tr>
                    <tr><td><strong>ESG Rating:</strong></td><td>{company_info.get('esg_rating', 'N/A')}</td></tr>
                </table>
            </div>
        </div>
        
        <style>
        .company-info-header {{
            font-family: Segoe UI, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .company-info-header h1 {{
            color: #1e40af;
            text-align: center;
            margin-bottom: 30px;
        }}
        .company-section {{
            margin-bottom: 30px;
        }}
        .company-section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #1e40af;
            padding-bottom: 5px;
        }}
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        .info-table td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        .info-table td:first-child {{
            background-color: #f8f9fa;
            font-weight: bold;
            width: 30%;
        }}
        </style>
        """

        return html
