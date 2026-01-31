-- TSRS (Türkiye Sürdürülebilirlik Raporlama Standardı) Veritabanı Şeması
-- TSRS Modülü için gerekli tablolar ve ilişkiler

-- TSRS Standartları Ana Tablosu
CREATE TABLE IF NOT EXISTS tsrs_standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL UNIQUE,           -- TSRS-001, TSRS-002, vb.
    title TEXT NOT NULL,                        -- Başlık
    description TEXT,                           -- Açıklama
    category VARCHAR(50) NOT NULL,              -- Yönetişim, Strateji, Risk Yönetimi, Metrikler
    subcategory VARCHAR(100),                   -- Alt kategori
    requirement_level VARCHAR(20) NOT NULL,     -- Zorunlu, Önerilen, İsteğe Bağlı
    reporting_frequency VARCHAR(20),            -- Yıllık, Çeyreklik, vb.
    effective_date DATE,                        -- Yürürlük tarihi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TSRS Göstergeleri Tablosu
CREATE TABLE IF NOT EXISTS tsrs_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    code VARCHAR(20) NOT NULL,                  -- TSRS-001-1, TSRS-001-2, vb.
    title TEXT NOT NULL,                        -- Gösterge başlığı
    description TEXT,                           -- Gösterge açıklaması
    unit VARCHAR(50),                           -- Birim (adet, %, m², vb.)
    methodology TEXT,                           -- Hesaplama metodolojisi
    data_type VARCHAR(20),                      -- Sayısal, Metin, Evet/Hayır
    is_mandatory BOOLEAN DEFAULT 0,             -- Zorunlu mu?
    is_quantitative BOOLEAN DEFAULT 1,          -- Sayısal mı?
    baseline_year INTEGER,                      -- Baz yıl
    target_year INTEGER,                        -- Hedef yıl
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (standard_id) REFERENCES tsrs_standards(id) ON DELETE CASCADE
);

-- TSRS Şirket Yanıtları Tablosu
CREATE TABLE IF NOT EXISTS tsrs_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    indicator_id INTEGER NOT NULL,
    reporting_period VARCHAR(10) NOT NULL,      -- 2024, 2024-Q1, vb.
    response_value TEXT,                        -- Yanıt değeri
    numerical_value DECIMAL(15,4),              -- Sayısal değer
    unit VARCHAR(50),                           -- Birim
    methodology_used TEXT,                      -- Kullanılan metodoloji
    data_source TEXT,                           -- Veri kaynağı
    reporting_status VARCHAR(20) DEFAULT 'Draft', -- Draft, Submitted, Approved
    evidence_url TEXT,                          -- Kanıt URL'i
    notes TEXT,                                 -- Notlar
    submitted_at TIMESTAMP,                     -- Gönderim tarihi
    approved_at TIMESTAMP,                      -- Onay tarihi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES tsrs_indicators(id) ON DELETE CASCADE,
    UNIQUE(company_id, indicator_id, reporting_period)
);

-- TSRS Hedefleri Tablosu
CREATE TABLE IF NOT EXISTS tsrs_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    indicator_id INTEGER NOT NULL,
    target_year INTEGER NOT NULL,
    target_value DECIMAL(15,4),                 -- Hedef değer
    baseline_value DECIMAL(15,4),               -- Baz değer
    unit VARCHAR(50),                           -- Birim
    target_type VARCHAR(20),                    -- Azaltım, Artırım, Koruma
    status VARCHAR(20) DEFAULT 'Active',        -- Active, Achieved, Not Achieved
    notes TEXT,                                 -- Notlar
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES tsrs_indicators(id) ON DELETE CASCADE
);

