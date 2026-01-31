-- SASB (Sustainability Accounting Standards Board) Veritabanı Şeması
-- 77 sektör standardı ve disclosure topics

-- SASB Sektörleri (77 sektör)
CREATE TABLE IF NOT EXISTS sasb_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code TEXT NOT NULL UNIQUE,      -- Örn: TC-SI, HC-BP
    sector_name TEXT NOT NULL,             -- Örn: Software & IT Services, Biotechnology & Pharmaceuticals
    industry_group TEXT NOT NULL,          -- Örn: Technology & Communications, Healthcare
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- SASB Disclosure Topics (Her sektör için materyal konular)
CREATE TABLE IF NOT EXISTS sasb_disclosure_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id INTEGER NOT NULL,
    topic_code TEXT NOT NULL,              -- Örn: GHG-EM, DATA-SEC
    topic_name TEXT NOT NULL,              -- Örn: GHG Emissions, Data Security
    category TEXT,                         -- Environment, Social Capital, Human Capital, Business Model, Leadership
    is_material INTEGER DEFAULT 1,         -- Bu sektör için materyal mi?
    description TEXT,
    FOREIGN KEY (sector_id) REFERENCES sasb_sectors(id) ON DELETE CASCADE
);

-- SASB Metrikleri (Her topic için ölçülebilir metrikler)
CREATE TABLE IF NOT EXISTS sasb_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disclosure_topic_id INTEGER NOT NULL,
    metric_code TEXT NOT NULL,             -- Örn: TC-SI-130a.1
    metric_name TEXT NOT NULL,
    metric_type TEXT,                      -- Quantitative, Qualitative, Discussion
    unit TEXT,                             -- tonCO2e, %, number, etc.
    description TEXT,
    reporting_guidance TEXT,               -- Nasıl raporlanacağı
    FOREIGN KEY (disclosure_topic_id) REFERENCES sasb_disclosure_topics(id) ON DELETE CASCADE
);

-- Şirket SASB Verileri
CREATE TABLE IF NOT EXISTS company_sasb_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    sector_id INTEGER NOT NULL,            -- Şirketin sektörü
    disclosure_status TEXT DEFAULT 'draft', -- draft, in_progress, completed
    completion_percentage REAL DEFAULT 0,  -- %
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (sector_id) REFERENCES sasb_sectors(id) ON DELETE CASCADE,
    UNIQUE(company_id, year, sector_id)
);

-- SASB Metrik Yanıtları
CREATE TABLE IF NOT EXISTS sasb_metric_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    metric_id INTEGER NOT NULL,
    response_value TEXT,                   -- Yanıt (metin veya sayı)
    numerical_value REAL,                  -- Sayısal değer (varsa)
    unit TEXT,                             -- Birim
    data_quality TEXT,                     -- High, Medium, Low
    evidence_url TEXT,                     -- Kanıt belgesi
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES sasb_metrics(id) ON DELETE CASCADE
);

-- SASB-GRI Mapping (Hangi SASB metriği hangi GRI göstergesine karşılık gelir)
CREATE TABLE IF NOT EXISTS sasb_gri_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sasb_metric_code TEXT NOT NULL,
    gri_standard TEXT,                     -- Örn: GRI 305
    gri_disclosure TEXT,                   -- Örn: 305-1
    mapping_strength TEXT,                 -- Strong, Moderate, Weak
    notes TEXT
);

-- SASB Finansal Materiality Değerlendirmesi
CREATE TABLE IF NOT EXISTS sasb_financial_materiality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    disclosure_topic_id INTEGER NOT NULL,
    financial_impact_score INTEGER,        -- 1-5 skala
    likelihood_score INTEGER,              -- 1-5 skala
    time_horizon TEXT,                     -- Short-term, Medium-term, Long-term
    revenue_impact REAL,                   -- Potansiyel gelir etkisi ($)
    cost_impact REAL,                      -- Potansiyel maliyet etkisi ($)
    risk_opportunity TEXT,                 -- Risk or Opportunity
    notes TEXT,
    assessed_by TEXT,
    assessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (disclosure_topic_id) REFERENCES sasb_disclosure_topics(id) ON DELETE CASCADE
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_sasb_sectors_code ON sasb_sectors(sector_code);
CREATE INDEX IF NOT EXISTS idx_sasb_metrics_code ON sasb_metrics(metric_code);
CREATE INDEX IF NOT EXISTS idx_company_sasb_data ON company_sasb_data(company_id, year);
CREATE INDEX IF NOT EXISTS idx_sasb_responses ON sasb_metric_responses(company_id, year, metric_id);
