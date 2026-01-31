#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Excel Importer v1 - Sprint 1
gri.xlsx dosyasından veritabanına veri aktarımı
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict

import pandas as pd
from config.database import DB_PATH


class GRIExcelImporter:
    """GRI Excel verilerini veritabanına aktaran sınıf"""

    def __init__(self, db_path: str = DB_PATH, excel_path: str = "gri/gri.xlsx") -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

        # excel_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(excel_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            excel_path = os.path.join(base_dir, excel_path)
        self.excel_path = excel_path

        # İstatistikler
        self.stats = {
            'standards_added': 0,
            'standards_updated': 0,
            'indicators_added': 0,
            'indicators_updated': 0,
            'errors': [],
            'warnings': []
        }

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def load_excel_data(self) -> Dict[str, pd.DataFrame]:
        """Excel dosyasından tüm sayfaları yükle"""
        try:
            logging.info(f"Excel dosyası yükleniyor: {self.excel_path}")

            # Tüm sayfaları yükle
            excel_data = pd.read_excel(self.excel_path, sheet_name=None)

            logging.info(f"Yüklenen sayfalar: {list(excel_data.keys())}")

            return excel_data

        except Exception as e:
            error_msg = f"Excel dosyası yükleme hatası: {e}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            return {}

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sütun adlarını normalize et (TR/EN varyantları)"""
        # Sütun adı eşleştirme sözlüğü
        column_mapping = {
            'GRI_Standard': 'standard_code',
            'Standard Code': 'standard_code',
            'Kod': 'disclosure_code',
            'Code': 'disclosure_code',
            'Başlık': 'title',
            'Title': 'title',
            'Baslik': 'title',
            'Açıklama': 'description',
            'Description': 'description',
            'Aciklama': 'description',
            'Kategori': 'category',
            'Category': 'category',
            'Alt_Kategori': 'sub_category',
            'Sub Category': 'sub_category',
            'Birim': 'unit',
            'Unit': 'unit',
            'Metodoloji': 'methodology',
            'Methodology': 'methodology',
            'Raporlama_Durumu': 'reporting_requirement',
            'Reporting Requirement': 'reporting_requirement',
            'Gereklilik_Seviyesi': 'requirement_level',
            'Requirement Level': 'requirement_level',
            'Oncelik': 'priority',
            'Priority': 'priority',
            'Veri_Kalitesi': 'data_quality',
            'Data Quality': 'data_quality',
            'Denetim_Gereksinimi': 'audit_required',
            'Audit Required': 'audit_required',
            'Validasyon_Gereksinimi': 'validation_required',
            'Validation Required': 'validation_required',
            'Dijitalleme_Durumu': 'digitalization_status',
            'Digitalization Status': 'digitalization_status',
            'Maliyet_Seviyesi': 'cost_level',
            'Cost Level': 'cost_level',
            'Zaman_Gereksinimi': 'time_requirement',
            'Time Requirement': 'time_requirement',
            'Uzmanlik_Gereksinimi': 'expertise_requirement',
            'Expertise Requirement': 'expertise_requirement',
            'Risk_Seviyesi': 'risk_level',
            'Risk Level': 'risk_level',
            'Sürdürülebilirlik_Etkisi': 'sustainability_impact',
            'Sustainability Impact': 'sustainability_impact',
            'Yasal_Uyumluluk': 'legal_compliance',
            'Legal Compliance': 'legal_compliance',
            'Sektor_Ozel': 'sector_specific',
            'Sector Specific': 'sector_specific',
            'Uluslararasi_Standart': 'international_standard',
            'International Standard': 'international_standard',
            'Metrik_Turu': 'metric_type',
            'Metric Type': 'metric_type',
            'Olcek_Birimi': 'scale_unit',
            'Scale Unit': 'scale_unit',
            'Veri_Kaynak_Sistemi': 'data_source_system',
            'Data Source System': 'data_source_system',
            'Raporlama_Format': 'reporting_format',
            'Reporting Format': 'reporting_format',
            'TSRS_ESRS_Eslesme': 'tsrs_esrs_mapping',
            'TSRS ESRS Mapping': 'tsrs_esrs_mapping',
            'UN_SDG_Eslesme': 'un_sdg_mapping',
            'UN SDG Mapping': 'un_sdg_mapping',
            'GRI_3_3_Referansi': 'gri_3_3_reference',
            'GRI 3-3 Reference': 'gri_3_3_reference',
            'Etki_Alani': 'impact_area',
            'Impact Area': 'impact_area',
            'Paydas_Grubu': 'stakeholder_group',
            'Stakeholder Group': 'stakeholder_group'
        }

        # Sütun adlarını güncelle
        df = df.rename(columns=column_mapping)

        return df

    def import_standards(self, df: pd.DataFrame) -> bool:
        """Standartları import et"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("\nStandartlar import ediliyor...")

            # Benzersiz standartları al
            standards_df = df[['standard_code']].drop_duplicates()

            for _, row in standards_df.iterrows():
                standard_code = str(row['standard_code']).strip()

                if pd.isna(standard_code) or standard_code == '' or standard_code == 'nan':
                    continue

                # Standart bilgilerini al (ilk satırdan)
                standard_rows = df[df['standard_code'] == standard_code]
                if len(standard_rows) == 0:
                    continue

                standard_row = standard_rows.iloc[0]

                # Güvenli değer alma
                def safe_get(row, key, default='') -> None:
                    try:
                        value = row.get(key, default)
                        if pd.isna(value) or str(value) == 'nan':
                            return default
                        return str(value).strip()
                    except Exception:
                        return default

                title = safe_get(standard_row, 'title')
                category = safe_get(standard_row, 'category')
                sub_category = safe_get(standard_row, 'sub_category')
                description = safe_get(standard_row, 'description')

                # Standart türünü belirle
                if 'GRI 1' in standard_code or 'GRI 2' in standard_code or 'GRI 3' in standard_code:
                    standard_type = 'Universal'
                elif standard_code.startswith('GRI 20'):
                    standard_type = 'Economic'
                elif standard_code.startswith('GRI 30'):
                    standard_type = 'Environmental'
                elif standard_code.startswith('GRI 40'):
                    standard_type = 'Social'
                else:
                    standard_type = 'Sector-Specific'

                # Upsert standart
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_standards 
                    (code, title, category, type, sub_category, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (standard_code, title, category, standard_type, sub_category, description, datetime.now().isoformat()))

                if cursor.rowcount > 0:
                    self.stats['standards_added'] += 1

            conn.commit()
            logging.info(f"Standartlar import edildi: {self.stats['standards_added']} standart")
            return True

        except Exception as e:
            error_msg = f"Standartlar import hatası: {e}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            conn.rollback()
            return False
        finally:
            conn.close()

    def import_indicators(self, df: pd.DataFrame) -> bool:
        """Göstergeleri import et"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("\nGöstergeler import ediliyor...")

            for _, row in df.iterrows():
                standard_code = str(row.get('standard_code', '')).strip()
                disclosure_code = str(row.get('disclosure_code', '')).strip()

                if pd.isna(standard_code) or standard_code == '' or standard_code == 'nan':
                    continue

                if pd.isna(disclosure_code) or disclosure_code == '' or disclosure_code == 'nan':
                    continue

                # Standart ID'sini al
                cursor.execute("SELECT id FROM gri_standards WHERE code = ?", (standard_code,))
                standard_result = cursor.fetchone()

                if not standard_result:
                    # Standart bulunamadı, önce oluştur
                    logging.info(f"Standart bulunamadı, oluşturuluyor: {standard_code}")

                    # Standart türünü belirle
                    if 'GRI 1' in standard_code or 'GRI 2' in standard_code or 'GRI 3' in standard_code:
                        standard_type = 'Universal'
                        category = 'Universal'
                    elif standard_code.startswith('GRI 20'):
                        standard_type = 'Economic'
                        category = 'Economic'
                    elif standard_code.startswith('GRI 30'):
                        standard_type = 'Environmental'
                        category = 'Environmental'
                    elif standard_code.startswith('GRI 40'):
                        standard_type = 'Social'
                        category = 'Social'
                    else:
                        standard_type = 'Sector-Specific'
                        category = 'Sector-Specific'

                    # Standart oluştur
                    cursor.execute("""
                        INSERT INTO gri_standards (code, title, category, type, description, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (standard_code, standard_code, category, standard_type, '', datetime.now().isoformat()))

                    standard_id = cursor.lastrowid
                    logging.info(f"Yeni standart oluşturuldu: {standard_code} (ID: {standard_id})")
                else:
                    standard_id = standard_result[0]

                # Güvenli değer alma fonksiyonu
                def safe_get(row, key, default='') -> None:
                    try:
                        value = row.get(key, default)
                        if pd.isna(value) or str(value) == 'nan':
                            return default
                        return str(value).strip()
                    except Exception:
                        return default

                # Gösterge bilgilerini hazırla
                title = safe_get(row, 'title')
                description = safe_get(row, 'description')
                unit = safe_get(row, 'unit')
                methodology = safe_get(row, 'methodology')
                reporting_requirement = safe_get(row, 'reporting_requirement')

                # Ek alanlar
                priority = safe_get(row, 'priority')
                requirement_level = safe_get(row, 'requirement_level')
                reporting_frequency = safe_get(row, 'reporting_frequency')
                data_quality = safe_get(row, 'data_quality')
                audit_required = safe_get(row, 'audit_required')
                validation_required = safe_get(row, 'validation_required')
                digitalization_status = safe_get(row, 'digitalization_status')
                cost_level = safe_get(row, 'cost_level')
                time_requirement = safe_get(row, 'time_requirement')
                expertise_requirement = safe_get(row, 'expertise_requirement')
                safe_get(row, 'risk_level')
                sustainability_impact = safe_get(row, 'sustainability_impact')
                legal_compliance = safe_get(row, 'legal_compliance')
                sector_specific = safe_get(row, 'sector_specific')
                international_standard = safe_get(row, 'international_standard')
                metric_type = safe_get(row, 'metric_type')
                scale_unit = safe_get(row, 'scale_unit')
                data_source_system = safe_get(row, 'data_source_system')
                reporting_format = safe_get(row, 'reporting_format')
                tsrs_esrs_mapping = safe_get(row, 'tsrs_esrs_mapping')
                un_sdg_mapping = safe_get(row, 'un_sdg_mapping')
                gri_3_3_reference = safe_get(row, 'gri_3_3_reference')
                impact_area = safe_get(row, 'impact_area')
                stakeholder_group = safe_get(row, 'stakeholder_group')

                # Upsert gösterge
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement,
                     priority, requirement_level, reporting_frequency, data_quality, audit_required,
                     validation_required, digitalization_status, cost_level, time_requirement,
                     expertise_requirement, sustainability_impact, legal_compliance,
                     sector_specific, international_standard, metric_type, scale_unit,
                     data_source_system, reporting_format, tsrs_esrs_mapping, un_sdg_mapping,
                     gri_3_3_reference, impact_area, stakeholder_group, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    standard_id, disclosure_code, title, description, unit, methodology, reporting_requirement,
                    priority, requirement_level, reporting_frequency, data_quality, audit_required,
                    validation_required, digitalization_status, cost_level, time_requirement,
                    expertise_requirement, sustainability_impact, legal_compliance,
                    sector_specific, international_standard, metric_type, scale_unit,
                    data_source_system, reporting_format, tsrs_esrs_mapping, un_sdg_mapping,
                    gri_3_3_reference, impact_area, stakeholder_group, datetime.now().isoformat()
                ))

                if cursor.rowcount > 0:
                    self.stats['indicators_added'] += 1

            conn.commit()
            logging.info(f"Göstergeler import edildi: {self.stats['indicators_added']} gösterge")
            return True

        except Exception as e:
            error_msg = f"Göstergeler import hatası: {e}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            conn.rollback()
            return False
        finally:
            conn.close()

    def import_analytical_data(self, excel_data: Dict[str, pd.DataFrame]) -> bool:
        """Analiz sayfalarını import et"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("\nAnaliz verileri import ediliyor...")

            # KPI Listesi
            if 'KPI_Listesi' in excel_data:
                kpi_df = excel_data['KPI_Listesi']
                kpi_df = self.normalize_column_names(kpi_df)

                for _, row in kpi_df.iterrows():
                    # Güvenli değer alma
                    def safe_get(row, key, default='') -> None:
                        try:
                            value = row.get(key, default)
                            if pd.isna(value) or str(value) == 'nan':
                                return default
                            return str(value).strip()
                        except Exception:
                            return default

                    standard_code = safe_get(row, 'standard_code')
                    disclosure_code = safe_get(row, 'disclosure_code')

                    if not standard_code or not disclosure_code:
                        continue

                    # Gösterge ID'sini al
                    cursor.execute("""
                        SELECT gi.id FROM gri_indicators gi
                        JOIN gri_standards gs ON gi.standard_id = gs.id
                        WHERE gs.code = ? AND gi.code = ?
                    """, (standard_code, disclosure_code))

                    indicator_result = cursor.fetchone()
                    if not indicator_result:
                        continue

                    indicator_id = indicator_result[0]

                    kpi_name = safe_get(row, 'kpi') or safe_get(row, 'KPI', standard_code + ' KPI')
                    formula = safe_get(row, 'formula') or safe_get(row, 'Formula')
                    unit = safe_get(row, 'unit') or safe_get(row, 'Birim')
                    frequency = safe_get(row, 'frequency') or safe_get(row, 'Raporlama_Sikligi')
                    owner = safe_get(row, 'owner') or safe_get(row, 'Sorumlu_Birim')
                    notes = safe_get(row, 'notes') or safe_get(row, 'Notlar')

                    cursor.execute("""
                        INSERT OR REPLACE INTO gri_kpis 
                        (indicator_id, name, formula, unit, frequency, owner, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (indicator_id, kpi_name, formula, unit, frequency, owner, notes, datetime.now().isoformat()))

            # Hedefler 2024-2025
            if 'Hedefler_2024_2025' in excel_data:
                targets_df = excel_data['Hedefler_2024_2025']
                targets_df = self.normalize_column_names(targets_df)

                for _, row in targets_df.iterrows():
                    # Güvenli değer alma
                    def safe_get(row, key, default='') -> None:
                        try:
                            value = row.get(key, default)
                            if pd.isna(value) or str(value) == 'nan':
                                return default
                            return str(value).strip()
                        except Exception:
                            return default

                    standard_code = safe_get(row, 'standard_code')
                    disclosure_code = safe_get(row, 'disclosure_code')

                    if not standard_code or not disclosure_code:
                        continue

                    # Gösterge ID'sini al
                    cursor.execute("""
                        SELECT gi.id FROM gri_indicators gi
                        JOIN gri_standards gs ON gi.standard_id = gs.id
                        WHERE gs.code = ? AND gi.code = ?
                    """, (standard_code, disclosure_code))

                    indicator_result = cursor.fetchone()
                    if not indicator_result:
                        continue

                    indicator_id = indicator_result[0]

                    # 2024 hedefi
                    target_2024 = safe_get(row, 'hedef_2024') or safe_get(row, 'Hedef_2024')
                    if target_2024:
                        cursor.execute("""
                            INSERT OR REPLACE INTO gri_targets 
                            (indicator_id, year, target_value, unit, method, notes, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (indicator_id, 2024, target_2024, '', '', '', datetime.now().isoformat()))

                    # 2025 hedefi
                    target_2025 = safe_get(row, 'hedef_2025') or safe_get(row, 'Hedef_2025')
                    if target_2025:
                        cursor.execute("""
                            INSERT OR REPLACE INTO gri_targets 
                            (indicator_id, year, target_value, unit, method, notes, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (indicator_id, 2025, target_2025, '', '', '', datetime.now().isoformat()))

            # Risk Sırası
            if 'Risk_Sirasi' in excel_data:
                risk_df = excel_data['Risk_Sirasi']
                risk_df = self.normalize_column_names(risk_df)

                for _, row in risk_df.iterrows():
                    # Güvenli değer alma
                    def safe_get(row, key, default='') -> None:
                        try:
                            value = row.get(key, default)
                            if pd.isna(value) or str(value) == 'nan':
                                return default
                            return str(value).strip()
                        except Exception:
                            return default

                    standard_code = safe_get(row, 'standard_code')
                    disclosure_code = safe_get(row, 'disclosure_code')

                    if not standard_code or not disclosure_code:
                        continue

                    # Gösterge ID'sini al
                    cursor.execute("""
                        SELECT gi.id FROM gri_indicators gi
                        JOIN gri_standards gs ON gi.standard_id = gs.id
                        WHERE gs.code = ? AND gi.code = ?
                    """, (standard_code, disclosure_code))

                    indicator_result = cursor.fetchone()
                    if not indicator_result:
                        continue

                    indicator_id = indicator_result[0]

                    risk_level = safe_get(row, 'risk_level') or safe_get(row, 'Risk_Seviyesi')
                    impact = safe_get(row, 'impact') or safe_get(row, 'Impact')
                    likelihood = safe_get(row, 'likelihood') or safe_get(row, 'Likelihood')
                    notes = safe_get(row, 'notes') or safe_get(row, 'Notlar')

                    cursor.execute("""
                        INSERT OR REPLACE INTO gri_risks 
                        (indicator_id, risk_level, impact, likelihood, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (indicator_id, risk_level, impact, likelihood, notes, datetime.now().isoformat()))

            conn.commit()
            logging.info("Analiz verileri import edildi")
            return True

        except Exception as e:
            error_msg = f"Analiz verileri import hatası: {e}"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            conn.rollback()
            return False
        finally:
            conn.close()

    def generate_import_report(self) -> str:
        """Import raporu oluştur"""
        report = []
        report.append("=== GRI EXCEL IMPORT RAPORU ===")
        report.append(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        report.append("=== İSTATİSTİKLER ===")
        report.append(f"Eklenen Standartlar: {self.stats['standards_added']}")
        report.append(f"Güncellenen Standartlar: {self.stats['standards_updated']}")
        report.append(f"Eklenen Göstergeler: {self.stats['indicators_added']}")
        report.append(f"Güncellenen Göstergeler: {self.stats['indicators_updated']}")
        report.append("")

        if self.stats['errors']:
            report.append("=== HATALAR ===")
            for i, error in enumerate(self.stats['errors'], 1):
                report.append(f"{i}. {error}")
            report.append("")

        if self.stats['warnings']:
            report.append("=== UYARILAR ===")
            for i, warning in enumerate(self.stats['warnings'], 1):
                report.append(f"{i}. {warning}")
            report.append("")

        report.append("=== SONUC ===")
        if not self.stats['errors']:
            report.append("Import basariyla tamamlandi!")
        else:
            report.append("Import sirasinda hatalar olustu!")

        return "\n".join(report)

    def import_all(self) -> bool:
        """Tüm import işlemini gerçekleştir"""
        logging.info("GRI Excel Import Başlıyor...")

        # 1. Excel verilerini yükle
        excel_data = self.load_excel_data()
        if not excel_data:
            return False

        # 2. Ana standartlar sayfasını bul
        main_sheet = None
        for sheet_name in ['GRI_Standartlari', 'GRI_Standartları', 'Standards']:
            if sheet_name in excel_data:
                main_sheet = sheet_name
                break

        if not main_sheet:
            error_msg = "Ana standartlar sayfası bulunamadı!"
            logging.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False

        logging.info(f"Ana sayfa bulundu: {main_sheet}")

        # 3. Verileri normalize et
        df = excel_data[main_sheet]
        df = self.normalize_column_names(df)

        # 4. Standartları import et
        if not self.import_standards(df):
            return False

        # 5. Göstergeleri import et
        if not self.import_indicators(df):
            return False

        # 6. Analiz verilerini import et
        if not self.import_analytical_data(excel_data):
            return False

        # 7. Rapor oluştur
        report = self.generate_import_report()
        logging.info("\n" + report)

        # 8. Raporu dosyaya kaydet
        report_file = "gri/gri_import_report.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logging.info(f"\nImport raporu kaydedildi: {report_file}")
        except Exception as e:
            logging.error(f"Rapor kaydetme hatası: {e}")

        return len(self.stats['errors']) == 0

def import_gri_excel() -> None:
    """GRI Excel import fonksiyonu"""
    importer = GRIExcelImporter()
    return importer.import_all()

if __name__ == "__main__":
    import_gri_excel()
