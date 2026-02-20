#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Manager - Backend İş Mantığı
- Sektör yönetimi
- Metrik yönetimi
- SASB-GRI mapping
- Veri import/export
"""

import logging
import json
import os
import sys
from typing import Dict, List, Optional

# Add project root to path if needed
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if base_dir not in sys.path:
    sys.path.append(base_dir)

try:
    from backend.config.database import DB_PATH
    from backend.core.base_manager import BaseTenantManager
except ImportError as e:
    import logging
    logging.error(f"Failed to import from backend: {e}")
    # Fallback removed for debugging/enforcement
    raise e


class SASBManager(BaseTenantManager):
    """SASB Modülü Backend Manager"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        """Init"""
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.module_dir = os.path.dirname(os.path.abspath(__file__))
        # Default context 1 used for global operations; specific methods accept company_id
        super().__init__(db_path, company_id)

        # Veritabanı başlat
        self.init_database()

        # Veri yükle
        self.load_sector_data()

    def init_database(self) -> None:
        """SASB tablolarını oluştur"""
        schema_path = os.path.join(self.module_dir, 'sasb_schema.sql')

        if not os.path.exists(schema_path):
            logging.info("️ SASB schema bulunamadı!")
            return

        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()

            # Use DatabaseManager's connection for script execution
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema)
                conn.commit()
            
            logging.info("[OK] SASB tablolari olusturuldu")
        except Exception as e:
            logging.error(f"[HATA] Tablo olusturma hatasi: {e}")

    def load_sector_data(self) -> bool:
        """Sektör verilerini JSON'dan yükle (Yeni yapı - Data dizini)"""
        try:
            data_dir = os.path.join(self.module_dir, 'data')
            
            # 1. Sektörleri Yükle (sasb_sectors.json)
            sectors_file = os.path.join(data_dir, 'sasb_sectors.json')
            if os.path.exists(sectors_file):
                with open(sectors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sector in data.get('sasb_sectors', []):
                        self.execute_update("""
                            INSERT OR IGNORE INTO sasb_sectors 
                            (sector_code, sector_name, industry_group, description)
                            VALUES (?, ?, ?, ?)
                        """, (sector['sector_code'], sector['sector_name'], 
                              sector['industry_group'], sector.get('sector_description', '')), company_id=1)
            
            # GLOBAL Sektör (IFRS S1/S2 gibi genel standartlar için)
            res = self.execute_query("SELECT id FROM sasb_sectors WHERE sector_code = 'GLOBAL'", company_id=1)
            if not res:
                self.execute_update("""
                    INSERT INTO sasb_sectors (sector_code, sector_name, industry_group, description) 
                    VALUES ('GLOBAL', 'Global Standards', 'General', 'Cross-industry standards like IFRS S1/S2')
                """, company_id=1)
            
            # 2. Topics Yükle (sasb_disclosure_topics.json)
            topics_file = os.path.join(data_dir, 'sasb_disclosure_topics.json')
            if os.path.exists(topics_file):
                with open(topics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for topic in data.get('sasb_disclosure_topics', []):
                        sector_code = topic.get('sector_code')
                        
                        # Sector ID bul
                        if sector_code == 'ALL':
                            res = self.execute_query("SELECT id FROM sasb_sectors WHERE sector_code = 'GLOBAL'", company_id=1)
                        else:
                            res = self.execute_query("SELECT id FROM sasb_sectors WHERE sector_code = ?", (sector_code,), company_id=1)
                        
                        if res:
                            sector_id = res[0]['id']
                            
                            # Check existence
                            check = self.execute_query("SELECT id FROM sasb_disclosure_topics WHERE sector_id = ? AND topic_code = ?", (sector_id, topic['topic_code']), company_id=1)
                            if not check:
                                self.execute_update("""
                                    INSERT INTO sasb_disclosure_topics 
                                    (sector_id, topic_code, topic_name, category, is_material, description)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (sector_id, topic['topic_code'], topic['topic_name'],
                                     topic['topic_category'], topic['is_financial_material'], topic.get('topic_description', '')), company_id=1)

            # 3. Metrics Yükle (sasb_metrics.json)
            metrics_file = os.path.join(data_dir, 'sasb_metrics.json')
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for metric in data.get('sasb_metrics', []):
                         # Topic ID bul (Code ile)
                         topics = self.execute_query("SELECT id FROM sasb_disclosure_topics WHERE topic_code = ?", (metric['topic_code'],), company_id=1)
                         
                         for topic_row in topics:
                             topic_id = topic_row['id']
                             
                             # Check existence
                             check = self.execute_query("SELECT id FROM sasb_metrics WHERE disclosure_topic_id = ? AND metric_code = ?", (topic_id, metric['metric_code']), company_id=1)
                             if not check:
                                 self.execute_update("""
                                    INSERT INTO sasb_metrics
                                    (disclosure_topic_id, metric_code, metric_name, metric_type, unit, reporting_guidance)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (topic_id, metric['metric_code'], metric['metric_name'],
                                     metric['metric_type'], metric.get('unit_of_measure', ''), metric.get('calculation_method', '')), company_id=1)

            # 4. GRI Mapping (sasb_gri_mapping.json)
            mapping_file = os.path.join(data_dir, 'sasb_gri_mapping.json')
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    mappings_list = data.get('sasb_gri_mapping', data.get('sasb_gri_mappings', []))
                    for mapping in mappings_list:
                        # Key uyumlulugu
                        sasb_code = mapping.get('sasb_metric_code', mapping.get('sasb_code'))
                        gri_ind = mapping.get('gri_indicator', mapping.get('gri_disclosure'))
                        notes = mapping.get('mapping_notes', mapping.get('notes', ''))
                        
                        # Check existence
                        check = self.execute_query("SELECT id FROM sasb_gri_mapping WHERE sasb_metric_code = ? AND gri_disclosure = ?", (sasb_code, gri_ind), company_id=1)
                        if not check:
                            self.execute_update("""
                                INSERT INTO sasb_gri_mapping 
                                (sasb_metric_code, gri_standard, gri_disclosure, mapping_strength, notes)
                                VALUES (?, ?, ?, ?, ?)
                            """, (sasb_code, mapping['gri_standard'], gri_ind, 
                                  mapping['mapping_strength'], notes), company_id=1)

            logging.info("[OK] SASB verileri yeni JSON yapisindan yuklendi (Data folder)")
            return True

        except Exception as e:
            logging.error(f"[HATA] SASB veri yukleme hatasi: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _import_sectors(self, cursor, sectors: List[Dict]) -> None:
        """Eski import metodu - Artik kullanilmiyor ama referans icin tutulabilir"""
        pass

    def get_all_sectors(self) -> List[Dict]:
        """Tüm sektörleri getir"""
        try:
            rows = self.execute_query("""
                SELECT id, sector_code, sector_name, industry_group, description
                FROM sasb_sectors
                ORDER BY industry_group, sector_name
            """, company_id=1)

            sectors = []
            for row in rows:
                sectors.append({
                    'id': row['id'],
                    'sector_code': row['sector_code'],
                    'sector_name': row['sector_name'],
                    'industry_group': row['industry_group'],
                    'description': row['description']
                })

            return sectors
        except Exception as e:
            logging.error(f"[HATA] Sektor getirme hatasi: {e}")
            return []

    def get_sector_topics(self, sector_id: int) -> List[Dict]:
        """Sektör disclosure topics"""
        try:
            rows = self.execute_query("""
                SELECT id, topic_code, topic_name, category, description
                FROM sasb_disclosure_topics
                WHERE sector_id = ? AND is_material = 1
                ORDER BY category, topic_name
            """, (sector_id,), company_id=1)

            topics = []
            for row in rows:
                topics.append({
                    'id': row['id'],
                    'topic_code': row['topic_code'],
                    'topic_name': row['topic_name'],
                    'category': row['category'],
                    'description': row['description']
                })

            return topics
        except Exception as e:
            logging.error(f"[HATA] Topic getirme hatasi: {e}")
            return []

    def get_topic_metrics(self, topic_id: int) -> List[Dict]:
        """Topic metrikleri"""
        try:
            rows = self.execute_query("""
                SELECT id, metric_code, metric_name, metric_type, unit, reporting_guidance
                FROM sasb_metrics
                WHERE disclosure_topic_id = ?
                ORDER BY metric_code
            """, (topic_id,), company_id=1)

            metrics = []
            for row in rows:
                metrics.append({
                    'id': row['id'],
                    'metric_code': row['metric_code'],
                    'metric_name': row['metric_name'],
                    'metric_type': row['metric_type'],
                    'unit': row['unit'],
                    'reporting_guidance': row['reporting_guidance']
                })

            return metrics
        except Exception as e:
            logging.error(f"[HATA] Metrik getirme hatasi: {e}")
            return []

    def select_company_sector(self, company_id: int, year: int, sector_id: int) -> bool:
        """Şirket sektörü seç"""
        try:
            # Note: company_sasb_data is tenant-specific, so we pass company_id
            self.execute_update("""
                INSERT OR REPLACE INTO company_sasb_data (company_id, year, sector_id)
                VALUES (?, ?, ?)
            """, (company_id, year, sector_id), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"[HATA] Sektor secim hatasi: {e}")
            return False

    def save_metric_response(self, company_id: int, year: int, metric_id: int,
                            response_value: str, numerical_value: Optional[float] = None,
                            unit: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Metrik yanıtı kaydet"""
        try:
            # Tenant specific
            self.execute_update("""
                INSERT OR REPLACE INTO sasb_metric_responses
                (company_id, year, metric_id, response_value, numerical_value, unit, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, year, metric_id, response_value, numerical_value, unit, notes), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"[HATA] Yanit kaydetme hatasi: {e}")
            return False

    def get_sasb_gri_mappings(self) -> List[Dict]:
        """SASB-GRI mapping listesi"""
        try:
            rows = self.execute_query("""
                SELECT sasb_metric_code, gri_standard, gri_disclosure, 
                       mapping_strength, notes
                FROM sasb_gri_mapping
                ORDER BY sasb_metric_code
            """, company_id=1)

            mappings = []
            for row in rows:
                mappings.append({
                    'sasb_code': row['sasb_metric_code'],
                    'gri_standard': row['gri_standard'],
                    'gri_disclosure': row['gri_disclosure'],
                    'strength': row['mapping_strength'],
                    'notes': row['notes']
                })

            return mappings
        except Exception as e:
            logging.error(f"[HATA] Mapping getirme hatasi: {e}")
            return []

    def get_metric_responses(self, company_id: int, year: int) -> Dict:
        """Şirketin belirli bir yıldaki metrik yanıtlarını getir"""
        try:
            rows = self.execute_query("""
                SELECT metric_id, response_value, numerical_value, unit, notes
                FROM sasb_metric_responses
                WHERE company_id = ? AND year = ?
            """, (company_id, year), company_id=company_id)

            responses = {}
            for row in rows:
                responses[row['metric_id']] = {
                    'response_value': row['response_value'],
                    'numerical_value': row['numerical_value'],
                    'unit': row['unit'],
                    'notes': row['notes']
                }
            return responses
        except Exception as e:
            logging.error(f"[HATA] Yanit getirme hatasi: {e}")
            return {}

    def get_company_sector(self, company_id: int, year: int) -> Optional[Dict]:
        """Şirketin seçili sektörünü getir"""
        try:
            rows = self.execute_query("""
                SELECT s.id, s.sector_code, s.sector_name, s.industry_group
                FROM company_sasb_data csd
                JOIN sasb_sectors s ON csd.sector_id = s.id
                WHERE csd.company_id = ? AND csd.year = ?
            """, (company_id, year), company_id=company_id)

            if rows:
                row = rows[0]
                return {
                    'id': row['id'],
                    'sector_code': row['sector_code'],
                    'sector_name': row['sector_name'],
                    'industry_group': row['industry_group']
                }
            return None
        except Exception as e:
            logging.error(f"[HATA] Sirket sektoru getirme hatasi: {e}")
            return None

    def get_company_disclosures(self, company_id: int, year: int) -> List[Dict]:
        """Rapor için detaylı disclosure verilerini getir"""
        try:
            rows = self.execute_query("""
                SELECT 
                    dt.topic_code, dt.topic_name,
                    m.metric_code, m.metric_name, m.unit,
                    r.response_value, r.notes
                FROM sasb_metric_responses r
                JOIN sasb_metrics m ON r.metric_id = m.id
                JOIN sasb_disclosure_topics dt ON m.disclosure_topic_id = dt.id
                WHERE r.company_id = ? AND r.year = ?
                ORDER BY dt.topic_code, m.metric_code
            """, (company_id, year), company_id=company_id)

            disclosures = []
            for row in rows:
                disclosures.append({
                    'topic_code': row['topic_code'],
                    'topic_name': row['topic_name'],
                    'metric_code': row['metric_code'],
                    'metric_name': row['metric_name'],
                    'unit_of_measure': row['unit'],
                    'metric_value': row['response_value'],
                    'notes': row['notes'],
                    'data_source': 'Manual Entry'
                })
            return disclosures
        except Exception as e:
            logging.error(f"[HATA] Disclosure getirme hatasi: {e}")
            return []

    def get_completion_status(self, company_id: int, year: int) -> Dict:
        """Tamamlanma durumu"""
        try:
            # Not: BaseTenantManager otomatik olarak sorgulara company_id filtresi ekler
            # Ancak burada complex joinler var. 
            # inject_tenant_filter "company_sasb_data" tablosunu görüp oraya company_id eklemeye calisabilir
            # veya zaten WHERE clause var.
            # BaseTenantManager logic: "If company_id in sql, skip".
            # Sorgumuzda "WHERE csd.company_id = ?" var, yani "company_id" stringi var.
            # Bu yuzden inject_tenant_filter atlayacaktir (ki bu dogru, cunku biz zaten manuel ekledik).
            
            rows = self.execute_query("""
                SELECT s.sector_name, COUNT(DISTINCT m.id) as total_metrics,
                       COUNT(DISTINCT r.metric_id) as completed_metrics
                FROM company_sasb_data csd
                JOIN sasb_sectors s ON csd.sector_id = s.id
                LEFT JOIN sasb_disclosure_topics dt ON dt.sector_id = s.id
                LEFT JOIN sasb_metrics m ON m.disclosure_topic_id = dt.id
                LEFT JOIN sasb_metric_responses r ON r.metric_id = m.id 
                    AND r.company_id = csd.company_id AND r.year = csd.year
                WHERE csd.company_id = ? AND csd.year = ?
                GROUP BY s.sector_name
            """, (company_id, year), company_id=company_id)

            if rows:
                row = rows[0]
                total = row['total_metrics'] or 0
                completed = row['completed_metrics'] or 0
                percentage = (completed / total * 100) if total > 0 else 0

                return {
                    'sector': row['sector_name'],
                    'total_metrics': total,
                    'completed_metrics': completed,
                    'completion_percentage': round(percentage, 1)
                }

            return {'total_metrics': 0, 'completed_metrics': 0, 'completion_percentage': 0}
        except Exception as e:
            logging.error(f"[HATA] Tamamlanma durumu hatasi: {e}")
            return {'total_metrics': 0, 'completed_metrics': 0, 'completion_percentage': 0}


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    logging.info(" SASB Manager Test...")

    manager = SASBManager()

    # Sektörleri listele
    sectors = manager.get_all_sectors()
    logging.info(f"[OK] {len(sectors)} sektor yuklendi")

    # İlk 5 sektörü göster
    for i, sector in enumerate(sectors[:5], 1):
        logging.info(f"{i}. {sector['sector_code']} - {sector['sector_name']}")

    # GRI Mapping
    mappings = manager.get_sasb_gri_mappings()
    logging.info(f"[OK] {len(mappings)} SASB-GRI mapping")

    logging.info("[OK] Test tamamlandi!")
