import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Content Index Export - Sprint 3
GRI Content Index template 2021 ile uyumlu Excel export
"""

import os
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager

class GRIContentIndex(BaseTenantManager):
    """GRI Content Index sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        super().__init__(db_path)

    def generate_content_index(self, company_id: int = 1) -> Dict:
        """GRI Content Index oluştur"""
        try:
            logging.info("GRI Content Index oluşturuluyor...")

            # Tüm göstergeleri al
            indicators = self.execute_query("""
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

            # Kategori bazında organize et
            content_index = {
                'universal': [],
                'economic': [],
                'environmental': [],
                'social': [],
                'sector': []
            }

            for indicator in indicators:
                category = indicator['category']
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

    def get_company_responses(self, company_id: int) -> Dict:
        """Şirket yanıtlarını al"""
        try:
            responses = self.execute_query("""
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

            # Response'ları indicator_id bazında organize et
            response_dict = {}
            for response in responses:
                indicator_id = response['indicator_id']
                response_dict[indicator_id] = {
                    'period': response['period'],
                    'response_value': response['response_value'],
                    'numerical_value': response['numerical_value'],
                    'unit': response['unit'],
                    'methodology': response['methodology'],
                    'reporting_status': response['reporting_status'],
                    'evidence_url': response['evidence_url'],
                    'notes': response['notes'],
                    'disclosure_code': response['disclosure_code']
                }

            return response_dict

        except Exception as e:
            logging.error(f"Company responses alma hatası: {e}")
            return {}

    def get_omission_map(self, company_id: int) -> Dict:
        try:
            result = {}
            # GRI 3 omissions
            gri_3_omissions = self.execute_query(
                """
                SELECT disclosure_number, omission_reason
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_3_omissions:
                result[str(row['disclosure_number'])] = row['omission_reason'] or ''

            # GRI 2 omissions
            gri_2_omissions = self.execute_query(
                """
                SELECT disclosure_number, omission_reason
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_2_omissions:
                disclosure = row['disclosure_number']
                reason = row['omission_reason']
                # Prefer non-empty reason; otherwise keep existing
                if str(disclosure) not in result or (reason and str(reason).strip()):
                    result[str(disclosure)] = reason or ''

            return result
        except Exception:
            return {}

    def get_disclosure_status_map(self, company_id: int) -> Dict:
        try:
            status_map: Dict[str, str] = {}
            # GRI 3 statuses
            gri_3_statuses = self.execute_query(
                """
                SELECT disclosure_number, reporting_status
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_3_statuses:
                status_map[str(row['disclosure_number'])] = row['reporting_status'] or ''

            # GRI 2 statuses
            gri_2_statuses = self.execute_query(
                """
                SELECT disclosure_number, reporting_status
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_2_statuses:
                disclosure = row['disclosure_number']
                status = row['reporting_status']
                status_map[str(disclosure)] = status or status_map.get(str(disclosure), '')

            return status_map
        except Exception:
            return {}

    def get_disclosure_page_map(self, company_id: int) -> Dict:
        try:
            page_map: Dict[str, Optional[int]] = {}
            # GRI 3 pages
            gri_3_pages = self.execute_query(
                """
                SELECT disclosure_number, page_number
                FROM gri_3_content_index
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_3_pages:
                page_map[str(row['disclosure_number'])] = row['page_number']

            # GRI 2 pages
            gri_2_pages = self.execute_query(
                """
                SELECT disclosure_number, page_number
                FROM gri_2_general_disclosures
                WHERE company_id = ?
                """,
                (company_id,),
            )
            for row in gri_2_pages:
                disclosure = row['disclosure_number']
                page = row['page_number']
                page_map[str(disclosure)] = page if page is not None else page_map.get(str(disclosure))

            return page_map
        except Exception:
            return {}

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
            indicator_id = indicator['id']
            response = responses.get(indicator_id, {})
            disclosure_code = indicator['disclosure_code']
            omission_reason = omissions.get(str(disclosure_code), '')
            status = status_map.get(str(disclosure_code), response.get('reporting_status', ''))
            page_ref = page_map.get(str(disclosure_code))

            sheet_data.append({
                'GRI Standard': indicator['standard_code'],
                'Disclosure': indicator['disclosure_code'],
                'Disclosure Title': indicator['disclosure_title'],
                'Description': indicator['description'],
                'Unit': indicator['unit'],
                'Methodology': indicator['methodology'],
                'Reporting Requirement': indicator['reporting_requirement'],
                'Priority': indicator['priority'],
                'Requirement Level': indicator['requirement_level'],
                'Reporting Frequency': indicator['reporting_frequency'],
                'Data Quality': indicator['data_quality'],
                'Audit Required': indicator['audit_required'],
                'Validation Required': indicator['validation_required'],
                'Digitalization Status': indicator['digitalization_status'],
                'Cost Level': indicator['cost_level'],
                'Time Requirement': indicator['time_requirement'],
                'Expertise Requirement': indicator['expertise_requirement'],
                'Sustainability Impact': indicator['sustainability_impact'],
                'Legal Compliance': indicator['legal_compliance'],
                'Sector Specific': indicator['sector_specific'],
                'International Standard': indicator['international_standard'],
                'Metric Type': indicator['metric_type'],
                'Scale Unit': indicator['scale_unit'],
                'Data Source System': indicator['data_source_system'],
                'Reporting Format': indicator['reporting_format'],
                'TSRS ESRS Mapping': indicator['tsrs_esrs_mapping'],
                'UN SDG Mapping': indicator['un_sdg_mapping'],
                'GRI 3-3 Reference': indicator['gri_3_3_reference'],
                'Impact Area': indicator['impact_area'],
                'Stakeholder Group': indicator['stakeholder_group'],
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
