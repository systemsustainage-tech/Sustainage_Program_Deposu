import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Content Index Export - Sprint 3
GRI Content Index template 2021 ile uyumlu Excel export
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from config.database import DB_PATH


class GRIContentIndex:
    """GRI Content Index sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(project_root, db_path)
        else:
            self.db_path = db_path
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def generate_content_index(self, company_id: int = 1) -> Dict:
        """GRI Content Index oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI Content Index oluşturuluyor...")

            # Tüm göstergeleri al
            cursor.execute("""
                SELECT 
                    gi.id,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gi.description,
                    gi.unit,
                    gi.methodology,
                    gi.reporting_requirement,
                    gi.priority,
                    gi.requirement_level,
                    gi.reporting_frequency,
                    gi.data_quality,
                    gi.audit_required,
                    gi.validation_required,
                    gi.digitalization_status,
                    gi.cost_level,
                    gi.time_requirement,
                    gi.expertise_requirement,
                    gi.sustainability_impact,
                    gi.legal_compliance,
                    gi.sector_specific,
                    gi.international_standard,
                    gi.metric_type,
                    gi.scale_unit,
                    gi.data_source_system,
                    gi.reporting_format,
                    gi.tsrs_esrs_mapping,
                    gi.un_sdg_mapping,
                    gi.gri_3_3_reference,
                    gi.impact_area,
                    gi.stakeholder_group,
                    gs.code as standard_code,
                    gs.title as standard_title,
                    gs.category,
                    gs.type as standard_type,
                    gs.sub_category
                FROM gri_indicators gi
                JOIN gri_standards gs ON gi.standard_id = gs.id
                ORDER BY gs.category, gs.code, gi.code
            """)

            indicators = cursor.fetchall()

            # Kategori bazında organize et
            content_index = {
                'universal': [],
                'economic': [],
                'environmental': [],
                'social': [],
                'sector': []
            }

            for indicator in indicators:
                category = indicator[31]  # gs.category
                if category == 'Universal':
                    content_index['universal'].append(indicator)
                elif category == 'Economic':
                    content_index['economic'].append(indicator)
                elif category == 'Environmental':
                    content_index['environmental'].append(indicator)
                elif category == 'Social':
                    content_index['social'].append(indicator)
                elif category == 'Sector-Specific':
                    content_index['sector'].append(indicator)

            # Company responses ve GRI 2/3 status/page bilgilerini al
            company_responses = self.get_company_responses(company_id)
            omission_map = self.get_omission_map(company_id)
            status_map = self.get_disclosure_status_map(company_id)
            page_map = self.get_disclosure_page_map(company_id)

            return {
                'indicators': content_index,
                'responses': company_responses,
                'omissions': omission_map,
                'generated_at': datetime.now().isoformat(),
                'total_indicators': len(indicators),
                'status_map': status_map,
                'page_map': page_map
            }

        except Exception as e:
            logging.error(f"Content Index oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def get_company_responses(self, company_id: int) -> Dict:
        """Şirket yanıtlarını al"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    gr.indicator_id,
                    gr.period,
                    gr.response_value,
                    gr.numerical_value,
                    gr.unit,
                    gr.methodology,
                    gr.reporting_status,
                    gr.evidence_url,
                    gr.notes,
                    gi.code as disclosure_code
                FROM gri_responses gr
                JOIN gri_indicators gi ON gr.indicator_id = gi.id
                WHERE gr.company_id = ?
                ORDER BY gi.code
            """, (company_id,))

            responses = cursor.fetchall()

            # Response'ları indicator_id bazında organize et
            response_dict = {}
            for response in responses:
                indicator_id = response[0]
                response_dict[indicator_id] = {
                    'period': response[1],
                    'response_value': response[2],
                    'numerical_value': response[3],
                    'unit': response[4],
                    'methodology': response[5],
                    'reporting_status': response[6],
                    'evidence_url': response[7],
                    'notes': response[8],
                    'disclosure_code': response[9]
                }

            return response_dict

        except Exception as e:
            logging.error(f"Company responses alma hatası: {e}")
            return {}
        finally:
            conn.close()

    def get_omission_map(self, company_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            result = {}
            # GRI 3 omissions
            cursor.execute(
                """
                SELECT disclosure_number, omission_reason
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, reason in cursor.fetchall():
                result[str(disclosure)] = reason or ''

            # GRI 2 omissions
            cursor.execute(
                """
                SELECT disclosure_number, omission_reason
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, reason in cursor.fetchall():
                # Prefer non-empty reason; otherwise keep existing
                if str(disclosure) not in result or (reason and str(reason).strip()):
                    result[str(disclosure)] = reason or ''

            return result
        except Exception:
            return {}
        finally:
            conn.close()

    def get_disclosure_status_map(self, company_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            status_map: Dict[str, str] = {}
            # GRI 3 statuses
            cursor.execute(
                """
                SELECT disclosure_number, reporting_status
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, status in cursor.fetchall():
                status_map[str(disclosure)] = status or ''

            # GRI 2 statuses
            cursor.execute(
                """
                SELECT disclosure_number, reporting_status
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, status in cursor.fetchall():
                status_map[str(disclosure)] = status or status_map.get(str(disclosure), '')

            return status_map
        except Exception:
            return {}
        finally:
            conn.close()

    def get_disclosure_page_map(self, company_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            page_map: Dict[str, Optional[int]] = {}
            # GRI 3 pages
            cursor.execute(
                """
                SELECT disclosure_number, page_number
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, page in cursor.fetchall():
                page_map[str(disclosure)] = page

            # GRI 2 pages
            cursor.execute(
                """
                SELECT disclosure_number, page_number
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for disclosure, page in cursor.fetchall():
                page_map[str(disclosure)] = page if page is not None else page_map.get(str(disclosure))

            return page_map
        except Exception:
            return {}
        finally:
            conn.close()

    def export_to_excel(self, output_path: str, company_id: int = 1) -> bool:
        """Content Index'i Excel'e export et"""
        try:
            logging.info(f"GRI Content Index Excel export başlıyor: {output_path}")

            # Content Index oluştur
            content_data = self.generate_content_index(company_id)
            if not content_data:
                logging.info("Content Index oluşturulamadı!")
                return False

            # Çıkış klasörünü oluştur
            out_dir = os.path.dirname(output_path)
            if out_dir:
                try:
                    os.makedirs(out_dir, exist_ok=True)
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            # Excel writer oluştur
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # 1. Özet Sayfası
                self.create_summary_sheet(writer, content_data)

                # 2. Universal Standards
                self.create_category_sheet(writer, content_data['indicators']['universal'],
                                         'Universal Standards', content_data['responses'], content_data.get('omissions', {}), content_data.get('status_map', {}), content_data.get('page_map', {}))

                # 3. Economic Standards
                self.create_category_sheet(writer, content_data['indicators']['economic'],
                                         'Economic Standards', content_data['responses'], content_data.get('omissions', {}), content_data.get('status_map', {}), content_data.get('page_map', {}))

                # 4. Environmental Standards
                self.create_category_sheet(writer, content_data['indicators']['environmental'],
                                         'Environmental Standards', content_data['responses'], content_data.get('omissions', {}), content_data.get('status_map', {}), content_data.get('page_map', {}))

                # 5. Social Standards
                self.create_category_sheet(writer, content_data['indicators']['social'],
                                         'Social Standards', content_data['responses'], content_data.get('omissions', {}), content_data.get('status_map', {}), content_data.get('page_map', {}))

                # 6. Sector-Specific Standards
                self.create_category_sheet(writer, content_data['indicators']['sector'],
                                         'Sector-Specific Standards', content_data['responses'], content_data.get('omissions', {}), content_data.get('status_map', {}), content_data.get('page_map', {}))

                # 7. Mapping Sayfası
                self.create_mapping_sheet(writer, content_data)

            logging.info(f"GRI Content Index başarıyla export edildi: {output_path}")
            return True

        except Exception as e:
            logging.error(f"Excel export hatası: {e}")
            return False

    def create_summary_sheet(self, writer, content_data) -> None:
        """Özet sayfası oluştur"""
        summary_data = []

        # Kategori bazında özet
        categories = ['universal', 'economic', 'environmental', 'social', 'sector']
        category_names = {
            'universal': 'Universal Standards',
            'economic': 'Economic Standards',
            'environmental': 'Environmental Standards',
            'social': 'Social Standards',
            'sector': 'Sector-Specific Standards'
        }

        for category in categories:
            indicators = content_data['indicators'][category]
            responses = content_data['responses']

            total_indicators = len(indicators)
            responded_indicators = sum(1 for ind in indicators if ind[0] in responses)

            summary_data.append({
                'Kategori': category_names[category],
                'Toplam Gösterge': total_indicators,
                'Yanıtlanan Gösterge': responded_indicators,
                'Yanıtlanma Oranı (%)': round((responded_indicators / total_indicators * 100) if total_indicators > 0 else 0, 1),
                'Son Güncelleme': content_data['generated_at']
            })

        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Özet', index=False)

        # Sayfa formatlaması
        worksheet = writer.sheets['Özet']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def create_category_sheet(self, writer, indicators, sheet_name, responses, omissions, status_map, page_map) -> None:
        """Kategori sayfası oluştur"""
        if not indicators:
            # Boş sayfa oluştur
            df = pd.DataFrame({'Mesaj': ['Bu kategoride gösterge bulunmamaktadır.']})
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        sheet_data = []

        for indicator in indicators:
            indicator_id = indicator[0]
            response = responses.get(indicator_id, {})
            disclosure_code = indicator[1]
            omission_reason = omissions.get(str(disclosure_code), '')
            status = status_map.get(str(disclosure_code), response.get('reporting_status', ''))
            page_ref = page_map.get(str(disclosure_code))

            sheet_data.append({
                'GRI Standard': indicator[30],  # standard_code
                'Disclosure': indicator[1],     # disclosure_code
                'Disclosure Title': indicator[2],  # disclosure_title
                'Description': indicator[3],    # description
                'Unit': indicator[4],          # unit
                'Methodology': indicator[5],    # methodology
                'Reporting Requirement': indicator[6],  # reporting_requirement
                'Priority': indicator[7],       # priority
                'Requirement Level': indicator[8],  # requirement_level
                'Reporting Frequency': indicator[9],  # reporting_frequency
                'Data Quality': indicator[10],   # data_quality
                'Audit Required': indicator[11], # audit_required
                'Validation Required': indicator[12],  # validation_required
                'Digitalization Status': indicator[13],  # digitalization_status
                'Cost Level': indicator[14],    # cost_level
                'Time Requirement': indicator[15],  # time_requirement
                'Expertise Requirement': indicator[16],  # expertise_requirement
                'Sustainability Impact': indicator[17],  # sustainability_impact
                'Legal Compliance': indicator[18],  # legal_compliance
                'Sector Specific': indicator[19],  # sector_specific
                'International Standard': indicator[20],  # international_standard
                'Metric Type': indicator[21],   # metric_type
                'Scale Unit': indicator[22],    # scale_unit
                'Data Source System': indicator[23],  # data_source_system
                'Reporting Format': indicator[24],  # reporting_format
                'TSRS ESRS Mapping': indicator[25],  # tsrs_esrs_mapping
                'UN SDG Mapping': indicator[26],  # un_sdg_mapping
                'GRI 3-3 Reference': indicator[27],  # gri_3_3_reference
                'Impact Area': indicator[28],   # impact_area
                'Stakeholder Group': indicator[29],  # stakeholder_group
                'Response Value': response.get('response_value', ''),
                'Numerical Value': response.get('numerical_value', ''),
                'Response Unit': response.get('unit', ''),
                'Response Methodology': response.get('methodology', ''),
                'Reporting Status': response.get('reporting_status', ''),
                'Evidence URL': response.get('evidence_url', ''),
                'Notes': response.get('notes', ''),
                'Page Reference': page_ref if page_ref is not None else '',
                'Omission': 'Yes' if status == 'Omitted' else 'No',
                'Reason for Omission': omission_reason if status == 'Omitted' else ''
            })

        df = pd.DataFrame(sheet_data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Sayfa formatlaması
        worksheet = writer.sheets[sheet_name]
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    def create_mapping_sheet(self, writer, content_data) -> None:
        """Mapping sayfası oluştur"""
        mapping_data = []

        # SDG-GRI mapping
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT 
                    mg.sdg_indicator_code,
                    mg.gri_standard,
                    mg.gri_disclosure,
                    mg.relation_type,
                    mg.notes
                FROM map_sdg_gri mg
                ORDER BY mg.sdg_indicator_code, mg.gri_standard
            """)

            sdg_gri_mappings = cursor.fetchall()

            for mapping in sdg_gri_mappings:
                relation = mapping[3] if (mapping[3] is not None and str(mapping[3]).strip().lower() != 'none') else ''
                note = mapping[4] if (mapping[4] is not None and str(mapping[4]).strip().lower() != 'none') else ''
                mapping_data.append({
                    'SDG Indicator': mapping[0],
                    'GRI Standard': mapping[1],
                    'GRI Disclosure': mapping[2],
                    'Relation Type': relation,
                    'Notes': note,
                    'Mapping Type': 'SDG-GRI'
                })

            # TSRS-GRI mapping
            cursor.execute("""
                SELECT 
                    mt.gri_standard,
                    mt.gri_disclosure,
                    mt.tsrs_section,
                    mt.tsrs_metric,
                    mt.relation_type,
                    mt.notes
                FROM map_gri_tsrs mt
                ORDER BY mt.gri_standard, mt.gri_disclosure
            """)

            tsrs_gri_mappings = cursor.fetchall()

            for mapping in tsrs_gri_mappings:
                relation = mapping[4] if (mapping[4] is not None and str(mapping[4]).strip().lower() != 'none') else ''
                note = mapping[5] if (mapping[5] is not None and str(mapping[5]).strip().lower() != 'none') else ''
                mapping_data.append({
                    'SDG Indicator': '',
                    'GRI Standard': mapping[0],
                    'GRI Disclosure': mapping[1],
                    'Relation Type': relation,
                    'Notes': note,
                    'Mapping Type': 'GRI-TSRS',
                    'TSRS Section': mapping[2],
                    'TSRS Metric': mapping[3]
                })

        except Exception as e:
            logging.error(f"Mapping verisi alma hatası: {e}")
        finally:
            conn.close()

        df = pd.DataFrame(mapping_data)
        df.to_excel(writer, sheet_name='Mappings', index=False)

        # Sayfa formatlaması
        worksheet = writer.sheets['Mappings']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

def export_gri_content_index(output_path: str, company_id: int = 1, db_path: str = None) -> None:
    """GRI Content Index export fonksiyonu"""
    content_index = GRIContentIndex(db_path=db_path or DB_PATH)
    return content_index.export_to_excel(output_path, company_id)

if __name__ == "__main__":
    # Test export
    output_file = "gri/gri_content_index_test.xlsx"
    if export_gri_content_index(output_file):
        logging.info(f"GRI Content Index başarıyla oluşturuldu: {output_file}")
    else:
        logging.info("GRI Content Index oluşturulamadı!")
