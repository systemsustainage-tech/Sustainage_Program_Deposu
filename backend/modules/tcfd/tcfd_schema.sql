-- TCFD (Task Force on Climate-related Financial Disclosures) Veritabanı Şeması
-- Ana veritabanına (sdg_desktop.sqlite) eklenecek tablolar

-- ============================================================================
-- 1. GOVERNANCE (Yönetişim)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tcfd_governance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Yönetim Kurulu Gözetimi
    board_oversight TEXT,                      -- YK'nın iklim risklerini gözetimi
    board_frequency TEXT,                      -- YK toplantı sıklığı (Yıllık, Çeyreklik, Aylık)
    board_expertise TEXT,                      -- YK'da iklim uzmanlığı
    
    -- Yönetimin Rolü
    management_role TEXT,                      -- Üst yönetimin rolü
    management_structure TEXT,                 -- Organizasyon yapısı
    management_responsibility TEXT,            -- Sorumluluk dağılımı
    
    -- Komiteler ve Birimler
    climate_committee INTEGER DEFAULT 0,      -- İklim komitesi var mı? (0/1)
    committee_name TEXT,                       -- Komite adı
    committee_members TEXT,                    -- Komite üyeleri
    responsible_executive TEXT,                -- Sorumlu yönetici
    
    -- Entegrasyon
    strategy_integration TEXT,                 -- Stratejiye entegrasyon
    risk_integration TEXT,                     -- Risk yönetimine entegrasyon
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, reporting_year)
);

-- ============================================================================
-- 2. STRATEGY (Strateji)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tcfd_strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Kısa, Orta, Uzun Vadeli Riskler
    short_term_risks TEXT,                     -- Kısa vade (0-3 yıl)
    medium_term_risks TEXT,                    -- Orta vade (3-10 yıl)
    long_term_risks TEXT,                      -- Uzun vade (10+ yıl)
    
    -- Fırsatlar
    short_term_opportunities TEXT,
    medium_term_opportunities TEXT,
    long_term_opportunities TEXT,
    
    -- İş, Strateji ve Finansal Planlama Üzerindeki Etki
    business_impact TEXT,                      -- İş modeli etkisi
    strategy_impact TEXT,                      -- Strateji etkisi
    financial_impact TEXT,                     -- Finansal planlama etkisi
    
    -- Dayanıklılık (Resilience)
    resilience_assessment TEXT,                -- Dayanıklılık değerlendirmesi
    adaptation_plans TEXT,                     -- Uyum planları
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, reporting_year)
);

-- Senaryo Analizi
CREATE TABLE IF NOT EXISTS tcfd_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Senaryo Bilgileri
    scenario_name TEXT NOT NULL,               -- 2°C, 4°C, Net Zero, vb.
    scenario_source TEXT,                      -- IEA, IPCC, NGFS
    scenario_type TEXT,                        -- Transition, Physical, Combined
    temperature_target REAL,                   -- Sıcaklık hedefi (°C)
    time_horizon INTEGER,                      -- Zaman ufku (yıl)
    
    -- Varsayımlar
    assumptions TEXT,                          -- Senaryo varsayımları (JSON)
    carbon_price REAL,                         -- Karbon fiyatı ($/ton)
    policy_stringency TEXT,                    -- Politika sertliği (Low/Medium/High)
    technology_change TEXT,                    -- Teknoloji değişimi
    
    -- Finansal Etkiler
    revenue_impact REAL,                       -- Gelir etkisi (%)
    cost_impact REAL,                          -- Maliyet etkisi (%)
    capex_impact REAL,                         -- Yatırım etkisi (milyon)
    total_financial_impact REAL,               -- Toplam finansal etki (milyon)
    
    -- Narrative
    description TEXT,                          -- Senaryo açıklaması
    key_findings TEXT,                         -- Ana bulgular
    strategic_implications TEXT,               -- Stratejik çıkarımlar
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. RISK MANAGEMENT (Risk Yönetimi)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tcfd_risk_management (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Risk Tanımlama ve Değerlendirme Süreci
    identification_process TEXT,               -- Risk tanımlama süreci
    assessment_process TEXT,                   -- Risk değerlendirme süreci
    assessment_criteria TEXT,                  -- Değerlendirme kriterleri
    
    -- Risk Yönetimi Süreci
    management_process TEXT,                   -- Risk yönetim süreci
    mitigation_strategies TEXT,                -- Azaltma stratejileri
    monitoring_process TEXT,                   -- İzleme süreci
    
    -- Entegrasyon
    integration_process TEXT,                  -- Genel risk yönetimine entegrasyon
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, reporting_year)
);

