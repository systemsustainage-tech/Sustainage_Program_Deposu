import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from config.settings import ensure_directories, get_db_path
from backend.core.base_manager import BaseTenantManager


class GRIManager(BaseTenantManager):
    """GRI (Global Reporting Initiative) modülü yöneticisi"""

    def __init__(self, db_path: str | None = None, company_id: int | None = None) -> None:
        if not db_path:
            ensure_directories()
            db_path = get_db_path()
        super().__init__(db_path, company_id)

        # Tabloları oluştur ve veri doldur
        self.create_gri_tables()
        self.populate_gri_standards()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        cid = self._ensure_context(company_id)
        stats = {
            'selected_goals': 0,
            'indicators': 0,
            'disclosures': 0
        }
        
        try:
            # Seçilen SDG hedefleri
            row = self.select_one(
                "SELECT COUNT(*) as count FROM user_sdg_selections WHERE company_id = ?", 
                (cid,)
            )
            if row:
                stats['selected_goals'] = row['count']
                
            # Haritalanmış GRI göstergeleri (tahmini)
            selected_ids = self.get_selected_sdg_goals(cid)
            indicators = self.get_sdg_indicators_for_goals(selected_ids)
            stats['indicators'] = len(indicators)
            
            gri_mappings = self.get_gri_indicators_for_sdg_selection(cid)
            stats['disclosures'] = len(gri_mappings)
                
        except Exception as e:
            logging.error(f"GRI stats error: {e}")
            
        return stats

    def get_selected_sdg_goals(self, company_id: int) -> List[int]:
        """Şirket için seçilen SDG hedeflerini getir"""
        cid = self._ensure_context(company_id)

        try:
            # user_sdg_selections tablosundan seçilen hedefleri al
            rows = self.select_all(
                """
                SELECT goal_id 
                FROM user_sdg_selections 
                WHERE company_id = ?
                ORDER BY goal_id
                """, 
                (cid,)
            )
            return [row['goal_id'] for row in rows]

        except Exception as e:
            logging.error(f"Seçilen SDG hedefleri getirilirken hata: {e}")
            return []

    def get_sdg_indicators_for_goals(self, goal_ids: List[int]) -> List[str]:
        """Seçilen SDG hedefleri için gösterge kodlarını getir"""
        if not goal_ids:
            return []

        try:
            placeholders = ','.join('?' * len(goal_ids))
            rows = self.select_all(f"""
                SELECT DISTINCT si.code 
                FROM sdg_indicators si
                JOIN sdg_targets st ON si.target_id = st.id
                WHERE st.goal_id IN ({placeholders})
            """, tuple(goal_ids))

            return [row['code'] for row in rows]
        except Exception as e:
            logging.error(f"SDG gösterge kodları getirilirken hata: {e}")
            return []

    def get_gri_indicators_for_sdg_selection(self, company_id: int) -> List[Dict]:
        """SDG seçimlerine göre ilgili GRI göstergelerini getir"""
        cid = self._ensure_context(company_id)
        
        # Seçilen SDG hedeflerini al
        selected_goals = self.get_selected_sdg_goals(cid)
        if not selected_goals:
            return []

        # SDG gösterge kodlarını al
        sdg_indicator_codes = self.get_sdg_indicators_for_goals(selected_goals)
        if not sdg_indicator_codes:
            return []

        try:
            # SDG-GRI eşleştirmelerini al
            placeholders = ','.join('?' * len(sdg_indicator_codes))
            gri_mappings = self.select_all(f"""
                SELECT DISTINCT mg.gri_standard, mg.gri_disclosure
                FROM map_sdg_gri mg
                WHERE mg.sdg_indicator_code IN ({placeholders})
            """, tuple(sdg_indicator_codes))

            if not gri_mappings:
                return []

            # GRI göstergelerini al
            gri_disclosures = [mapping['gri_disclosure'] for mapping in gri_mappings if mapping['gri_disclosure'] and mapping['gri_disclosure'].strip()]
            gri_standards = [mapping['gri_standard'] for mapping in gri_mappings]

            # Eğer disclosure kodları yoksa, standart kodlarına göre ara
            if not gri_disclosures:
                standard_placeholders = ','.join('?' * len(set(gri_standards)))
                rows = self.select_all(f"""
                    SELECT gi.id, gi.code, gi.title, gi.description, gi.unit, gi.methodology, 
                           gi.reporting_requirement, gs.code as standard_code, gs.title as standard_title,
                           gs.category
                    FROM gri_indicators gi
                    JOIN gri_standards gs ON gi.standard_id = gs.id
                    WHERE gs.code IN ({standard_placeholders})
                    ORDER BY gs.category, gs.code, gi.code
                """, tuple(set(gri_standards)))
            else:
                gri_placeholders = ','.join('?' * len(gri_disclosures))
                rows = self.select_all(f"""
                    SELECT gi.id, gi.code, gi.title, gi.description, gi.unit, gi.methodology, 
                           gi.reporting_requirement, gs.code as standard_code, gs.title as standard_title,
                           gs.category
                    FROM gri_indicators gi
                    JOIN gri_standards gs ON gi.standard_id = gs.id
                    WHERE gi.code IN ({gri_placeholders})
                    ORDER BY gs.category, gs.code, gi.code
                """, tuple(gri_disclosures))

            results = []

            for row in rows:
                result = dict(row)

                # Bu GRI göstergesine eşleşen SDG gösterge kodlarını bul
                sdg_rows = self.select_all("""
                    SELECT sdg_indicator_code FROM map_sdg_gri 
                    WHERE gri_disclosure = ?
                """, (result['code'],))
                result['mapped_sdg_indicators'] = [r['sdg_indicator_code'] for r in sdg_rows]

                # TSRS eşleştirmelerini bul
                tsrs_rows = self.select_all("""
                    SELECT tsrs_section, tsrs_metric FROM map_gri_tsrs 
                    WHERE gri_disclosure = ?
                """, (result['code'],))
                result['mapped_tsrs'] = [{'section': r['tsrs_section'], 'metric': r['tsrs_metric']} for r in tsrs_rows]

                results.append(result)

            return results

        except Exception as e:
            logging.error(f"GRI göstergeleri getirilirken hata: {e}")
            return []

    def get_gri_standards_for_sdg_selection(self, company_id: int) -> Dict[str, List[Dict]]:
        """SDG seçimlerine göre GRI standartlarını kategorilere göre grupla"""
        cid = self._ensure_context(company_id)
        gri_indicators = self.get_gri_indicators_for_sdg_selection(cid)

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
        try:
            if category == "universal":
                rows = self.select_all("""
                    SELECT code, title, description, 
                           type, category, created_at
                    FROM gri_standards 
                    WHERE type = 'Universal'
                    ORDER BY code
                """)
            else:
                rows = self.select_all("""
                    SELECT code, title, description, 
                           type, category, created_at
                    FROM gri_standards 
                    WHERE category = ?
                    ORDER BY code
                """, (category.title(),))

            results = [dict(row) for row in rows]

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

    def get_indicators_by_standard(self, standard_code) -> List[Dict]:
        """Standart koduna göre göstergeleri getir"""
        try:
            rows = self.select_all("""
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

            results = []
            for row in rows:
                indicator = dict(row)
                # Gösterge kodunu indicator_code olarak da ekle
                indicator['indicator_code'] = indicator['code']
                indicator['indicator_title'] = indicator['title']
                results.append(indicator)

            return results

        except Exception as e:
            logging.error(f"GRI göstergeleri getirilirken hata: {e}")
            return []

    def create_gri_tables(self) -> bool:
        """GRI tablolarını oluştur"""
        try:
            # GRI Standartları
            self.db.execute_query("""
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
                self.db.execute_query("SELECT sector FROM gri_standards LIMIT 1")
            except Exception:
                self.db.execute_query("ALTER TABLE gri_standards ADD COLUMN sector TEXT DEFAULT 'General'")

            # GRI Göstergeleri
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS gri_indicators (
                    id INTEGER PRIMARY KEY,
                    standard_id INTEGER NOT NULL,
                    code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    unit TEXT,
                    methodology TEXT,
                    reporting_requirement TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
                )
            """)
            
            # Ensure unique index exists (for migration)
            self.db.execute_query("CREATE UNIQUE INDEX IF NOT EXISTS idx_gri_indicators_code ON gri_indicators(code)")

            # GRI Cevapları
            self.db.execute_query("""
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
            self.db.execute_query("""
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

            logging.info("GRI tablolari basariyla olusturuldu")
            return True

        except Exception as e:
            logging.error(f"GRI tablolari olusturma hatasi: {e}")
            return False

    def insert_gri_standards(self) -> bool:
        """GRI standartlarını ekle"""
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
                self.db.execute_update("""
                    INSERT INTO gri_standards (code, title, category, description, sector)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(code) DO UPDATE SET
                        title=excluded.title,
                        category=excluded.category,
                        description=excluded.description,
                        sector=excluded.sector
                """, (code, title, category, description, sector))

            logging.info(f"{len(all_standards)} GRI standardi eklendi/guncellendi")
            return True

        except Exception as e:
            logging.error(f"GRI standartlari ekleme hatasi: {e}")
            return False

    def insert_gri_indicators(self) -> bool:
        """GRI göstergelerini ekle"""
        try:
            # GRI 2 - General Disclosures göstergeleri
            rows = self.db.execute_query("SELECT id FROM gri_standards WHERE code = 'GRI 2'")
            if not rows:
                return False
            gri2_id = rows[0]['id']

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
                self.db.execute_update("""
                    INSERT INTO gri_indicators 
                    (standard_id, code, title, description, unit, methodology, reporting_requirement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(code) DO UPDATE SET
                        standard_id=excluded.standard_id,
                        title=excluded.title,
                        description=excluded.description,
                        unit=excluded.unit,
                        methodology=excluded.methodology,
                        reporting_requirement=excluded.reporting_requirement
                """, (gri2_id, code, title, description, unit, methodology, requirement))

            # GRI 3 - Material Topics göstergeleri
            rows = self.db.execute_query("SELECT id FROM gri_standards WHERE code = 'GRI 3'")
            if rows:
                gri3_id = rows[0]['id']
                gri3_indicators = [
                    ("3-1", "Process to determine material topics", "Materyal konu belirleme süreci", "Text", "Genel", "Zorunlu"),
                    ("3-2", "List of material topics", "Materyal konular listesi", "Text", "Genel", "Zorunlu"),
                    ("3-3", "Management of material topics", "Materyal konuların yönetimi", "Text", "Genel", "Zorunlu")
                ]

                for code, title, description, unit, methodology, requirement in gri3_indicators:
                    self.db.execute_update("""
                        INSERT INTO gri_indicators 
                        (standard_id, code, title, description, unit, methodology, reporting_requirement)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(code) DO UPDATE SET
                            standard_id=excluded.standard_id,
                            title=excluded.title,
                            description=excluded.description,
                            unit=excluded.unit,
                            methodology=excluded.methodology,
                            reporting_requirement=excluded.reporting_requirement
                    """, (gri3_id, code, title, description, unit, methodology, requirement))

            # GRI 301 - Materials göstergeleri
            rows = self.db.execute_query("SELECT id FROM gri_standards WHERE code = 'GRI 301'")
            if rows:
                gri301_id = rows[0]['id']
                gri301_indicators = [
                    ("301-1", "Materials used by weight or volume", "Ağırlık veya hacim olarak kullanılan malzemeler", "Ton/m³", "Ölçüm", "Zorunlu"),
                    ("301-2", "Recycled input materials used", "Kullanılan geri dönüştürülmüş girdi malzemeleri", "Ton/m³", "Ölçüm", "Zorunlu"),
                    ("301-3", "Reclaimed products and their packaging materials", "Geri kazanılan ürünler ve ambalaj malzemeleri", "Ton/m³", "Ölçüm", "Zorunlu")
                ]

                for code, title, description, unit, methodology, requirement in gri301_indicators:
                    self.db.execute_update("""
                        INSERT INTO gri_indicators 
                        (standard_id, code, title, description, unit, methodology, reporting_requirement)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(code) DO UPDATE SET
                            standard_id=excluded.standard_id,
                            title=excluded.title,
                            description=excluded.description,
                            unit=excluded.unit,
                            methodology=excluded.methodology,
                            reporting_requirement=excluded.reporting_requirement
                    """, (gri301_id, code, title, description, unit, methodology, requirement))

            # GRI 302 - Energy göstergeleri
            rows = self.db.execute_query("SELECT id FROM gri_standards WHERE code = 'GRI 302'")
            if rows:
                gri302_id = rows[0]['id']
                gri302_indicators = [
                    ("302-1", "Energy consumption within the organization", "Organizasyon içi enerji tüketimi", "MWh", "Ölçüm", "Zorunlu"),
                    ("302-2", "Energy consumption outside of the organization", "Organizasyon dışı enerji tüketimi", "MWh", "Ölçüm", "Zorunlu"),
                    ("302-3", "Energy intensity", "Enerji yoğunluğu", "MWh/unit", "Hesaplama", "Zorunlu"),
                    ("302-4", "Reduction of energy consumption", "Enerji tüketiminin azaltılması", "MWh", "Ölçüm", "Zorunlu"),
                    ("302-5", "Reductions in energy requirements of products and services", "Ürün ve hizmetlerin enerji gereksinimlerinin azaltılması", "MWh", "Ölçüm", "Zorunlu")
                ]

                for code, title, description, unit, methodology, requirement in gri302_indicators:
                    self.db.execute_update("""
                        INSERT INTO gri_indicators 
                        (standard_id, code, title, description, unit, methodology, reporting_requirement)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(code) DO UPDATE SET
                            standard_id=excluded.standard_id,
                            title=excluded.title,
                            description=excluded.description,
                            unit=excluded.unit,
                            methodology=excluded.methodology,
                            reporting_requirement=excluded.reporting_requirement
                    """, (gri302_id, code, title, description, unit, methodology, requirement))

            logging.info("GRI gostergeleri eklendi")
            return True

        except Exception as e:
            logging.error(f"GRI gostergeleri ekleme hatasi: {e}")
            return False

    def get_gri_standards(self) -> List[Dict]:
        """GRI standartlarını getir"""
        rows = self.select_all("""
            SELECT id, code, title, category, description, sector
            FROM gri_standards
            ORDER BY category, code
        """)
        return [dict(row) for row in rows]

    def get_gri_indicators(self, standard_id: int = None) -> List[Dict]:
        """GRI göstergelerini getir"""
        if standard_id:
            rows = self.select_all("""
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology, i.reporting_requirement,
                       s.code as standard_code, s.title as standard_title
                FROM gri_indicators i
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE i.standard_id = ?
                ORDER BY i.code
            """, (standard_id,))
        else:
            rows = self.select_all("""
                SELECT i.id, i.code, i.title, i.description, i.unit, i.methodology, i.reporting_requirement,
                       s.code as standard_code, s.title as standard_title
                FROM gri_indicators i
                JOIN gri_standards s ON i.standard_id = s.id
                ORDER BY s.code, i.code
            """)

        return [dict(row) for row in rows]

    def get_mappings_for_gri_indicator(self, gri_code: str) -> Dict:
        """Belirli bir GRI gösterge kodu için eşleştirmeleri getir (SDG↔GRI ve GRI↔TSRS)."""
        mappings = {
            'sdg_gri': [],
            'gri_tsrs': []
        }
        try:
            # SDG↔GRI: gri_disclosure alanı GRI gösterge kodu ile eşleşir
            rows = self.select_all("""
                SELECT sdg_indicator_code, gri_standard, gri_disclosure, relation_type, notes
                FROM map_sdg_gri
                WHERE gri_disclosure = ?
            """, (gri_code,))
            
            for row in rows:
                mappings['sdg_gri'].append({
                    'sdg_indicator_code': row['sdg_indicator_code'],
                    'gri_standard': row['gri_standard'],
                    'gri_disclosure': row['gri_disclosure'],
                    'relation_type': row['relation_type'],
                    'notes': row['notes']
                })

            # GRI↔TSRS: gri_disclosure GRI gösterge kodu ile eşleşir
            rows = self.execute_query("""
                SELECT gri_standard, gri_disclosure, tsrs_section, tsrs_metric, relation_type, notes
                FROM map_gri_tsrs
                WHERE gri_disclosure = ?
            """, (gri_code,))
            
            for row in rows:
                mappings['gri_tsrs'].append({
                    'gri_standard': row['gri_standard'],
                    'gri_disclosure': row['gri_disclosure'],
                    'tsrs_section': row['tsrs_section'],
                    'tsrs_metric': row['tsrs_metric'],
                    'relation_type': row['relation_type'],
                    'notes': row['notes']
                })
        except Exception as e:
            logging.error(f"Eşleştirme getirirken hata: {e}")
            
        return mappings

    def save_gri_response(self, company_id: int, indicator_id: int, period: str,
                         response_value: str, numerical_value: float = None,
                         unit: str = None, methodology: str = None,
                         evidence_url: str = None, notes: str = None) -> bool:
        """GRI cevabını kaydet"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT OR REPLACE INTO gri_responses 
                (company_id, indicator_id, period, response_value, numerical_value, 
                 unit, methodology, evidence_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, indicator_id, period, response_value, numerical_value,
                  unit, methodology, evidence_url, notes))
            return True

        except Exception as e:
            logging.error(f"GRI cevap kaydetme hatasi: {e}")
            return False

    def get_gri_responses(self, company_id: int, period: str = None) -> List[Dict]:
        """GRI cevaplarını getir"""
        cid = self._ensure_context(company_id)

        if period:
            rows = self.execute_query("""
                SELECT r.id, r.indicator_id, r.period, r.response_value, r.numerical_value,
                       r.unit, r.methodology, r.reporting_status, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title as indicator_title,
                       s.code as standard_code, s.title as standard_title
                FROM gri_responses r
                JOIN gri_indicators i ON r.indicator_id = i.id
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE r.company_id = ? AND r.period = ?
                ORDER BY s.code, i.code
            """, (cid, period))
        else:
            rows = self.execute_query("""
                SELECT r.id, r.indicator_id, r.period, r.response_value, r.numerical_value,
                       r.unit, r.methodology, r.reporting_status, r.evidence_url, r.notes,
                       i.code as indicator_code, i.title as indicator_title,
                       s.code as standard_code, s.title as standard_title
                FROM gri_responses r
                JOIN gri_indicators i ON r.indicator_id = i.id
                JOIN gri_standards s ON i.standard_id = s.id
                WHERE r.company_id = ?
                ORDER BY r.period DESC, s.code, i.code
            """, (cid,))

        return [dict(row) for row in rows]

    def get_gri_statistics(self, company_id: int) -> Dict:
        """GRI istatistiklerini getir"""
        cid = self._ensure_context(company_id)

        # Toplam standart sayısı
        row = self.select_one("SELECT COUNT(*) as count FROM gri_standards")
        total_standards = row['count'] if row else 0

        # Toplam gösterge sayısı
        row = self.select_one("SELECT COUNT(*) as count FROM gri_indicators")
        total_indicators = row['count'] if row else 0

        # Cevaplanan gösterge sayısı
        row = self.select_one("""
            SELECT COUNT(DISTINCT indicator_id) as count FROM gri_responses 
            WHERE company_id = ?
        """, (cid,))
        answered_indicators = row['count'] if row else 0

        # Kategori bazında istatistikler
        rows = self.execute_query("""
            SELECT s.category, COUNT(i.id) as indicator_count,
                   COUNT(r.id) as response_count
            FROM gri_standards s
            LEFT JOIN gri_indicators i ON s.id = i.standard_id
            LEFT JOIN gri_responses r ON i.id = r.indicator_id AND r.company_id = ?
            GROUP BY s.category
            ORDER BY s.category
        """, (cid,))

        category_stats = []
        for row in rows:
            category_stats.append({
                'category': row['category'],
                'indicator_count': row['indicator_count'],
                'response_count': row['response_count']
            })

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
        cid = self._ensure_context(company_id)

        try:
            # Eğer indicator_id verilmemişse, koddan bul ve birim bilgisini al
            unit = None
            if not indicator_id:
                row = self.select_one("SELECT id, unit FROM gri_indicators WHERE code = ?", (indicator_code,))
                if not row:
                    logging.info(f"Gösterge bulunamadı: {indicator_code}")
                    return False
                indicator_id = row['id']
                unit = row['unit']

            period = datetime.now().strftime("%Y")  # Varsayılan period: içinde bulunulan yıl

            # Mevcut period için yanıt var mı kontrol et
            existing = self.select_one(
                """
                SELECT id FROM gri_responses
                WHERE company_id = ? AND indicator_id = ? AND period = ?
                """,
                (cid, indicator_id, period),
            )

            if existing:
                self.execute_update(
                    """
                    UPDATE gri_responses
                    SET response_value = ?, unit = COALESCE(unit, ?)
                    WHERE id = ?
                    """,
                    (response_text, unit, existing['id']),
                )
                logging.info(f"GRI yanıtı güncellendi: {indicator_code} ({period})")
            else:
                self.execute_update(
                    """
                    INSERT INTO gri_responses (company_id, indicator_id, period, response_value, unit, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (cid, indicator_id, period, response_text, unit, datetime.now().isoformat()),
                )
                logging.info(f"Yeni GRI yanıtı eklendi: {indicator_code} ({period})")

            return True

        except Exception as e:
            logging.error(f"GRI yanıt kaydetme hatası: {e}")
            return False

    def populate_gri_standards(self) -> None:
        """GRI standartlarını ve göstergelerini doldur"""
        
        try:
            # 1. Standartları ve temel göstergeleri doldur
            self.insert_gri_standards()
            self.insert_gri_indicators()

            # 2. Ek göstergeleri doldur
            gri_indicators_data = [
                # Economic Indicators
                ("GRI 201-1", "GRI 201", "Toplam gelir", "Şirketin toplam geliri", "TL"),
                ("GRI 201-2", "GRI 201", "Finansal etkiler", "İklim değişikliğinin finansal etkileri", "TL"),
                ("GRI 202-1", "GRI 202", "Pazar varlığı", "Operasyonel pazarlar", "Sayı"),
                ("GRI 203-1", "GRI 203", "Altyapı yatırımları", "Altyapıya yapılan yatırımlar", "TL"),
                ("GRI 204-1", "GRI 204", "Yerel tedarikçi oranı", "Yerel tedarikçi yüzdesi", "%"),

                # Environmental Indicators
                ("GRI 301-1", "GRI 301", "Malzeme tüketimi", "Kullanılan malzemelerin ağırlığı", "Ton"),
                ("GRI 302-1", "GRI 302", "Enerji tüketimi", "Toplam enerji tüketimi", "MWh"),
                ("GRI 303-1", "GRI 303", "Su çekimi", "Toplam su çekimi", "m³"),
                ("GRI 304-1", "GRI 304", "Biyoçeşitlilik etkisi", "Operasyonların biyoçeşitlilik üzerindeki etkisi", "Sayı"),
                ("GRI 305-1", "GRI 305", "Sera gazı emisyonları", "Doğrudan sera gazı emisyonları", "tCO2e"),
                ("GRI 305-2", "GRI 305", "Sera gazı emisyonları", "Enerji dolaylı sera gazı emisyonları", "tCO2e"),
                ("GRI 306-1", "GRI 306", "Atık üretimi", "Üretilen atık miktarı", "Ton"),
                ("GRI 306-2", "GRI 306", "Atık yönetimi", "Atık yönetim uygulamaları", "Sayı"),

                # Social Indicators
                ("GRI 401-1", "GRI 401", "Yeni işe alımlar", "Yeni işe alınan çalışan sayısı", "Sayı"),
                ("GRI 401-2", "GRI 401", "İşten çıkarmalar", "İşten çıkarılan çalışan sayısı", "Sayı"),
                ("GRI 403-1", "GRI 403", "İş kazaları", "Mesleki yaralanma sayısı", "Sayı"),
                ("GRI 403-2", "GRI 403", "İş hastalıkları", "Mesleki hastalık sayısı", "Sayı"),
                ("GRI 404-1", "GRI 404", "Eğitim programları", "Çalışanlara verilen eğitim saatleri", "Saat"),
                ("GRI 405-1", "GRI 405", "Çeşitlilik oranı", "Cinsiyet dağılımı", "%"),
                ("GRI 405-2", "GRI 405", "Yönetim çeşitliliği", "Yönetim pozisyonlarında çeşitlilik", "%"),
                ("GRI 412-1", "GRI 412", "İnsan hakları değerlendirmesi", "İnsan hakları değerlendirme süreçleri", "Sayı"),
                ("GRI 413-1", "GRI 413", "Yerel topluluk katılımı", "Yerel topluluklarla etkileşim", "Sayı"),
                ("GRI 414-1", "GRI 414", "Tedarikçi değerlendirmesi", "Tedarikçi sosyal değerlendirmeleri", "Sayı"),
                ("GRI 416-1", "GRI 416", "Müşteri güvenliği", "Müşteri güvenliği olayları", "Sayı"),
                ("GRI 417-1", "GRI 417", "Pazarlama uyumu", "Pazarlama ve etiketleme uyumu", "Sayı"),
                ("GRI 418-1", "GRI 418", "Gizlilik ihlalleri", "Müşteri gizliliği ihlalleri", "Sayı")
            ]

            # GRI göstergelerini ekle
            for code, std_code, title, description, unit in gri_indicators_data:
                rows = self.db.execute_query("SELECT id FROM gri_standards WHERE code = ?", (std_code,))
                if rows:
                    std_id = rows[0]['id']
                    self.db.execute_update("""
                        INSERT INTO gri_indicators (code, standard_id, title, description, unit, reporting_requirement)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(code) DO UPDATE SET
                            standard_id=excluded.standard_id,
                            title=excluded.title,
                            description=excluded.description,
                            unit=excluded.unit,
                            reporting_requirement=excluded.reporting_requirement
                    """, (code, std_id, title, description, unit, "Mandatory"))

            logging.info("[OK] GRI standartları ve göstergeleri dolduruldu")

        except Exception as e:
            logging.error(f"GRI verileri doldurulurken hata: {e}")

    def get_filtered_data(self, category, search_term="", priority_filter="Tümü", requirement_filter="Tümü") -> Dict:
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