-- TSRS Risk Değerlendirmesi Tablosu
CREATE TABLE IF NOT EXISTS tsrs_risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    standard_id INTEGER NOT NULL,
    risk_title TEXT NOT NULL,                   -- Risk başlığı
    risk_description TEXT,                      -- Risk açıklaması
    risk_category VARCHAR(50),                  -- Çevresel, Sosyal, Yönetişim
    probability VARCHAR(20),                    -- Düşük, Orta, Yüksek
    impact VARCHAR(20),                         -- Düşük, Orta, Yüksek
    risk_level VARCHAR(20),                     -- Düşük, Orta, Yüksek, Kritik
    mitigation_strategy TEXT,                   -- Azaltım stratejisi
    responsible_person VARCHAR(100),            -- Sorumlu kişi
    target_date DATE,                           -- Hedef tarih
    status VARCHAR(20) DEFAULT 'Open',          -- Open, In Progress, Closed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (standard_id) REFERENCES tsrs_standards(id) ON DELETE CASCADE
);

-- TSRS Paydaş Grupları Tablosu
CREATE TABLE IF NOT EXISTS tsrs_stakeholder_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,                 -- Paydaş grubu adı
    description TEXT,                           -- Açıklama
    engagement_method TEXT,                     -- Katılım yöntemi
    frequency VARCHAR(50),                      -- Sıklık
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TSRS - ESRS Eşleştirme Tablosu
CREATE TABLE IF NOT EXISTS map_tsrs_esrs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tsrs_indicator_id INTEGER NOT NULL,
    esrs_code VARCHAR(20) NOT NULL,             -- E1-1, S1-1, vb.
    relationship_type VARCHAR(20) DEFAULT 'Direct', -- Direct, Partial, Related
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tsrs_indicator_id) REFERENCES tsrs_indicators(id) ON DELETE CASCADE
);

-- TSRS Paydaş Katılımı Tablosu
CREATE TABLE IF NOT EXISTS tsrs_stakeholder_engagement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    stakeholder_group_id INTEGER NOT NULL,
    engagement_date DATE NOT NULL,
    engagement_type VARCHAR(50),                -- Toplantı, Anket, Görüşme
    participants_count INTEGER,                 -- Katılımcı sayısı
    key_topics TEXT,                            -- Ana konular
    outcomes TEXT,                              -- Sonuçlar
    follow_up_actions TEXT,                     -- Takip eylemleri
    next_engagement_date DATE,                  -- Sonraki katılım tarihi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stakeholder_group_id) REFERENCES tsrs_stakeholder_groups(id) ON DELETE CASCADE
);

-- TSRS-GRI Eşleştirmeleri Tablosu
CREATE TABLE IF NOT EXISTS map_tsrs_gri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tsrs_standard_code VARCHAR(20) NOT NULL,
    tsrs_indicator_code VARCHAR(20),
    gri_standard VARCHAR(20) NOT NULL,
    gri_disclosure VARCHAR(20),
    relationship_type VARCHAR(20) DEFAULT 'Related', -- Related, Equivalent, Complementary
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tsrs_standard_code) REFERENCES tsrs_standards(code),
    FOREIGN KEY (gri_standard) REFERENCES gri_standards(code)
);

-- TSRS-SDG Eşleştirmeleri Tablosu
CREATE TABLE IF NOT EXISTS map_tsrs_sdg (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tsrs_standard_code VARCHAR(20) NOT NULL,
    tsrs_indicator_code VARCHAR(20),
    sdg_goal_id INTEGER NOT NULL,
    sdg_target_id INTEGER,
    sdg_indicator_code VARCHAR(20),
    relationship_type VARCHAR(20) DEFAULT 'Related', -- Related, Direct, Indirect
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tsrs_standard_code) REFERENCES tsrs_standards(code),
    FOREIGN KEY (sdg_goal_id) REFERENCES sdg_goals(id)
);

