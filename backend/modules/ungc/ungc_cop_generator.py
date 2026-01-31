import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UN Global Compact - COP (Communication on Progress) Report Generator
PDF raporu oluşturur
"""
import os
from datetime import datetime
from typing import Dict, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
from config.database import DB_PATH


class UNGCCOPGenerator:
    """COP Report Generator"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.manager = UNGCManagerEnhanced(db_path)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles - TÜRKÇE KARAKTER DESTEKLİ"""
        # Türkçe karakterler için uygun fontlar - SİSTEM FONTU KULLAN
        turkish_font = 'Helvetica'  # Sistem fontu, her zaman mevcut

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=turkish_font  # Bold kaldırıldı
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=20,
            fontName=turkish_font  # Bold kaldırıldı
        ))

        # Principle heading
        self.styles.add(ParagraphStyle(
            name='PrincipleHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=10,
            spaceBefore=15,
            fontName=turkish_font  # Bold kaldırıldı
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            fontName=turkish_font
        ))

    def _get_company_info(self, company_id: int) -> Dict:
        """Get company information"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            result = cursor.execute(
                "SELECT name, sector, country FROM companies WHERE id = ?",
                (company_id,)
            ).fetchone()

            if result:
                # Türkçe karakterleri koruyarak PDF generation
                name = result[0] or 'Şirket Adı'
                return {
                    'name': name or 'Şirket',
                    'sector': result[1] or 'N/A',
                    'country': result[2] or 'N/A'
                }
            return {'name': 'Company', 'sector': 'N/A', 'country': 'N/A'}
        finally:
            conn.close()

    def _create_cover_page(self, company_name: str, period: str, level_info: Dict) -> list:
        """Create COP cover page"""
        elements = []

        # Logo area (if exists)
        logo_path = 'resimler/ungc_logo.png'
        if os.path.exists(logo_path):
            try:
                logo = RLImage(logo_path, width=8*cm, height=4*cm)
                elements.append(logo)
                elements.append(Spacer(1, 1*cm))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # Title
        elements.append(Spacer(1, 2*cm))
        title = Paragraph(
            "Communication on Progress (COP)",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 1*cm))

        # Company info
        company_info = Paragraph(
            f"<b>{company_name}</b><br/>"
            f"Period: {period}<br/>"
            f"Report Date: {datetime.now().strftime('%d %B %Y')}",
            self.styles['BodyText']
        )
        elements.append(company_info)
        elements.append(Spacer(1, 1*cm))

        # Level badge
        level_badge = Paragraph(
            f"<b>UNGC Level:</b> {level_info['level']} {level_info['badge']}<br/>"
            f"<i>{level_info['description']}</i>",
            self.styles['BodyText']
        )
        elements.append(level_badge)

        elements.append(PageBreak())
        return elements

    def _create_ceo_statement(self, ceo_statement: str) -> list:
        """Create CEO statement section"""
        elements = []

        # Section title
        title = Paragraph("Statement of Continued Support", self.styles['SectionHeading'])
        elements.append(title)

        # CEO statement text
        if ceo_statement:
            statement_para = Paragraph(ceo_statement, self.styles['BodyJustify'])
            elements.append(statement_para)
        else:
            default_text = (
                "To our stakeholders:<br/><br/>"
                "I am pleased to confirm that [Company Name] reaffirms its support of the Ten Principles "
                "of the United Nations Global Compact in the areas of Human Rights, Labour, Environment "
                "and Anti-Corruption.<br/><br/>"
                "In this annual Communication on Progress, we describe our actions to continually improve "
                "the integration of the Global Compact and its principles into our business strategy, "
                "culture and daily operations. We also commit to share this information with our stakeholders "
                "using our primary channels of communication.<br/><br/>"
                "Sincerely yours,<br/>"
                "[CEO Name]<br/>"
                "[CEO Title]"
            )
            statement_para = Paragraph(default_text, self.styles['BodyJustify'])
            elements.append(statement_para)

        elements.append(Spacer(1, 0.5*cm))
        return elements

    def _create_principle_section(self, principle_data: Dict) -> list:
        """Create section for one principle"""
        elements = []

        # Principle heading
        principle_id = principle_data['id']
        principle_title = principle_data['title']
        score = principle_data['score']

        heading = Paragraph(
            f"Principle {principle_id}: {principle_title}",
            self.styles['PrincipleHeading']
        )
        elements.append(heading)

        # Score indicator
        score_text = Paragraph(
            f"<b>Compliance Score: {score}%</b>",
            self.styles['BodyText']
        )
        elements.append(score_text)
        elements.append(Spacer(1, 0.3*cm))

        # KPI table
        kpis = principle_data.get('kpis', [])
        if kpis:
            # Table data
            table_data = [['KPI', 'Current Value', 'Target', 'Score']]

            for kpi in kpis:
                kpi_name = kpi.get('name', 'N/A')
                current = kpi.get('current_value')
                target = kpi.get('target')
                kpi_score = kpi.get('score', 0)

                # Format values
                if current is not None:
                    if kpi.get('type') == 'boolean':
                        current_str = 'Yes' if current > 0 else 'No'
                    elif kpi.get('type') == 'percentage':
                        current_str = f"{current:.1f}%"
                    else:
                        current_str = f"{current:.1f}"
                else:
                    current_str = 'N/A'

                target_str = f"{target}" if target is not None else 'N/A'
                score_str = f"{kpi_score:.1f}%"

                table_data.append([kpi_name, current_str, target_str, score_str])

            # Create table
            table = Table(table_data, colWidths=[8*cm, 3*cm, 2.5*cm, 2.5*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            elements.append(table)

        elements.append(Spacer(1, 0.5*cm))
        gaps = principle_data.get('gaps', {})
        gap_rows = []
        for ev in gaps.get('missing_evidence', []):
            gap_rows.append(['Missing Evidence', ev, ''])
        for md in gaps.get('missing_kpi_data', []):
            gap_rows.append(['Missing KPI Data', md.get('name', 'N/A'), ''])
        for bt in gaps.get('below_target_kpis', []):
            gap_rows.append(['Below Target KPI', bt.get('name', 'N/A'), f"{bt.get('score', 0):.1f}%"])
        if gap_rows:
            gap_title = Paragraph('Gap Checklist', self.styles['BodyText'])
            elements.append(gap_title)
            gtable = Table([['Type', 'Item', 'Detail']] + gap_rows, colWidths=[5*cm, 7*cm, 3*cm])
            gtable.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fee2e2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            elements.append(gtable)
            elements.append(Spacer(1, 0.5*cm))
        return elements

    def _create_category_section(self, section_data: Dict) -> list:
        """Create section for a category (Human Rights, Labour, etc.)"""
        elements = []

        # Section title
        section_title = section_data['title']
        title = Paragraph(section_title, self.styles['SectionHeading'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Add principles in this section
        for principle_data in section_data.get('principles', []):
            principle_elements = self._create_principle_section(principle_data)
            elements.extend(principle_elements)

        return elements

    def _create_summary_table(self, overall_data: Dict) -> list:
        """Create summary table"""
        elements = []

        # Title
        title = Paragraph("Executive Summary", self.styles['SectionHeading'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*cm))

        # Overall score
        overall_score = overall_data['overall_score']
        level = overall_data['level']

        summary_text = Paragraph(
            f"<b>Overall UNGC Compliance Score: {overall_score}%</b><br/>"
            f"<b>Classification Level: {level}</b>",
            self.styles['BodyText']
        )
        elements.append(summary_text)
        elements.append(Spacer(1, 0.5*cm))

        # Category scores table
        category_scores = overall_data.get('category_scores', {})
        table_data = [['Category', 'Score']]

        for category, score in category_scores.items():
            table_data.append([category, f"{score:.1f}%"])

        table = Table(table_data, colWidths=[10*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 1*cm))

        return elements

    def generate_report(self, company_id: int, period: Optional[str] = None,
                       output_path: Optional[str] = None, ceo_statement: str = "") -> str:
        """
        Generate COP PDF report
        
        Args:
            company_id: Company ID
            period: Reporting period (year)
            output_path: Output PDF path
            ceo_statement: CEO statement text
            
        Returns:
            Path to generated PDF
        """
        if period is None:
            period = str(datetime.now().year)

        # Get company info
        company_info = self._get_company_info(company_id)
        company_name = company_info['name']

        # Generate COP data
        cop_data = self.manager.generate_cop_data(company_id, period, ceo_statement)
        overall_data = self.manager.calculate_overall_score(company_id, period)

        # Output path
        if output_path is None:
            os.makedirs('reports/ungc', exist_ok=True)
            output_path = f"reports/ungc/COP_{company_name.replace(' ', '_')}_{period}.pdf"

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Cover page
        cover_elements = self._create_cover_page(
            company_name,
            period,
            overall_data['level_info']
        )
        elements.extend(cover_elements)

        # CEO Statement
        ceo_elements = self._create_ceo_statement(ceo_statement)
        elements.extend(ceo_elements)
        elements.append(PageBreak())

        # Executive Summary
        summary_elements = self._create_summary_table(overall_data)
        elements.extend(summary_elements)
        elements.append(PageBreak())

        # Sections (Human Rights, Labour, Environment, Anti-Corruption)
        for section in cop_data.get('sections', []):
            section_elements = self._create_category_section(section)
            elements.extend(section_elements)
            elements.append(PageBreak())

        # Build PDF
        doc.build(elements)

        return output_path


if __name__ == '__main__':
    # Test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    company_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    period = sys.argv[3] if len(sys.argv) > 3 else str(datetime.now().year)

    generator = UNGCCOPGenerator(db)

    # Sample CEO statement
    ceo_statement = """
    To our stakeholders,
    
    I am pleased to confirm that our company reaffirms its support of the Ten Principles 
    of the United Nations Global Compact in the areas of Human Rights, Labour, Environment 
    and Anti-Corruption.
    
    In this annual Communication on Progress, we describe our actions to continually improve 
    the integration of the Global Compact and its principles into our business strategy, 
    culture and daily operations.
    
    We are committed to making the Global Compact and its principles part of the strategy, 
    culture and day-to-day operations of our company, and to engaging in collaborative 
    projects which advance the broader development goals of the United Nations, particularly 
    the Sustainable Development Goals.
    
    Sincerely,
    [CEO Name]
    Chief Executive Officer
    """

    output = generator.generate_report(company_id, period, ceo_statement=ceo_statement)
    logging.info(f"\nReport saved to: {output}")

