import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS (Türkiye Sürdürülebilirlik Raporlama Standardı) Manager
TSRS standartları, göstergeleri ve raporlama yönetimi
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from config.database import DB_PATH


from backend.core.base_manager import BaseTenantManager

class TSRSManager(BaseTenantManager):
    """TSRS modülü yöneticisi"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)

    def create_tables(self) -> bool:
        """TSRS tablolarını oluştur"""
        try:
            # TSRS şema dosyasını oku ve çalıştır
            schema_file = os.path.join(os.path.dirname(__file__), 'tsrs_schema.sql')
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            # SQL komutlarını çalıştır
            self.db.execute_script(schema_sql)
            logging.info("TSRS tabloları başarıyla oluşturuldu")
            return True

        except Exception as e:
            logging.error(f"TSRS tabloları oluşturulurken hata: {e}")
            return False

    def get_tsrs_standards(self, category: Optional[str] = None) -> List[Dict]:
        """TSRS standartlarını getir"""
        try:
            if category:
                query = """
                    SELECT id, code, title, description, category, subcategory, 
                           requirement_level, reporting_frequency, effective_date
                    FROM tsrs_standards 
                    WHERE category = ?
                    ORDER BY code
                """
                return self.execute_query(query, (category,), skip_tenant_filter=True)
            else:
                query = """
                    SELECT id, code, title, description, category, subcategory, 
                           requirement_level, reporting_frequency, effective_date
                    FROM tsrs_standards 
                    ORDER BY category, code
                """
                return self.execute_query(query, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS standartları getirilirken hata: {e}")
            return []

    def get_tsrs_indicators(self) -> List[Dict]:
        """Tüm TSRS göstergelerini getir"""
        try:
            query = """
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology,
                       i.data_type, i.is_mandatory, i.is_quantitative, 
                       i.baseline_year, i.target_year, i.standard_id
                FROM tsrs_indicators i
                ORDER BY i.code
            """
            return self.execute_query(query, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS göstergeleri getirilirken hata: {e}")
            return []

    def get_tsrs_indicators_by_standard(self, standard_id: int) -> List[Dict]:
        """Belirli bir standart için göstergeleri getir"""
        try:
            query = """
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology,
                       i.data_type, i.is_mandatory, i.is_quantitative, 
                       i.baseline_year, i.target_year
                FROM tsrs_indicators i
                WHERE i.standard_id = ?
                ORDER BY i.code
            """
            return self.execute_query(query, (standard_id,), skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS göstergeleri getirilirken hata: {e}")
            return []

    def get_tsrs_categories(self) -> List[str]:
        """TSRS kategorilerini getir"""
        try:
            query = """
                SELECT DISTINCT category 
                FROM tsrs_standards 
                ORDER BY category
            """
            results = self.execute_query(query, skip_tenant_filter=True)
            return [row['category'] for row in results]

        except Exception as e:
            logging.error(f"TSRS kategorileri getirilirken hata: {e}")
            return []

    def save_tsrs_response(self, company_id: int, indicator_id: int,
                          reporting_period: str, response_data: Dict) -> bool:
        """TSRS yanıtını kaydet"""
        try:
            # Mevcut yanıtı kontrol et
            existing = self.select_one(
                "tsrs_responses", 
                company_id=company_id,
                columns="id",
                where="indicator_id = ? AND reporting_period = ?",
                params=(indicator_id, reporting_period)
            )

            if existing:
                # Güncelle
                update_data = {
                    'response_value': response_data.get('response_value'),
                    'numerical_value': response_data.get('numerical_value'),
                    'unit': response_data.get('unit'),
                    'methodology_used': response_data.get('methodology_used'),
                    'data_source': response_data.get('data_source'),
                    'reporting_status': response_data.get('reporting_status', 'Draft'),
                    'evidence_url': response_data.get('evidence_url'),
                    'notes': response_data.get('notes'),
                    'updated_at': datetime.now().isoformat()
                }
                self.update(
                    "tsrs_responses", 
                    update_data, 
                    company_id=company_id,
                    where="id = ?", 
                    params=(existing['id'],)
                )
            else:
                # Yeni kayıt
                insert_data = {
                    'indicator_id': indicator_id,
                    'reporting_period': reporting_period,
                    'response_value': response_data.get('response_value'),
                    'numerical_value': response_data.get('numerical_value'),
                    'unit': response_data.get('unit'),
                    'methodology_used': response_data.get('methodology_used'),
                    'data_source': response_data.get('data_source'),
                    'reporting_status': response_data.get('reporting_status', 'Draft'),
                    'evidence_url': response_data.get('evidence_url'),
                    'notes': response_data.get('notes'),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self.insert("tsrs_responses", insert_data, company_id=company_id)

            return True

        except Exception as e:
            logging.error(f"TSRS yanıtı kaydedilirken hata: {e}")
            return False

    def get_tsrs_esrs_mappings(self, tsrs_indicator_id: Optional[int] = None) -> List[Dict]:
        """TSRS-ESRS eşleştirmelerini getir"""
        try:
            query = """
                SELECT m.id, m.tsrs_indicator_id, m.esrs_code, m.relationship_type, m.description,
                       i.code as tsrs_code, i.title as tsrs_title
                FROM map_tsrs_esrs m
                JOIN tsrs_indicators i ON m.tsrs_indicator_id = i.id
            """
            params = []

            if tsrs_indicator_id:
                query += " WHERE m.tsrs_indicator_id = ?"
                params.append(tsrs_indicator_id)
            
            query += " ORDER BY m.esrs_code"

            return self.execute_query(query, tuple(params), skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS-ESRS eşleştirmeleri getirilirken hata: {e}")
            return []

    def add_tsrs_esrs_mapping(self, tsrs_indicator_id: int, esrs_code: str, 
                             relationship_type: str = 'Direct', description: str = '') -> bool:
        """TSRS-ESRS eşleştirmesi ekle"""
        try:
            query = """
                INSERT INTO map_tsrs_esrs (tsrs_indicator_id, esrs_code, relationship_type, description)
                VALUES (?, ?, ?, ?)
            """
            self.execute_update(query, (tsrs_indicator_id, esrs_code, relationship_type, description), skip_tenant_filter=True)
            return True
        except Exception as e:
            logging.error(f"TSRS-ESRS eşleştirmesi eklenirken hata: {e}")
            return False

    def add_tsrs_risk(self, company_id: int, standard_id: int,
                       risk_title: str, risk_description: Optional[str],
                       risk_category: str, probability: str, impact: str,
                       risk_level: str, mitigation_strategy: Optional[str],
                       responsible_person: Optional[str], target_date: Optional[str],
                       status: str) -> bool:
        """TSRS risk kaydı ekle (tsrs_risks tablosu)"""
        try:
            data = {
                'standard_id': standard_id,
                'risk_title': risk_title,
                'risk_description': risk_description,
                'risk_category': risk_category,
                'probability': probability,
                'impact': impact,
                'risk_level': risk_level,
                'mitigation_strategy': mitigation_strategy,
                'responsible_person': responsible_person,
                'target_date': target_date,
                'status': status,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.insert("tsrs_risks", data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"TSRS risk kaydı eklenirken hata: {e}")
            return False

    def get_tsrs_responses(self, company_id: int, reporting_period: Optional[str] = None) -> List[Dict]:
        """Şirket için TSRS yanıtlarını getir"""
        try:
            if reporting_period:
                query = """
                    SELECT r.id, r.indicator_id, r.reporting_period, r.response_value,
                           r.numerical_value, r.unit, r.methodology_used, r.data_source,
                           r.reporting_status, r.evidence_url, r.notes,
                           i.code as indicator_code, i.title as indicator_title,
                           s.code as standard_code, s.title as standard_title, s.category
                    FROM tsrs_responses r
                    JOIN tsrs_indicators i ON r.indicator_id = i.id
                    JOIN tsrs_standards s ON i.standard_id = s.id
                    WHERE r.company_id = ? AND r.reporting_period = ?
                    ORDER BY s.category, s.code, i.code
                """
                return self.execute_query(query, (company_id, reporting_period), company_id=company_id)
            else:
                query = """
                    SELECT r.id, r.indicator_id, r.reporting_period, r.response_value,
                           r.numerical_value, r.unit, r.methodology_used, r.data_source,
                           r.reporting_status, r.evidence_url, r.notes,
                           i.code as indicator_code, i.title as indicator_title,
                           s.code as standard_code, s.title as standard_title, s.category
                    FROM tsrs_responses r
                    JOIN tsrs_indicators i ON r.indicator_id = i.id
                    JOIN tsrs_standards s ON i.standard_id = s.id
                    WHERE r.company_id = ?
                    ORDER BY r.reporting_period DESC, s.category, s.code, i.code
                """
                return self.execute_query(query, (company_id,), company_id=company_id)

        except Exception as e:
            logging.error(f"TSRS yanıtları getirilirken hata: {e}")
            return []

    def get_tsrs_statistics(self, company_id: int) -> Dict:
        """TSRS istatistiklerini getir"""
        try:
            # Toplam standart sayısı
            total_standards_result = self.execute_query("SELECT COUNT(*) as cnt FROM tsrs_standards", skip_tenant_filter=True)
            total_standards = total_standards_result[0]['cnt'] if total_standards_result else 0

            # Toplam gösterge sayısı
            total_indicators_result = self.execute_query("SELECT COUNT(*) as cnt FROM tsrs_indicators", skip_tenant_filter=True)
            total_indicators = total_indicators_result[0]['cnt'] if total_indicators_result else 0

            # Yanıtlanan göstergeler
            answered_query = """
                SELECT COUNT(DISTINCT indicator_id) as cnt
                FROM tsrs_responses 
                WHERE company_id = ? AND response_value IS NOT NULL
            """
            answered_result = self.execute_query(answered_query, (company_id,), company_id=company_id)
            answered_indicators = answered_result[0]['cnt'] if answered_result else 0

            # Kategori bazlı yanıtlar
            cat_query = """
                SELECT s.category, COUNT(DISTINCT r.indicator_id) as answered_count
                FROM tsrs_responses r
                JOIN tsrs_indicators i ON r.indicator_id = i.id
                JOIN tsrs_standards s ON i.standard_id = s.id
                WHERE r.company_id = ? AND r.response_value IS NOT NULL
                GROUP BY s.category
            """
            cat_results = self.execute_query(cat_query, (company_id,), company_id=company_id)

            category_stats = {}
            for row in cat_results:
                category_stats[row['category']] = row['answered_count']

            # Yanıt yüzdesi
            response_percentage = (answered_indicators / total_indicators * 100) if total_indicators > 0 else 0

            return {
                'total_standards': total_standards,
                'total_indicators': total_indicators,
                'answered_indicators': answered_indicators,
                'response_percentage': round(response_percentage, 1),
                'category_stats': category_stats
            }

        except Exception as e:
            logging.error(f"TSRS istatistikleri getirilirken hata: {e}")
            return {
                'total_standards': 0,
                'total_indicators': 0,
                'answered_indicators': 0,
                'response_percentage': 0,
                'category_stats': {}
            }

    def get_tsrs_gri_mappings(self, tsrs_standard_code: Optional[str] = None) -> List[Dict]:
        """TSRS-GRI eşleştirmelerini getir"""
        try:
            if tsrs_standard_code:
                query = """
                    SELECT tsrs_standard_code, tsrs_indicator_code, 
                           gri_standard, gri_disclosure, relationship_type, notes
                    FROM map_tsrs_gri
                    WHERE tsrs_standard_code = ?
                    ORDER BY gri_standard, gri_disclosure
                """
                return self.execute_query(query, (tsrs_standard_code,), skip_tenant_filter=True)
            else:
                query = """
                    SELECT tsrs_standard_code, tsrs_indicator_code, 
                           gri_standard, gri_disclosure, relationship_type, notes
                    FROM map_tsrs_gri
                    ORDER BY tsrs_standard_code, gri_standard
                """
                return self.execute_query(query, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS-GRI eşleştirmeleri getirilirken hata: {e}")
            return []

    def get_tsrs_sdg_mappings(self, tsrs_standard_code: Optional[str] = None) -> List[Dict]:
        """TSRS-SDG eşleştirmelerini getir"""
        try:
            if tsrs_standard_code:
                query = """
                    SELECT tsrs_standard_code, tsrs_indicator_code, 
                           sdg_goal_id, sdg_target_id, sdg_indicator_code, 
                           relationship_type, notes
                    FROM map_tsrs_sdg
                    WHERE tsrs_standard_code = ?
                    ORDER BY sdg_goal_id, sdg_target_id
                """
                return self.execute_query(query, (tsrs_standard_code,), skip_tenant_filter=True)
            else:
                query = """
                    SELECT tsrs_standard_code, tsrs_indicator_code, 
                           sdg_goal_id, sdg_target_id, sdg_indicator_code, 
                           relationship_type, notes
                    FROM map_tsrs_sdg
                    ORDER BY tsrs_standard_code, sdg_goal_id
                """
                return self.execute_query(query, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS-SDG eşleştirmeleri getirilirken hata: {e}")
            return []

    def create_default_tsrs_data(self, sample: bool = False) -> bool:
        """Varsayılan TSRS verilerini oluştur.
        sample=True ise, eklenen kayıtlar 'TSRS-SAMPLE-' kod ön eki veya '(Sample)' adı ile işaretlenir
        ve ileride silinebilmeleri kolaylaştırılır.
        """
        try:
            # TSRS standartları
            prefix = "TSRS-SAMPLE-" if sample else "TSRS-"
            tsrs_standards = [
                (f"{prefix}001", "Yönetişim Yapısı ve Sorumluluklar",
                 "Şirketin sürdürülebilirlik yönetişim yapısı ve sorumluluklarının açıklanması",
                 "Yönetişim", "Yönetim Kurulu", "Zorunlu", "Yıllık"),

                (f"{prefix}002", "Sürdürülebilirlik Stratejisi ve Hedefler",
                 "Şirketin sürdürülebilirlik stratejisi ve uzun vadeli hedeflerinin açıklanması",
                 "Strateji", "Stratejik Planlama", "Zorunlu", "Yıllık"),

                (f"{prefix}003", "İklim Değişikliği ve Çevresel Riskler",
                 "İklim değişikliği ve çevresel risklerin değerlendirilmesi ve yönetimi",
                 "Risk Yönetimi", "Çevresel Riskler", "Zorunlu", "Yıllık"),

                (f"{prefix}004", "Karbon Emisyonları",
                 "Sera gazı emisyonlarının ölçümü, raporlanması ve azaltım hedefleri",
                 "Metrikler", "Çevresel Performans", "Zorunlu", "Yıllık"),

                (f"{prefix}005", "Enerji Kullanımı ve Verimlilik",
                 "Enerji tüketimi, verimlilik önlemleri ve yenilenebilir enerji kullanımı",
                 "Metrikler", "Çevresel Performans", "Zorunlu", "Yıllık"),

                (f"{prefix}006", "Su Kullanımı ve Su Yönetimi",
                 "Su tüketimi, su verimliliği ve su kaynaklarının korunması",
                 "Metrikler", "Çevresel Performans", "Önerilen", "Yıllık"),

                (f"{prefix}007", "Atık Yönetimi",
                 "Atık üretimi, geri dönüşüm oranları ve atık azaltım hedefleri",
                 "Metrikler", "Çevresel Performans", "Zorunlu", "Yıllık"),

                (f"{prefix}008", "Çalışan Hakları ve İnsan Kaynakları",
                 "Çalışan hakları, iş güvenliği ve insan kaynakları politikaları",
                 "Metrikler", "Sosyal Performans", "Zorunlu", "Yıllık"),

                (f"{prefix}009", "Toplumsal Etki ve Sosyal Sorumluluk",
                 "Toplumsal etki, sosyal sorumluluk projeleri ve paydaş katılımı",
                 "Metrikler", "Sosyal Performans", "Önerilen", "Yıllık"),

                (f"{prefix}010", "Tedarik Zinciri Sürdürülebilirliği",
                 "Tedarik zinciri sürdürülebilirlik politikaları ve tedarikçi değerlendirmesi",
                 "Metrikler", "Sosyal Performans", "İsteğe Bağlı", "Yıllık")
            ]

            for standard in tsrs_standards:
                cursor.execute("""
                    INSERT OR IGNORE INTO tsrs_standards 
                    (code, title, description, category, subcategory, requirement_level, reporting_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, standard)

            # Çevresel göstergeleri tohumla
            try:
                cursor.execute(
                    "SELECT id FROM tsrs_standards "
                    "WHERE code LIKE 'TSRS-%' AND title LIKE '%Karbon Emisyonları%'"
                )
                s_emissions = cursor.fetchone()
                cursor.execute(
                    "SELECT id FROM tsrs_standards "
                    "WHERE code LIKE 'TSRS-%' AND title LIKE '%Enerji Kullanımı%'"
                )
                s_energy = cursor.fetchone()
                cursor.execute(
                    "SELECT id FROM tsrs_standards "
                    "WHERE code LIKE 'TSRS-%' AND title LIKE '%Su Kullanımı%'"
                )
                s_water = cursor.fetchone()
                cursor.execute(
                    "SELECT id FROM tsrs_standards "
                    "WHERE code LIKE 'TSRS-%' AND title LIKE '%Atık Yönetimi%'"
                )
                s_waste = cursor.fetchone()
                indicators = []
                if s_emissions:
                    indicators += [
                        (
                            s_emissions[0],
                            f"{prefix}004-01",
                            "Toplam Karbon Emisyonu (Scope 1+2)",
                            "Kurumsal karbon ayak izi toplamı",
                            "tCO2e",
                            "GHG Protokolü",
                            "numeric",
                            1,
                            1,
                            None,
                            None,
                        ),
                        (
                            s_emissions[0],
                            f"{prefix}004-02",
                            "Karbon Yoğunluğu",
                            "Üretim/Satış başına emisyon yoğunluğu",
                            "tCO2e/ürün",
                            "Yoğunluk hesaplaması",
                            "numeric",
                            0,
                            1,
                            None,
                            None,
                        ),
                    ]
                if s_energy:
                    indicators += [
                        (
                            s_energy[0],
                            f"{prefix}005-01",
                            "Toplam Enerji Tüketimi",
                            "Yıllık toplam enerji kullanımı",
                            "MWh",
                            "Enerji tüketimi ölçümü",
                            "numeric",
                            1,
                            1,
                            None,
                            None,
                        ),
                        (
                            s_energy[0],
                            f"{prefix}005-02",
                            "Yenilenebilir Enerji Oranı",
                            "Toplam tüketimde yenilenebilir oranı",
                            "%",
                            "Oran hesaplaması",
                            "percent",
                            0,
                            1,
                            None,
                            None,
                        ),
                    ]
                if s_water:
                    indicators += [
                        (
                            s_water[0],
                            f"{prefix}006-01",
                            "Toplam Su Tüketimi",
                            "Yıllık toplam su kullanımı",
                            "m³",
                            "Su tüketimi ölçümü",
                            "numeric",
                            0,
                            1,
                            None,
                            None,
                        ),
                        (
                            s_water[0],
                            f"{prefix}006-02",
                            "Su Geri Dönüşüm Oranı",
                            "Kullanılan suyun geri kazanım oranı",
                            "%",
                            "Oran hesaplaması",
                            "percent",
                            0,
                            1,
                            None,
                            None,
                        ),
                    ]
                if s_waste:
                    indicators += [
                        (
                            s_waste[0],
                            f"{prefix}007-01",
                            "Toplam Atık Miktarı",
                            "Yıllık toplam atık",
                            "ton",
                            "Atık ölçümü",
                            "numeric",
                            1,
                            1,
                            None,
                            None,
                        ),
                        (
                            s_waste[0],
                            f"{prefix}007-02",
                            "Atık Geri Dönüşüm Oranı",
                            "Toplam atıkta geri dönüşüm oranı",
                            "%",
                            "Oran hesaplaması",
                            "percent",
                            0,
                            1,
                            None,
                            None,
                        ),
                    ]
                if indicators:
                    self.db.execute_many(
                        """
                        INSERT OR IGNORE INTO tsrs_indicators (
                            standard_id, code, title, description, unit, methodology,
                            data_type, is_mandatory, is_quantitative, baseline_year, target_year
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        indicators
                    )
            except Exception as e:
                logging.error(f"TSRS göstergeleri eklenirken hata: {e}")

            # Paydaş grupları
            stakeholder_groups = [
                ("Çalışanlar" + (" (Sample)" if sample else ""), "Şirket çalışanları ve sendika temsilcileri",
                 "Toplantılar, Anketler", "Yıllık"),
                ("Müşteriler" + (" (Sample)" if sample else ""), "Ana müşteriler ve tüketici grupları",
                 "Müşteri Memnuniyet Anketleri", "Çeyreklik"),
                ("Tedarikçiler" + (" (Sample)" if sample else ""), "Ana tedarikçiler ve iş ortakları",
                 "Tedarikçi Değerlendirme", "Yıllık"),
                ("Yatırımcılar" + (" (Sample)" if sample else ""), "Hisse senedi sahipleri ve finansal kurumlar",
                 "Yatırımcı İlişkileri Toplantıları", "Çeyreklik"),
                ("Yerel Toplum" + (" (Sample)" if sample else ""), "Yerel toplum liderleri ve STK'lar",
                 "Toplumsal Katılım", "Yıllık"),
                ("Regülatörler" + (" (Sample)" if sample else ""), "Kamu kurumları ve düzenleyici otoriteler",
                 "Resmi Toplantılar", "Gerektiğinde")
            ]

            for group in stakeholder_groups:
                self.execute_update("""
                    INSERT OR IGNORE INTO tsrs_stakeholder_groups 
                    (name, description, engagement_method, frequency)
                    VALUES (?, ?, ?, ?)
                """, group, skip_tenant_filter=True)

            logging.info("Varsayılan TSRS verileri başarıyla oluşturuldu" + (" (Sample)" if sample else ""))
            return True

        except Exception as e:
            logging.error(f"Varsayılan TSRS verileri oluşturulurken hata: {e}")
            return False

    def delete_sample_tsrs_data(self) -> bool:
        """Örnek (sample) TSRS verilerini sil.
        'TSRS-SAMPLE-%' kodu ile eklenen standartları ve '(Sample)' adı taşıyan paydaş gruplarını temizler.
        """
        try:
            results = self.execute_query("SELECT id FROM tsrs_standards WHERE code LIKE ?", ("TSRS-SAMPLE-%",), skip_tenant_filter=True)
            sample_standard_ids = [row['id'] for row in results]
            
            if sample_standard_ids:
                placeholders = ','.join(['?'] * len(sample_standard_ids))
                self.execute_update(
                    (
                        "DELETE FROM tsrs_responses WHERE indicator_id IN ("
                        "SELECT id FROM tsrs_indicators WHERE standard_id IN (" + placeholders + "))"
                    ),
                    tuple(sample_standard_ids),
                    skip_tenant_filter=True 
                )
                self.execute_update(
                    "DELETE FROM tsrs_indicators WHERE standard_id IN (" + placeholders + ")",
                    tuple(sample_standard_ids),
                    skip_tenant_filter=True
                )
            # Standartlar (TSRS-SAMPLE-%)
            self.execute_update("DELETE FROM tsrs_standards WHERE code LIKE ?", ("TSRS-SAMPLE-%",), skip_tenant_filter=True)

            # Paydaş grupları
            self.execute_update("DELETE FROM tsrs_stakeholder_groups WHERE name LIKE ?", ("%(Sample)%",), skip_tenant_filter=True)

            logging.info("Örnek TSRS verileri silindi")
            return True
        except Exception as e:
            logging.error(f"Örnek TSRS verileri silinirken hata: {e}")
            return False

    def purge_company_tsrs_data(
        self,
        company_id: int,
        delete_exports: bool = True,
        exports_dir: Optional[str] = None,
    ) -> bool:
        try:
            tables = [
                "tsrs_responses",
                "tsrs_targets",
                "tsrs_risks",
                "tsrs_performance_data",
                "tsrs_stakeholder_engagement",
                "tsrs_reports",
            ]
            for t in tables:
                self.delete(t, company_id=company_id)

            if delete_exports:
                if exports_dir is None:
                    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    exports_dir = os.path.join(repo_root, 'data', 'exports')
                try:
                    if os.path.isdir(exports_dir):
                        for name in os.listdir(exports_dir):
                            if name.startswith('TSRS_Raporu_'):
                                try:
                                    os.remove(os.path.join(exports_dir, name))
                                except Exception as e:
                                    logging.error(f"Silent error caught: {str(e)}")
                except Exception as e:
                    logging.error(f"Silent error caught: {str(e)}")

            logging.info(f"Şirket {company_id} için TSRS verileri temizlendi")
            return True
        except Exception as e:
            logging.error(f"TSRS şirket verileri temizlenirken hata: {e}")
            return False

    def get_tsrs_report_templates(self) -> List[Dict]:
        """TSRS rapor şablonlarını getir"""
        try:
            query = """
                SELECT id, name, description, template_type, sectors, 
                       mandatory_standards, optional_standards, is_active
                FROM tsrs_report_templates
                WHERE is_active = 1
                ORDER BY name
            """
            return self.execute_query(query, skip_tenant_filter=True)

        except Exception as e:
            logging.error(f"TSRS rapor şablonları getirilirken hata: {e}")
            return []

    def create_tsrs_report(self, company_id: int, template_id: int,
                          reporting_period: str, report_data: Dict) -> Optional[int]:
        """TSRS raporu oluştur"""
        try:
            data = {
                'template_id': template_id,
                'reporting_period': reporting_period,
                'report_title': report_data.get('report_title', f'TSRS Raporu {reporting_period}'),
                'report_status': report_data.get('report_status', 'Draft'),
                'cover_period_start': report_data.get('cover_period_start'),
                'cover_period_end': report_data.get('cover_period_end'),
                'assurance_type': report_data.get('assurance_type'),
                'assurance_provider': report_data.get('assurance_provider'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            return self.insert("tsrs_reports", data, company_id=company_id)

        except Exception as e:
            logging.error(f"TSRS raporu oluşturulurken hata: {e}")
            return -1