-- TSRS Raporlama Şablonları Tablosu
CREATE TABLE IF NOT EXISTS tsrs_report_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,                 -- Şablon adı
    description TEXT,                           -- Açıklama
    template_type VARCHAR(20) NOT NULL,         -- Annual, Quarterly, Thematic
    sectors TEXT,                               -- Hedeflenen sektörler
    mandatory_standards TEXT,                   -- Zorunlu standartlar
    optional_standards TEXT,                    -- İsteğe bağlı standartlar
    template_content TEXT,                      -- Şablon içeriği (JSON)
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TSRS Raporları Tablosu
CREATE TABLE IF NOT EXISTS tsrs_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    reporting_period VARCHAR(10) NOT NULL,      -- 2024, 2024-Q1, vb.
    report_title VARCHAR(200) NOT NULL,         -- Rapor başlığı
    report_status VARCHAR(20) DEFAULT 'Draft',  -- Draft, Submitted, Approved, Published
    cover_period_start DATE,                    -- Kapsam başlangıç tarihi
    cover_period_end DATE,                      -- Kapsam bitiş tarihi
    assurance_type VARCHAR(20),                 -- Internal, External, None
    assurance_provider VARCHAR(100),            -- Güvence sağlayıcı
    report_url TEXT,                            -- Rapor URL'i
    file_path TEXT,                             -- Dosya yolu
    file_size INTEGER,                          -- Dosya boyutu
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,                     -- Yayın tarihi
    FOREIGN KEY (template_id) REFERENCES tsrs_report_templates(id)
);

-- TSRS KPI'ları Tablosu
CREATE TABLE IF NOT EXISTS tsrs_kpis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_id INTEGER NOT NULL,
    kpi_name VARCHAR(100) NOT NULL,             -- KPI adı
    kpi_description TEXT,                       -- KPI açıklaması
    formula TEXT,                               -- Hesaplama formülü
    unit VARCHAR(50),                           -- Birim
    frequency VARCHAR(20),                      -- Hesaplama sıklığı
    owner VARCHAR(100),                         -- Sorumlu
    data_source TEXT,                           -- Veri kaynağı
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_id) REFERENCES tsrs_indicators(id) ON DELETE CASCADE
);

-- TSRS Performans Verileri Tablosu
CREATE TABLE IF NOT EXISTS tsrs_performance_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    kpi_id INTEGER NOT NULL,
    reporting_period VARCHAR(10) NOT NULL,
    actual_value DECIMAL(15,4),                 -- Gerçekleşen değer
    target_value DECIMAL(15,4),                 -- Hedef değer
    previous_value DECIMAL(15,4),               -- Önceki dönem değeri
    variance_percentage DECIMAL(5,2),           -- Sapma yüzdesi
    trend VARCHAR(20),                          -- Artış, Azalış, Sabit
    notes TEXT,                                 -- Notlar
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kpi_id) REFERENCES tsrs_kpis(id) ON DELETE CASCADE,
    UNIQUE(company_id, kpi_id, reporting_period)
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_tsrs_standards_category ON tsrs_standards(category);
CREATE INDEX IF NOT EXISTS idx_tsrs_standards_requirement ON tsrs_standards(requirement_level);
CREATE INDEX IF NOT EXISTS idx_tsrs_indicators_standard ON tsrs_indicators(standard_id);
CREATE INDEX IF NOT EXISTS idx_tsrs_indicators_mandatory ON tsrs_indicators(is_mandatory);
CREATE INDEX IF NOT EXISTS idx_tsrs_responses_company ON tsrs_responses(company_id);
CREATE INDEX IF NOT EXISTS idx_tsrs_responses_period ON tsrs_responses(reporting_period);
CREATE INDEX IF NOT EXISTS idx_tsrs_targets_company ON tsrs_targets(company_id);
CREATE INDEX IF NOT EXISTS idx_tsrs_risks_company ON tsrs_risks(company_id);
CREATE INDEX IF NOT EXISTS idx_tsrs_risks_level ON tsrs_risks(risk_level);
CREATE INDEX IF NOT EXISTS idx_map_tsrs_gri_tsrs ON map_tsrs_gri(tsrs_standard_code);
CREATE INDEX IF NOT EXISTS idx_map_tsrs_gri_gri ON map_tsrs_gri(gri_standard);
CREATE INDEX IF NOT EXISTS idx_map_tsrs_sdg_tsrs ON map_tsrs_sdg(tsrs_standard_code);
CREATE INDEX IF NOT EXISTS idx_map_tsrs_sdg_sdg ON map_tsrs_sdg(sdg_goal_id);