-- İklim Riskleri Katalogu
CREATE TABLE IF NOT EXISTS tcfd_climate_risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Risk Kategorisi
    risk_category TEXT NOT NULL,               -- Transition, Physical
    risk_type TEXT NOT NULL,                   -- Policy, Technology, Market, Reputation, Acute, Chronic
    risk_subcategory TEXT,                     -- Alt kategori
    
    -- Risk Tanımı
    risk_name TEXT NOT NULL,                   -- Risk adı
    risk_description TEXT,                     -- Risk açıklaması
    
    -- Değerlendirme
    likelihood TEXT,                           -- Olasılık (Very Low, Low, Medium, High, Very High)
    likelihood_score INTEGER,                  -- Olasılık skoru (1-5)
    impact TEXT,                               -- Etki (Very Low, Low, Medium, High, Very High)
    impact_score INTEGER,                      -- Etki skoru (1-5)
    risk_rating TEXT,                          -- Risk derecesi (Low, Medium, High, Critical)
    risk_score INTEGER,                        -- Risk skoru (likelihood × impact)
    
    -- Zaman Ufku
    time_horizon TEXT,                         -- Short, Medium, Long
    
    -- Finansal Etki
    financial_impact_low REAL,                 -- Minimum finansal etki (milyon)
    financial_impact_high REAL,                -- Maksimum finansal etki (milyon)
    financial_impact_currency TEXT DEFAULT 'TRY',
    
    -- Yönetim
    current_controls TEXT,                     -- Mevcut kontroller
    mitigation_actions TEXT,                   -- Azaltma eylemleri
    responsible_party TEXT,                    -- Sorumlu birim/kişi
    action_deadline TEXT,                      -- Aksiyon son tarihi
    status TEXT DEFAULT 'Identified',          -- Identified, Assessed, Managed, Closed
    
    -- Notlar
    notes TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ============================================================================
-- 4. METRICS AND TARGETS (Metrikler ve Hedefler)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tcfd_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- GHG Emisyonları
    scope1_emissions REAL,                     -- Scope 1 (tonCO2e)
    scope2_emissions REAL,                     -- Scope 2 (tonCO2e)
    scope3_emissions REAL,                     -- Scope 3 (tonCO2e)
    total_emissions REAL,                      -- Toplam emisyon
    
    -- Emisyon Yoğunluğu
    emissions_intensity REAL,                  -- Emisyon yoğunluğu
    intensity_metric TEXT,                     -- Yoğunluk metriği (tonCO2e/milyon TRY ciro, vs.)
    
    -- Enerji
    total_energy_consumption REAL,            -- Toplam enerji (MWh)
    renewable_energy_pct REAL,                -- Yenilenebilir enerji (%)
    energy_intensity REAL,                     -- Enerji yoğunluğu
    
    -- Su
    water_consumption REAL,                    -- Su tüketimi (m3)
    water_intensity REAL,                      -- Su yoğunluğu
    
    -- Karbon Fiyatlama
    internal_carbon_price REAL,                -- Dahili karbon fiyatı ($/tonCO2e)
    carbon_price_coverage REAL,                -- Kapsam (%)
    
    -- Finansal Metrikler
    climate_related_revenue REAL,             -- İklim ilgili gelir (milyon)
    climate_related_opex REAL,                 -- İklim ilgili işletme gideri (milyon)
    climate_related_capex REAL,                -- İklim ilgili yatırım (milyon)
    
    -- Diğer Metrikler (JSON)
    other_metrics TEXT,                        -- Diğer sektöre özel metrikler
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, reporting_year)
);

