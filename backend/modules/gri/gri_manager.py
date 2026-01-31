import logging
import sqlite3
from datetime import datetime
from typing import Dict, List

from config.settings import ensure_directories, get_db_path


class GRIManager:
    """GRI (Global Reporting Initiative) modülü yöneticisi"""

    def __init__(self, db_path: str | None = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            ensure_directories()
            self.db_path = get_db_path()
        self.company_id = 1  # Varsayılan company_id

        # Tabloları oluştur ve veri doldur
        self.create_gri_tables()
        self.populate_gri_standards()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        stats = {
            'selected_goals': 0,
            'indicators': 0,
            'disclosures': 0
        }
        
        try:
            # Seçilen SDG hedefleri
            cursor.execute("SELECT COUNT(*) FROM user_sdg_selections WHERE company_id = ?", (company_id,))
            row = cursor.fetchone()
            if row:
                stats['selected_goals'] = row[0]
                
            # Haritalanmış GRI göstergeleri (tahmini)
            selected_ids = self.get_selected_sdg_goals(company_id)
            indicators = self.get_sdg_indicators_for_goals(selected_ids)
            stats['indicators'] = len(indicators)
            
            gri_mappings = self.get_gri_indicators_for_sdg_selection(company_id)
            stats['disclosures'] = len(gri_mappings)
                
        except Exception as e:
            logging.error(f"GRI stats error: {e}")
        finally:
            conn.close()
            
        return stats

    def get_selected_sdg_goals(self, company_id: int) -> List[int]:
        """Şirket için seçilen SDG hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # user_sdg_selections tablosundan seçilen hedefleri al
            cursor.execute("""
                SELECT goal_id 
                FROM user_sdg_selections 
                WHERE company_id = ?
                ORDER BY goal_id
            """, (company_id,))

            selected_ids = [row[0] for row in cursor.fetchall()]
            return selected_ids

        except Exception as e:
            logging.error(f"Seçilen SDG hedefleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()


    def get_sdg_indicators_for_goals(self, goal_ids: List[int]) -> List[str]:
        """Seçilen SDG hedefleri için gösterge kodlarını getir"""
        if not goal_ids:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            placeholders = ','.join('?' * len(goal_ids))
            cursor.execute(f"""
                SELECT DISTINCT si.code 
                FROM sdg_indicators si
                JOIN sdg_targets st ON si.target_id = st.id
                WHERE st.goal_id IN ({placeholders})
            """, goal_ids)

            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"SDG gösterge kodları getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_gri_indicators_for_sdg_selection(self, company_id: int) -> List[Dict]:
        """SDG seçimlerine göre ilgili GRI göstergelerini getir"""
        # Seçilen SDG hedeflerini al
        selected_goals = self.get_selected_sdg_goals(company_id)
        if not selected_goals:
            return []

        # SDG gösterge kodlarını al
        sdg_indicator_codes = self.get_sdg_indicators_for_goals(selected_goals)
        if not sdg_indicator_codes:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # SDG-GRI eşleştirmelerini al
            placeholders = ','.join('?' * len(sdg_indicator_codes))
            cursor.execute(f"""
                SELECT DISTINCT mg.gri_standard, mg.gri_disclosure
                FROM map_sdg_gri mg
                WHERE mg.sdg_indicator_code IN ({placeholders})
            """, sdg_indicator_codes)

            gri_mappings = cursor.fetchall()
            if not gri_mappings:
                return []

            # GRI göstergelerini al
            gri_disclosures = [mapping[1] for mapping in gri_mappings if mapping[1].strip()]
            gri_standards = [mapping[0] for mapping in gri_mappings]

            # Eğer disclosure kodları yoksa, standart kodlarına göre ara
            if not gri_disclosures:
                standard_placeholders = ','.join('?' * len(set(gri_standards)))
                cursor.execute(f"""
                    SELECT gi.id, gi.code, gi.title, gi.description, gi.unit, gi.methodology, 
                           gi.reporting_requirement, gs.code as standard_code, gs.title as standard_title,
                           gs.category
                    FROM gri_indicators gi
                    JOIN gri_standards gs ON gi.standard_id = gs.id
                    WHERE gs.code IN ({standard_placeholders})
                    ORDER BY gs.category, gs.code, gi.code
                """, list(set(gri_standards)))
            else:
                gri_placeholders = ','.join('?' * len(gri_disclosures))
                cursor.execute(f"""
                    SELECT gi.id, gi.code, gi.title, gi.description, gi.unit, gi.methodology, 
                           gi.reporting_requirement, gs.code as standard_code, gs.title as standard_title,
                           gs.category
                    FROM gri_indicators gi
                    JOIN gri_standards gs ON gi.standard_id = gs.id
                    WHERE gi.code IN ({gri_placeholders})
                    ORDER BY gs.category, gs.code, gi.code
                """, gri_disclosures)

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                result = dict(zip(columns, row))

                # Bu GRI göstergesine eşleşen SDG gösterge kodlarını bul
                cursor.execute("""
                    SELECT sdg_indicator_code FROM map_sdg_gri 
                    WHERE gri_disclosure = ?
                """, (result['code'],))

                result['mapped_sdg_indicators'] = [row[0] for row in cursor.fetchall()]

                # TSRS eşleştirmelerini bul
                cursor.execute("""
                    SELECT tsrs_section, tsrs_metric FROM map_gri_tsrs 
                    WHERE gri_disclosure = ?
                """, (result['code'],))

                result['mapped_tsrs'] = [{'section': row[0], 'metric': row[1]} for row in cursor.fetchall()]

                results.append(result)

            return results

        except Exception as e:
            logging.error(f"GRI göstergeleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def get_gri_standards_for_sdg_selection(self, company_id: int) -> Dict[str, List[Dict]]:
        """SDG seçimlerine göre GRI standartlarını kategorilere göre grupla"""
        gri_indicators = self.get_gri_indicators_for_sdg_selection(company_id)

        # Kategorilere göre grupla
        standards_by_category = {}

        for indicator in gri_indicators:
            category = indicator['category']
            if category not in standards_by_category:
                standards_by_category[category] = {}

            standard_code = indicator['standard_code']
            if standard_code not in standards_by_category[category]:
                standards_by_category[category][standard_code] = {
                    'code': standard_code,
                    'title': indicator['standard_title'],
                    'category': category,
                    'indicators': []
                }

            standards_by_category[category][standard_code]['indicators'].append(indicator)

        # Dict'i list'e çevir
        result = {}
        for category, standards in standards_by_category.items():
            result[category] = list(standards.values())

        return result

    def get_standards_by_category(self, category: str) -> List[Dict]:
        """Kategoriye göre standartları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if category == "universal":
                cursor.execute("""
                    SELECT code, title, description, 
                           type, category, created_at
                    FROM gri_standards 
                    WHERE type = 'Universal'
                    ORDER BY code
                """)
            else:
                cursor.execute("""
                    SELECT code, title, description, 
                           type, category, created_at
                    FROM gri_standards 
                    WHERE category = ?
                    ORDER BY code
                """, (category.title(),))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            # Standartları ve göstergeleri birleştir
            formatted_data = {
                'standards': results,
                'indicators': []
            }

            # Her standart için göstergeleri al
            for standard in results:
                indicators = self.get_indicators_by_standard(standard['code'])
                formatted_data['indicators'].extend(indicators)

            return formatted_data

        except Exception as e:
            logging.error(f"GRI standartları getirilirken hata: {e}")
            return {'standards': [], 'indicators': []}
        finally:
            conn.close()

    def get_indicators_by_standard(self, standard_code) -> None:
        """Standart koduna göre göstergeleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT gi.code, gi.title, gi.description, gi.unit, gi.methodology, 
                       gi.reporting_requirement, gi.priority, gi.requirement_level,
                       gi.data_quality, gi.audit_required, gi.validation_required,
                       gi.digitalization_status, gi.cost_level, gi.time_requirement,
                       gi.expertise_requirement, gi.sustainability_impact,
                       gi.legal_compliance, gi.sector_specific, gi.international_standard,
                       gi.metric_type, gi.scale_unit, gi.data_source_system,
                       gi.reporting_format, gi.tsrs_esrs_mapping, gi.un_sdg_mapping,
                       gi.gri_3_3_reference, gi.impact_area, gi.stakeholder_group,
                       gs.code as standard_code, gs.title as standard_title
                FROM gri_indicators gi
                JOIN gri_standards gs ON gi.standard_id = gs.id
                WHERE gs.code = ?
                ORDER BY gi.code
            """, (standard_code,))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                indicator = dict(zip(columns, row))
                # Gösterge kodunu indicator_code olarak da ekle
                indicator['indicator_code'] = indicator['code']
                indicator['indicator_title'] = indicator['title']
                results.append(indicator)

            return results

        except Exception as e:
            logging.error(f"GRI göstergeleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def create_gri_tables(self) -> None:
        """GRI tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # GRI Standartları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_standards (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    sector TEXT DEFAULT 'General'
                )
            """)

            # Check if sector column exists (migration for existing dbs)
            try:
                cursor.execute("SELECT sector FROM gri_standards LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE gri_standards ADD COLUMN sector TEXT DEFAULT 'General'")

            # GRI Göstergeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_indicators (
                    id INTEGER PRIMARY KEY,
                    standard_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    unit TEXT,
                    methodology TEXT,
                    reporting_requirement TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
                )
            """)

            # GRI Cevapları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_responses (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    indicator_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    response_value TEXT,
                    numerical_value REAL,
                    unit TEXT,
                    methodology TEXT,
                    reporting_status TEXT DEFAULT 'Draft',
                    evidence_url TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # GRI Seçimleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_selections (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    indicator_id INTEGER NOT NULL,
                    selected INTEGER DEFAULT 0,
                    priority_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            conn.commit()
            logging.info("GRI tablolari basariyla olusturuldu")
            return True

        except Exception as e:
            logging.error(f"GRI tablolari olusturma hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def insert_gri_standards(self) -> None:
        """GRI standartlarını ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # GRI Universal Standards (2021)
            universal_standards = [
                ("GRI 1", "Foundation", "Universal", "Temel bilgiler ve raporlama ilkeleri", "General"),
                ("GRI 2", "General Disclosures", "Universal", "Genel açıklamalar ve organizasyonel bilgiler", "General"),
                ("GRI 3", "Material Topics", "Universal", "Materyal konular ve önceliklendirme", "General")
            ]

            # GRI Topic Standards - Economic
            economic_standards = [
                ("GRI 201", "Economic Performance", "Economic", "Ekonomik performans göstergeleri", "General"),
                ("GRI 202", "Market Presence", "Economic", "Pazar varlığı ve rekabet", "General"),
                ("GRI 203", "Indirect Economic Impacts", "Economic", "Dolaylı ekonomik etkiler", "General"),
                ("GRI 204", "Procurement Practices", "Economic", "Tedarik uygulamaları", "General"),
                ("GRI 205", "Anti-corruption", "Economic", "Yolsuzlukla mücadele", "General"),
                ("GRI 206", "Anti-competitive Behavior", "Economic", "Rekabet karşıtı davranışlar", "General"),
                ("GRI 207", "Tax", "Economic", "Vergi uygulamaları", "General")
            ]

            # GRI Topic Standards - Environmental
            environmental_standards = [
                ("GRI 301", "Materials", "Environmental", "Malzeme kullanımı ve verimlilik", "General"),
                ("GRI 302", "Energy", "Environmental", "Enerji tüketimi ve verimlilik", "General"),
                ("GRI 303", "Water and Effluents", "Environmental", "Su kullanımı ve atık sular", "General"),
                ("GRI 304", "Biodiversity", "Environmental", "Biyoçeşitlilik ve ekosistemler", "General"),
                ("GRI 305", "Emissions", "Environmental", "Emisyonlar ve hava kalitesi", "General"),
                ("GRI 306", "Waste", "Environmental", "Atık yönetimi", "General"),
                ("GRI 307", "Environmental Compliance", "Environmental", "Çevresel uyumluluk", "General"),
                ("GRI 308", "Supplier Environmental Assessment", "Environmental", "Tedarikçi çevresel değerlendirmesi", "General")
            ]

            # GRI Topic Standards - Social
            social_standards = [
                ("GRI 401", "Employment", "Social", "İstihdam ve çalışan hakları", "General"),
                ("GRI 402", "Labor/Management Relations", "Social", "İşçi-yönetim ilişkileri", "General"),
                ("GRI 403", "Occupational Health and Safety", "Social", "İş sağlığı ve güvenliği", "General"),
                ("GRI 404", "Training and Education", "Social", "Eğitim ve gelişim", "General"),
                ("GRI 405", "Diversity and Equal Opportunity", "Social", "Çeşitlilik ve fırsat eşitliği", "General"),
                ("GRI 406", "Non-discrimination", "Social", "Ayrımcılık yasağı", "General"),
                ("GRI 407", "Freedom of Association", "Social", "Örgütlenme özgürlüğü", "General"),
                ("GRI 408", "Child Labor", "Social", "Çocuk işçiliği", "General"),
                ("GRI 409", "Forced or Compulsory Labor", "Social", "Zorla çalıştırma", "General"),
                ("GRI 410", "Security Practices", "Social", "Güvenlik uygulamaları", "General"),
                ("GRI 411", "Rights of Indigenous Peoples", "Social", "Yerli halk hakları", "General"),
                ("GRI 412", "Human Rights Assessment", "Social", "İnsan hakları değerlendirmesi", "General"),
                ("GRI 413", "Local Communities", "Social", "Yerel topluluklar", "General"),
                ("GRI 414", "Supplier Social Assessment", "Social", "Tedarikçi sosyal değerlendirmesi", "General"),
                ("GRI 415", "Public Policy", "Social", "Kamu politikaları", "General"),
                ("GRI 416", "Customer Health and Safety", "Social", "Müşteri sağlığı ve güvenliği", "General"),
                ("GRI 417", "Marketing and Labeling", "Social", "Pazarlama ve etiketleme", "General"),
                ("GRI 418", "Customer Privacy", "Social", "Müşteri gizliliği", "General"),
                ("GRI 419", "Socioeconomic Compliance", "Social", "Sosyoekonomik uyumluluk", "General")
            ]
            
            # GRI Sector Standards (2024-2026 Updates)
            sector_standards = [
                ("GRI 11", "Oil and Gas Sector 2021", "Sector", "Petrol ve Gaz Sektörü Standartları", "Oil & Gas"),
                ("GRI 12", "Coal Sector 2022", "Sector", "Kömür Sektörü Standartları", "Coal"),
                ("GRI 13", "Agriculture, Aquaculture and Fishing Sectors 2022", "Sector", "Tarım, Su Ürünleri ve Balıkçılık", "Agriculture"),
                ("GRI 14", "Mining Sector 2024", "Sector", "Madencilik Sektörü Standartları", "Mining"),
                ("GRI 101", "Biodiversity 2024", "Environmental", "Biyoçeşitlilik (2024 Güncellemesi)", "General"),
                ("GRI 103", "Energy 2025", "Environmental", "Enerji (2025 Güncellemesi)", "General")
            ]

            all_standards = universal_standards + economic_standards + environmental_standards + social_standards + sector_standards

            for code, title, category, description, sector in all_standards:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_standards (code, title, category, description, sector)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, title, category, description, sector))

            conn.commit()
            logging.info(f"{len(all_standards)} GRI standardi eklendi/guncellendi")
            return True

        except Exception as e:
            logging.error(f"GRI standartlari ekleme hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def insert_gri_indicators(self) -> None:
        """GRI göstergelerini ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # GRI 2 - General Disclosures göstergeleri
            cursor.execute("SELECT id FROM gri_standards WHERE code = 'GRI 2'")
            gri2_id = cursor.fetchone()[0]

            gri2_indicators = [
                ("2-1", "Organizational details", "Organizasyonel detaylar", "Text", "Genel", "Zorunlu"),
                ("2-2", "Entities included in sustainability reporting", "Sürdürülebilirlik raporlamasına dahil kuruluşlar", "Text", "Genel", "Zorunlu"),
                ("2-3", "Reporting period, frequency and contact point", "Raporlama dönemi, sıklığı ve iletişim noktası", "Text", "Genel", "Zorunlu"),
                ("2-4", "Restatements of information", "Bilgi yeniden beyanları", "Text", "Genel", "Zorunlu"),
                ("2-5", "External assurance", "Harici güvence", "Text", "Genel", "Zorunlu"),
                ("2-6", "Activities, value chain and business relationships", "Faaliyetler, değer zinciri ve iş ilişkileri", "Text", "Genel", "Zorunlu"),
                ("2-7", "Employees", "Çalışanlar", "Number", "Kişi", "Zorunlu"),
                ("2-8", "Workers who are not employees", "Çalışan olmayan işçiler", "Number", "Kişi", "Zorunlu"),
                ("2-9", "Governance structure and composition", "Yönetişim yapısı ve bileşimi", "Text", "Genel", "Zorunlu"),
                ("2-10", "Nomination and selection of the highest governance body", "En yüksek yönetişim organının aday gösterilmesi ve seçimi", "Text", "Genel", "Zorunlu"),
                ("2-11", "Chair of the highest governance body", "En yüksek yönetişim organının başkanı", "Text", "Genel", "Zorunlu"),
                ("2-12", "Role of the highest governance body in sustainability topics", "Sürdürülebilirlik konularında en yüksek yönetişim organının rolü", "Text", "Genel", "Zorunlu"),
                ("2-13", "Delegation of responsibility for sustainability topics", "Sürdürülebilirlik konularından sorumluluğun devredilmesi", "Text", "Genel", "Zorunlu"),
                ("2-14", "Role of the highest governance body in sustainability reporting", "Sürdürülebilirlik raporlamasında en yüksek yönetişim organının rolü", "Text", "Genel", "Zorunlu"),
                ("2-15", "Conflicts of interest", "Çıkar çatışmaları", "Text", "Genel", "Zorunlu"),
                ("2-16", "Communication of critical concerns", "Kritik endişelerin iletişimi", "Text", "Genel", "Zorunlu"),
                ("2-17", "Collective knowledge of the highest governance body", "En yüksek yönetişim organının toplu bilgisi", "Text", "Genel", "Zorunlu"),
                ("2-18", "Evaluation of the performance of the highest governance body", "En yüksek yönetişim organının performansının değerlendirilmesi", "Text", "Genel", "Zorunlu"),
                ("2-19", "Remuneration policies", "Ödeme politikaları", "Text", "Genel", "Zorunlu"),
                ("2-20", "Process to determine remuneration", "Ödeme belirleme süreci", "Text", "Genel", "Zorunlu"),
                ("2-21", "Annual total compensation ratio", "Yıllık toplam tazminat oranı", "Ratio", "Oran", "Zorunlu"),
                ("2-22", "Statement on sustainable development strategy", "Sürdürülebilir kalkınma stratejisi beyanı", "Text", "Genel", "Zorunlu"),
                ("2-23", "Policy commitments", "Politika taahhütleri", "Text", "Genel", "Zorunlu"),
                ("2-24", "Embedding policy commitments", "Politika taahhütlerinin gömülmesi", "Text", "Genel", "Zorunlu"),
                ("2-25", "Contributing to public policy", "Kamu politikasına katkı", "Text", "Genel", "Zorunlu"),
                ("2-26", "Lobbying", "Lobicilik", "Text", "Genel", "Zorunlu"),
                ("2-27", "Political contributions", "Siyasi katkılar", "Text", "Genel", "Zorunlu"),
                ("2-28", "Approach to stakeholder engagement", "Paydaş katılımı yaklaşımı", "Text", "Genel", "Zorunlu"),
                ("2-29", "Stakeholder groups", "Paydaş grupları", "Text", "Genel", "Zorunlu"),
                ("2-30", "Collective bargaining agreements", "Toplu pazarlık anlaşmaları", "Text", "Genel", "Zorunlu")
            ]

            for code, title, description, unit, methodology, requirement in gri2_indicators:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (gri2_id, code, title, description, unit, methodology, requirement))

            # GRI 3 - Material Topics göstergeleri
            cursor.execute("SELECT id FROM gri_standards WHERE code = 'GRI 3'")
            gri3_id = cursor.fetchone()[0]

            gri3_indicators = [
                ("3-1", "Process to determine material topics", "Materyal konu belirleme süreci", "Text", "Genel", "Zorunlu"),
                ("3-2", "List of material topics", "Materyal konular listesi", "Text", "Genel", "Zorunlu"),
                ("3-3", "Management of material topics", "Materyal konuların yönetimi", "Text", "Genel", "Zorunlu")
            ]

            for code, title, description, unit, methodology, requirement in gri3_indicators:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (gri3_id, code, title, description, unit, methodology, requirement))

            # GRI 301 - Materials göstergeleri
            cursor.execute("SELECT id FROM gri_standards WHERE code = 'GRI 301'")
            gri301_id = cursor.fetchone()[0]

            gri301_indicators = [
                ("301-1", "Materials used by weight or volume", "Ağırlık veya hacim olarak kullanılan malzemeler", "Ton/m³", "Ölçüm", "Zorunlu"),
                ("301-2", "Recycled input materials used", "Kullanılan geri dönüştürülmüş girdi malzemeleri", "Ton/m³", "Ölçüm", "Zorunlu"),
                ("301-3", "Reclaimed products and their packaging materials", "Geri kazanılan ürünler ve ambalaj malzemeleri", "Ton/m³", "Ölçüm", "Zorunlu")
            ]

            for code, title, description, unit, methodology, requirement in gri301_indicators:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (gri301_id, code, title, description, unit, methodology, requirement))

            # GRI 302 - Energy göstergeleri
            cursor.execute("SELECT id FROM gri_standards WHERE code = 'GRI 302'")
            gri302_id = cursor.fetchone()[0]

            gri302_indicators = [
                ("302-1", "Energy consumption within the organization", "Organizasyon içi enerji tüketimi", "MWh", "Ölçüm", "Zorunlu"),
                ("302-2", "Energy consumption outside of the organization", "Organizasyon dışı enerji tüketimi", "MWh", "Ölçüm", "Zorunlu"),
                ("302-3", "Energy intensity", "Enerji yoğunluğu", "MWh/unit", "Hesaplama", "Zorunlu"),
                ("302-4", "Reduction of energy consumption", "Enerji tüketiminin azaltılması", "MWh", "Ölçüm", "Zorunlu"),
                ("302-5", "Reductions in energy requirements of products and services", "Ürün ve hizmetlerin enerji gereksinimlerinin azaltılması", "MWh", "Ölçüm", "Zorunlu")
            ]

            for code, title, description, unit, methodology, requirement in gri302_indicators:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (gri302_id, code, title, description, unit, methodology, requirement))

            conn.commit()
            logging.info("GRI gostergeleri eklendi")
            return True

        except Exception as e:
            logging.error(f"GRI gostergeleri ekleme hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_gri_standards(self) -> List[Dict]:
        """GRI standartlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, code, title, category, description, sector
            FROM gri_standards
            ORDER BY category, code
        """)

        standards = []
        for row in cursor.fetchall():
            standards.append({
                'id': row[0],
                'code': row[1],
                'title': row[2],
                'category': row[3],
                'description': row[4],
                'sector': row[5]
            })

        conn.close()
        return standards

    def get_gri_indicators(self, standard_id: int = None) -> List[Dict]:
        """GRI göstergelerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if standard_id:
            cursor.execute("""
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology, i.reporting_requirement,
                       s.code as standard_code, s.title as standard_title
                FROM gri_indicators i
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE i.standard_id = ?
                ORDER BY i.code
            """, (standard_id,))
        else:
            cursor.execute("""
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology, i.reporting_requirement,
                       s.code as standard_code, s.title as standard_title
                FROM gri_indicators i
                JOIN gri_standards s ON i.standard_id = s.id
                ORDER BY s.code, i.code
            """)

        indicators = []
        for row in cursor.fetchall():
            indicators.append({
                'id': row[0],
                'code': row[1],
                'title': row[2],
                'description': row[3],
                'unit': row[4],
                'methodology': row[5],
                'reporting_requirement': row[6],
                'standard_code': row[7],
                'standard_title': row[8]
            })

        conn.close()
        return indicators

    def get_mappings_for_gri_indicator(self, gri_code: str) -> Dict:
        """Belirli bir GRI gösterge kodu için eşleştirmeleri getir (SDG↔GRI ve GRI↔TSRS)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        mappings = {
            'sdg_gri': [],
            'gri_tsrs': []
        }
        try:
            # SDG↔GRI: gri_disclosure alanı GRI gösterge kodu ile eşleşir
            cursor.execute("""
                SELECT sdg_indicator_code, gri_standard, gri_disclosure, relation_type, notes
                FROM map_sdg_gri
                WHERE gri_disclosure = ?
            """, (gri_code,))
            for row in cursor.fetchall():
                mappings['sdg_gri'].append({
                    'sdg_indicator_code': row[0],
                    'gri_standard': row[1],
                    'gri_disclosure': row[2],
                    'relation_type': row[3],
                    'notes': row[4]
                })

            # GRI↔TSRS: gri_disclosure GRI gösterge kodu ile eşleşir
            cursor.execute("""
                SELECT gri_standard, gri_disclosure, tsrs_section, tsrs_metric, relation_type, notes
                FROM map_gri_tsrs
                WHERE gri_disclosure = ?
            """, (gri_code,))
            for row in cursor.fetchall():
                mappings['gri_tsrs'].append({
                    'gri_standard': row[0],
                    'gri_disclosure': row[1],
                    'tsrs_section': row[2],
                    'tsrs_metric': row[3],
                    'relation_type': row[4],
                    'notes': row[5]
                })
        except Exception as e:
            logging.error(f"Eşleştirme getirirken hata: {e}")
        finally:
            conn.close()
        return mappings

    def save_gri_response(self, company_id: int, indicator_id: int, period: str,
                         response_value: str, numerical_value: float = None,
                         unit: str = None, methodology: str = None,
                         evidence_url: str = None, notes: str = None) -> bool:
        """GRI cevabını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO gri_responses 
                (company_id, indicator_id, period, response_value, numerical_value, 
                 unit, methodology, evidence_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, indicator_id, period, response_value, numerical_value,
                  unit, methodology, evidence_url, notes))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"GRI cevap kaydetme hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_gri_responses(self, company_id: int, period: str = None) -> List[Dict]:
        """GRI cevaplarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if period:
            cursor.execute("""
                SELECT r.id, r.indicator_id, r.period, r.response_value, r.numerical_value,
                       r.unit, r.methodology, r.reporting_status, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title as indicator_title,
                       s.code as standard_code, s.title as standard_title
                FROM gri_responses r
                JOIN gri_indicators i ON r.indicator_id = i.id
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE r.company_id = ? AND r.period = ?
                ORDER BY s.code, i.code
            """, (company_id, period))
        else:
            cursor.execute("""
                SELECT r.id, r.indicator_id, r.period, r.response_value, r.numerical_value,
                       r.unit, r.methodology, r.reporting_status, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title as indicator_title,
                       s.code as standard_code, s.title as standard_title
                FROM gri_responses r
                JOIN gri_indicators i ON r.indicator_id = i.id
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE r.company_id = ?
                ORDER BY r.period DESC, s.code, i.code
            """, (company_id,))

        responses = []
        for row in cursor.fetchall():
            responses.append({
                'id': row[0],
                'indicator_id': row[1],
                'period': row[2],
                'response_value': row[3],
                'numerical_value': row[4],
                'unit': row[5],
                'methodology': row[6],
                'reporting_status': row[7],
                'evidence_url': row[8],
                'notes': row[9],
                'indicator_code': row[10],
                'indicator_title': row[11],
                'standard_code': row[12],
                'standard_title': row[13]
            })

        conn.close()
        return responses

    def get_gri_statistics(self, company_id: int) -> Dict:
        """GRI istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Toplam standart sayısı
        cursor.execute("SELECT COUNT(*) FROM gri_standards")
        total_standards = cursor.fetchone()[0]

        # Toplam gösterge sayısı
        cursor.execute("SELECT COUNT(*) FROM gri_indicators")
        total_indicators = cursor.fetchone()[0]

        # Cevaplanan gösterge sayısı
        cursor.execute("""
            SELECT COUNT(DISTINCT indicator_id) FROM gri_responses 
            WHERE company_id = ?
        """, (company_id,))
        answered_indicators = cursor.fetchone()[0]

        # Kategori bazında istatistikler
        cursor.execute("""
            SELECT s.category, COUNT(i.id) as indicator_count,
                   COUNT(r.id) as response_count
            FROM gri_standards s
            LEFT JOIN gri_indicators i ON s.id = i.standard_id
            LEFT JOIN gri_responses r ON i.id = r.indicator_id AND r.company_id = ?
            GROUP BY s.category
            ORDER BY s.category
        """, (company_id,))

        category_stats = []
        for row in cursor.fetchall():
            category_stats.append({
                'category': row[0],
                'indicator_count': row[1],
                'response_count': row[2]
            })

        conn.close()

        return {
            'total_standards': total_standards,
            'total_indicators': total_indicators,
            'answered_indicators': answered_indicators,
            'answer_percentage': (answered_indicators / total_indicators * 100) if total_indicators > 0 else 0,
            'category_stats': category_stats
        }

    def save_indicator_response(self, indicator_code: str, response_text: str, indicator_id: int = None, company_id: int = None) -> bool:
        """GRI gösterge yanıtını kaydet (hızlı yanıt).
        Not: DB şemasına uygun olarak yanıtı `gri_responses.response_value` alanına ve mevcut yıl period’una kaydeder.
        """
        if company_id is None:
            company_id = self.company_id

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Eğer indicator_id verilmemişse, koddan bul ve birim bilgisini al
            unit = None
            if not indicator_id:
                cursor.execute("SELECT id, unit FROM gri_indicators WHERE code = ?", (indicator_code,))
                result = cursor.fetchone()
                if not result:
                    logging.info(f"Gösterge bulunamadı: {indicator_code}")
                    return False
                indicator_id = result[0]
                unit = result[1]

            period = datetime.now().strftime("%Y")  # Varsayılan period: içinde bulunulan yıl

            # Mevcut period için yanıt var mı kontrol et
            cursor.execute(
                """
                SELECT id FROM gri_responses
                WHERE company_id = ? AND indicator_id = ? AND period = ?
                """,
                (company_id, indicator_id, period),
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE gri_responses
                    SET response_value = ?, unit = COALESCE(unit, ?)
                    WHERE id = ?
                    """,
                    (response_text, unit, existing[0]),
                )
                logging.info(f"GRI yanıtı güncellendi: {indicator_code} ({period})")
            else:
                cursor.execute(
                    """
                    INSERT INTO gri_responses (company_id, indicator_id, period, response_value, unit, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (company_id, indicator_id, period, response_text, unit, datetime.now().isoformat()),
                )
                logging.info(f"Yeni GRI yanıtı eklendi: {indicator_code} ({period})")

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"GRI yanıt kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def populate_gri_standards(self) -> None:
        """GRI standartlarını ve göstergelerini doldur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # GRI Standartları verisi
            gri_standards_data = [
                # GRI 200: Economic
                ("GRI 200", "Economic", "Ekonomik Performans"),
                ("GRI 201", "Economic", "Ekonomik Performans"),
                ("GRI 202", "Economic", "Pazar Varlığı"),
                ("GRI 203", "Economic", "Dolaylı Ekonomik Etkiler"),
                ("GRI 204", "Economic", "Satın Alma Uygulamaları"),
                ("GRI 205", "Economic", "Yolsuzlukla Mücadele"),
                ("GRI 206", "Economic", "Rekabetçi Davranış"),
                ("GRI 207", "Economic", "Vergi"),

                # GRI 300: Environmental
                ("GRI 300", "Environmental", "Çevresel Performans"),
                ("GRI 301", "Environmental", "Malzemeler"),
                ("GRI 302", "Environmental", "Enerji"),
                ("GRI 303", "Environmental", "Su ve Atık Su"),
                ("GRI 304", "Environmental", "Biyoçeşitlilik"),
                ("GRI 305", "Environmental", "Emisyonlar"),
                ("GRI 306", "Environmental", "Atık ve Çevresel Etkiler"),
                ("GRI 307", "Environmental", "Çevresel Uyum"),
                ("GRI 308", "Environmental", "Tedarikçi Çevresel Değerlendirmesi"),

                # GRI 400: Social
                ("GRI 400", "Social", "Sosyal Performans"),
                ("GRI 401", "Social", "İstihdam"),
                ("GRI 402", "Social", "İşçi-İşveren İlişkileri"),
                ("GRI 403", "Social", "İş Sağlığı ve Güvenliği"),
                ("GRI 404", "Social", "Eğitim ve Öğretim"),
                ("GRI 405", "Social", "Çeşitlilik ve Eşit Fırsatlar"),
                ("GRI 406", "Social", "Ayrımcılıkla Mücadele"),
                ("GRI 407", "Social", "Toplu Görüşme Özgürlüğü"),
                ("GRI 408", "Social", "Çocuk İşçiliği"),
                ("GRI 409", "Social", "Zorla ve Mecburi İşçilik"),
                ("GRI 410", "Social", "Güvenlik Uygulamaları"),
                ("GRI 411", "Social", "İnsan Hakları Değerlendirmesi"),
                ("GRI 412", "Social", "İnsan Hakları Değerlendirmesi"),
                ("GRI 413", "Social", "Yerel Topluluklar"),
                ("GRI 414", "Social", "Tedarikçi Sosyal Değerlendirmesi"),
                ("GRI 415", "Social", "Kamu Politikası"),
                ("GRI 416", "Social", "Müşteri Sağlığı ve Güvenliği"),
                ("GRI 417", "Social", "Pazarlama ve Etiketleme"),
                ("GRI 418", "Social", "Müşteri Gizliliği"),
                ("GRI 419", "Social", "Sosyoekonomik Uyum")
            ]

            # GRI standartlarını ekle
            for code, category, title in gri_standards_data:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_standards (code, category, title, description)
                    VALUES (?, ?, ?, ?)
                """, (code, category, title, f"{title} standardı"))

            # GRI Göstergeleri verisi
            gri_indicators_data = [
                # Economic Indicators
                ("GRI 201-1", 2, "Toplam gelir", "Şirketin toplam geliri", "TL"),
                ("GRI 201-2", 2, "Finansal etkiler", "İklim değişikliğinin finansal etkileri", "TL"),
                ("GRI 202-1", 3, "Pazar varlığı", "Operasyonel pazarlar", "Sayı"),
                ("GRI 203-1", 4, "Altyapı yatırımları", "Altyapıya yapılan yatırımlar", "TL"),
                ("GRI 204-1", 5, "Yerel tedarikçi oranı", "Yerel tedarikçi yüzdesi", "%"),

                # Environmental Indicators
                ("GRI 301-1", 10, "Malzeme tüketimi", "Kullanılan malzemelerin ağırlığı", "Ton"),
                ("GRI 302-1", 11, "Enerji tüketimi", "Toplam enerji tüketimi", "MWh"),
                ("GRI 303-1", 12, "Su çekimi", "Toplam su çekimi", "m³"),
                ("GRI 304-1", 13, "Biyoçeşitlilik etkisi", "Operasyonların biyoçeşitlilik üzerindeki etkisi", "Sayı"),
                ("GRI 305-1", 14, "Sera gazı emisyonları", "Doğrudan sera gazı emisyonları", "tCO2e"),
                ("GRI 305-2", 14, "Sera gazı emisyonları", "Enerji dolaylı sera gazı emisyonları", "tCO2e"),
                ("GRI 306-1", 15, "Atık üretimi", "Üretilen atık miktarı", "Ton"),
                ("GRI 306-2", 15, "Atık yönetimi", "Atık yönetim uygulamaları", "Sayı"),

                # Social Indicators
                ("GRI 401-1", 20, "Yeni işe alımlar", "Yeni işe alınan çalışan sayısı", "Sayı"),
                ("GRI 401-2", 20, "İşten çıkarmalar", "İşten çıkarılan çalışan sayısı", "Sayı"),
                ("GRI 403-1", 22, "İş kazaları", "Mesleki yaralanma sayısı", "Sayı"),
                ("GRI 403-2", 22, "İş hastalıkları", "Mesleki hastalık sayısı", "Sayı"),
                ("GRI 404-1", 23, "Eğitim programları", "Çalışanlara verilen eğitim saatleri", "Saat"),
                ("GRI 405-1", 24, "Çeşitlilik oranı", "Cinsiyet dağılımı", "%"),
                ("GRI 405-2", 24, "Yönetim çeşitliliği", "Yönetim pozisyonlarında çeşitlilik", "%"),
                ("GRI 412-1", 31, "İnsan hakları değerlendirmesi", "İnsan hakları değerlendirme süreçleri", "Sayı"),
                ("GRI 413-1", 32, "Yerel topluluk katılımı", "Yerel topluluklarla etkileşim", "Sayı"),
                ("GRI 414-1", 33, "Tedarikçi değerlendirmesi", "Tedarikçi sosyal değerlendirmeleri", "Sayı"),
                ("GRI 416-1", 35, "Müşteri güvenliği", "Müşteri güvenliği olayları", "Sayı"),
                ("GRI 417-1", 36, "Pazarlama uyumu", "Pazarlama ve etiketleme uyumu", "Sayı"),
                ("GRI 418-1", 37, "Gizlilik ihlalleri", "Müşteri gizliliği ihlalleri", "Sayı")
            ]

            # GRI göstergelerini ekle
            for code, standard_id, title, description, unit in gri_indicators_data:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_indicators (code, standard_id, title, description, unit, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, standard_id, title, description, unit, "Mandatory"))

            conn.commit()
            logging.info("[OK] GRI standartları ve göstergeleri dolduruldu")

        except Exception as e:
            logging.error(f"[HATA] GRI verileri doldurulurken hata: {e}")
            conn.rollback()
        finally:
            conn.close()
    def get_filtered_data(self, category, search_term="", priority_filter="Tümü", requirement_filter="Tümü") -> None:
        """Filtrelenmiş veriyi getir"""
        try:
            # Kategori verilerini al
            if category == "universal":
                data = self.get_standards_by_category("Universal")
            elif category == "economic":
                data = self.get_standards_by_category("Economic")
            elif category == "environmental":
                data = self.get_standards_by_category("Environmental")
            elif category == "social":
                data = self.get_standards_by_category("Social")
            elif category == "sector":
                data = self.get_standards_by_category("Sector-Specific")
            else:
                data = {'standards': [], 'indicators': []}

            # Arama filtresi uygula
            if search_term:
                filtered_indicators = []
                for indicator in data.get('indicators', []):
                    if (search_term.lower() in indicator.get('code', '').lower() or
                        search_term.lower() in indicator.get('title', '').lower()):
                        filtered_indicators.append(indicator)
                data['indicators'] = filtered_indicators

            return data

        except Exception as e:
            logging.error(f"Filtrelenmiş veri getirilirken hata: {e}")
            return {'standards': [], 'indicators': []}