-- Hedefler
CREATE TABLE IF NOT EXISTS tcfd_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    
    -- Hedef Bilgileri
    target_name TEXT NOT NULL,                 -- Hedef adı
    target_category TEXT,                      -- Kategori (Emissions, Energy, Water, etc.)
    target_type TEXT,                          -- Absolute, Intensity
    
    -- Hedef Değerleri
    baseline_year INTEGER,                     -- Baz yıl
    baseline_value REAL,                       -- Baz değer
    target_year INTEGER,                       -- Hedef yıl
    target_value REAL,                         -- Hedef değer
    reduction_pct REAL,                        -- Azaltma yüzdesi
    
    -- Kapsam
    scope TEXT,                                -- Kapsam (Scope 1, 2, 3, Company-wide, etc.)
    boundary TEXT,                             -- Sınır (Operational, Value chain)
    
    -- İlerleme
    current_value REAL,                        -- Güncel değer
    progress_pct REAL,                         -- İlerleme (%)
    on_track INTEGER DEFAULT 1,                -- Hedefte mi? (0/1)
    
    -- SBTi veya Diğer Onaylar
    sbti_approved INTEGER DEFAULT 0,           -- SBTi onaylı mı?
    external_verification TEXT,                -- Dış doğrulama
    
    -- Açıklama
    description TEXT,
    methodology TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active',              -- Active, Achieved, Revised, Discontinued
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Hedef İlerleme Geçmişi
CREATE TABLE IF NOT EXISTS tcfd_target_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    actual_value REAL NOT NULL,
    progress_pct REAL,
    on_track INTEGER DEFAULT 1,
    notes TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY(target_id) REFERENCES tcfd_targets(id) ON DELETE CASCADE,
    UNIQUE(target_id, reporting_year)
);

-- ============================================================================
-- 5. TCFD RAPORLARI
-- ============================================================================

CREATE TABLE IF NOT EXISTS tcfd_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    reporting_year INTEGER NOT NULL,
    
    -- Rapor Bilgileri
    report_title TEXT,
    report_date TEXT,
    report_status TEXT DEFAULT 'Draft',        -- Draft, Review, Published
    
    -- Executive Summary
    executive_summary TEXT,
    
    -- Dosya Yolları
    pdf_path TEXT,
    docx_path TEXT,
    excel_path TEXT,
    
    -- Metadata
    created_by INTEGER,
    reviewed_by INTEGER,
    approved_by INTEGER,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    published_at TEXT,
    
    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(company_id, reporting_year)
);

-- ============================================================================
-- 6. YARDIMCI TABLOLAR
-- ============================================================================

-- Risk Katalogu Şablonları (varsayılan riskler)
CREATE TABLE IF NOT EXISTS tcfd_risk_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_category TEXT NOT NULL,
    risk_type TEXT NOT NULL,
    risk_name TEXT NOT NULL,
    risk_description TEXT,
    sector TEXT,                               -- All, Finance, Energy, Manufacturing, etc.
    typical_likelihood TEXT,
    typical_impact TEXT,
    example_controls TEXT,
    reference_source TEXT
);

-- Senaryo Şablonları
CREATE TABLE IF NOT EXISTS tcfd_scenario_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL,
    scenario_source TEXT,
    temperature_target REAL,
    time_horizon INTEGER,
    description TEXT,
    assumptions TEXT,
    is_default INTEGER DEFAULT 0
);

-- ============================================================================
-- İNDEKSLER (Performans için)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tcfd_gov_company_year 
    ON tcfd_governance(company_id, reporting_year);

CREATE INDEX IF NOT EXISTS idx_tcfd_risks_company_year 
    ON tcfd_climate_risks(company_id, reporting_year);

CREATE INDEX IF NOT EXISTS idx_tcfd_risks_category 
    ON tcfd_climate_risks(risk_category, risk_type);

CREATE INDEX IF NOT EXISTS idx_tcfd_risks_rating 
    ON tcfd_climate_risks(risk_rating, risk_score);

CREATE INDEX IF NOT EXISTS idx_tcfd_metrics_company_year 
    ON tcfd_metrics(company_id, reporting_year);

CREATE INDEX IF NOT EXISTS idx_tcfd_targets_company 
    ON tcfd_targets(company_id, status);

CREATE INDEX IF NOT EXISTS idx_tcfd_scenarios_company_year 
    ON tcfd_scenarios(company_id, reporting_year);

