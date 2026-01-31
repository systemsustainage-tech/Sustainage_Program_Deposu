--- Table: advanced_report_categories ---
CREATE TABLE advanced_report_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    icon VARCHAR(20),
                    color VARCHAR(20),
                    is_active BOOLEAN DEFAULT 1
                );

--- Table: advanced_report_distributions ---
CREATE TABLE advanced_report_distributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    recipient_email VARCHAR(255),
                    recipient_name VARCHAR(100),
                    distribution_method VARCHAR(20),
                    sent_at TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'Pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    company_id INTEGER,
                    distribution_name VARCHAR(100),
                    recipient_type VARCHAR(20),
                    distribution_status VARCHAR(20),
                    updated_at TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                );

--- Table: advanced_report_metrics ---
CREATE TABLE advanced_report_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value DECIMAL(15,4),
                    metric_unit VARCHAR(50),
                    metric_type VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                );

--- Table: advanced_report_schedules ---
CREATE TABLE advanced_report_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    schedule_name VARCHAR(100) NOT NULL,
                    frequency VARCHAR(20) NOT NULL,
                    frequency_value INTEGER,
                    start_date DATE,
                    end_date DATE,
                    time_of_day TIME,
                    recipients TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP,
                    deleted_at TIMESTAMP,
                    company_id INTEGER,
                    FOREIGN KEY (template_id) REFERENCES advanced_report_templates(id)
                );

--- Table: advanced_report_templates ---
CREATE TABLE advanced_report_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    template_type VARCHAR(20) NOT NULL,
                    data_source VARCHAR(100),
                    template_config TEXT,
                    output_formats TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: app_settings ---
CREATE TABLE app_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: audit_assignments ---
CREATE TABLE audit_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    auditor_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    assignment_type TEXT NOT NULL,
                    scope TEXT,
                    start_date DATE NOT NULL,
                    deadline DATE NOT NULL,
                    status TEXT DEFAULT 'assigned',
                    priority TEXT DEFAULT 'orta',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (auditor_id) REFERENCES auditors(id)
                );

--- Table: audit_findings ---
CREATE TABLE audit_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    finding_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    finding_title TEXT NOT NULL,
                    finding_description TEXT,
                    affected_module TEXT,
                    affected_data TEXT,
                    recommendation TEXT,
                    status TEXT DEFAULT 'open',
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (assignment_id) REFERENCES audit_assignments(id),
                    FOREIGN KEY (created_by) REFERENCES auditors(id)
                );

--- Table: audit_logs ---
CREATE TABLE audit_logs (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  action TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP, resource_type VARCHAR(50), resource_id INTEGER, ip_address VARCHAR(45), user_agent TEXT, old_values TEXT, new_values TEXT, username VARCHAR(50), timestamp TEXT, module_name TEXT,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

--- Table: audit_reports ---
CREATE TABLE audit_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    report_title TEXT NOT NULL,
                    report_period TEXT,
                    file_path TEXT,
                    summary TEXT,
                    total_findings INTEGER DEFAULT 0,
                    critical_findings INTEGER DEFAULT 0,
                    overall_opinion TEXT,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (assignment_id) REFERENCES audit_assignments(id),
                    FOREIGN KEY (created_by) REFERENCES auditors(id)
                );

--- Table: auditors ---
CREATE TABLE auditors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    auditor_role TEXT NOT NULL,
                    organization TEXT,
                    certification TEXT,
                    certification_number TEXT,
                    valid_until DATE,
                    specialization TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: auto_task_logs ---
CREATE TABLE auto_task_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    selection_type TEXT NOT NULL, -- 'SDG', 'GRI', 'TSRS'
                    selected_items TEXT NOT NULL, -- JSON array
                    tasks_created INTEGER DEFAULT 0,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: auto_tasks ---
CREATE TABLE auto_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    user_id INTEGER,
                    task_name TEXT NOT NULL,
                    task_description TEXT,
                    task_type TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'Açık',
                    due_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: benchmark_metrics ---
CREATE TABLE benchmark_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_code TEXT UNIQUE NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_category TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    description TEXT,
                    calculation_method TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: best_performers ---
CREATE TABLE best_performers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector_code TEXT NOT NULL,
                    metric_code TEXT NOT NULL,
                    performer_name TEXT,
                    performer_value REAL NOT NULL,
                    performance_description TEXT,
                    data_year INTEGER NOT NULL,
                    rank INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sector_code, metric_code, data_year, rank)
                );

--- Table: brand_identity ---
CREATE TABLE brand_identity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER UNIQUE NOT NULL,
                    company_name TEXT,
                    logo_path TEXT,
                    logo_width INTEGER DEFAULT 200,
                    logo_height INTEGER DEFAULT 100,
                    color_primary TEXT DEFAULT '#2c3e50',
                    color_secondary TEXT DEFAULT '#3498db',
                    color_accent TEXT DEFAULT '#27ae60',
                    font_heading TEXT DEFAULT 'Arial',
                    font_body TEXT DEFAULT 'Arial',
                    report_header_text TEXT,
                    report_footer_text TEXT,
                    watermark_text TEXT,
                    custom_styles TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: business_continuity_plans ---
CREATE TABLE business_continuity_plans (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                plan_type TEXT, -- Genel, Departman, Kritik Süreç
                description TEXT,
                version TEXT,
                approval_date TEXT,
                review_date TEXT,
                status TEXT DEFAULT 'active', -- active, draft, archived
                critical_processes TEXT, -- Kritik süreçler (JSON)
                backup_procedures TEXT, -- Yedekleme prosedürleri
                communication_protocols TEXT, -- İletişim protokolleri
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: business_impact_assessments ---
CREATE TABLE business_impact_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    financial_impact REAL NOT NULL,
                    operational_impact REAL NOT NULL,
                    reputational_impact REAL NOT NULL,
                    regulatory_impact REAL NOT NULL,
                    total_impact REAL NOT NULL,
                    assessment_method TEXT,
                    confidence_level TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                );

--- Table: calculation_details ---
CREATE TABLE calculation_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    calculation_formula TEXT NOT NULL,
                    input_parameters TEXT NOT NULL,
                    constants_used TEXT,
                    calculation_steps TEXT,
                    result_value TEXT,
                    result_unit TEXT,
                    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    calculated_by INTEGER,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                );

--- Table: carbon_emissions ---
CREATE TABLE carbon_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scope INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    emission_factor REAL,
                    co2e_kg REAL NOT NULL,
                    period_start TEXT,
                    period_end TEXT,
                    description TEXT,
                    source TEXT,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: carbon_reduction_initiatives ---
CREATE TABLE carbon_reduction_initiatives (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    initiative_description TEXT,
                    initiative_type TEXT,                -- energy_efficiency, renewable, process_change, etc.
                    target_scope TEXT,                   -- scope1, scope2, scope3
                    start_date DATE,
                    end_date DATE,
                    investment_amount REAL,              -- Yatırım tutarı
                    expected_reduction_co2e REAL,        -- Beklenen azaltma (tCO2e/yıl)
                    actual_reduction_co2e REAL,          -- Gerçekleşen azaltma
                    status TEXT DEFAULT 'planned',       -- planned, ongoing, completed, cancelled
                    roi_years REAL,                      -- Return on Investment (yıl)
                    sdg_alignment TEXT,                  -- İlgili SDG'ler (JSON)
                    responsible_person TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: carbon_reports ---
CREATE TABLE carbon_reports (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT,                    -- annual, quarterly, verification
                    scope1_total REAL,
                    scope2_total REAL,
                    scope3_total REAL,
                    total_co2e REAL NOT NULL,
                    boundary_description TEXT,           -- Organizational boundary
                    base_year INTEGER,
                    reporting_standard TEXT DEFAULT 'GHG Protocol',
                    verification_status TEXT,            -- unverified, third_party, internal
                    verifier_name TEXT,
                    verification_date DATE,
                    report_file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: carbon_summary ---
CREATE TABLE carbon_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    scope1_total REAL DEFAULT 0,
                    scope2_total REAL DEFAULT 0,
                    scope3_total REAL DEFAULT 0,
                    total_emissions REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, year)
                );

--- Table: carbon_targets ---
CREATE TABLE carbon_targets (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    target_name TEXT NOT NULL,
                    target_description TEXT,
                    scope_coverage TEXT NOT NULL,        -- scope1, scope1_2, scope1_2_3
                    baseline_year INTEGER NOT NULL,
                    baseline_co2e REAL NOT NULL,         -- Baz yıl emisyonu
                    target_year INTEGER NOT NULL,
                    target_co2e REAL NOT NULL,           -- Hedef emisyon
                    target_reduction_pct REAL,           -- Hedef azaltma %
                    target_type TEXT,                    -- absolute, intensity
                    intensity_metric TEXT,               -- revenue, employee, production
                    commitment_level TEXT,               -- committed, aspirational
                    sbti_approved BOOLEAN DEFAULT 0,     -- Science Based Target Initiative
                    status TEXT DEFAULT 'active',        -- active, achieved, missed, revised
                    progress_pct REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: cbam_emissions ---
CREATE TABLE cbam_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    reporting_period VARCHAR(20),
                    emission_type VARCHAR(50),
                    direct_emissions DECIMAL(15,4),
                    indirect_emissions DECIMAL(15,4),
                    embedded_emissions DECIMAL(15,4),
                    total_emissions DECIMAL(15,4),
                    emission_factor DECIMAL(10,6),
                    calculation_method VARCHAR(100),
                    data_quality VARCHAR(50),
                    verification_status VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES cbam_products(id)
                );

--- Table: cbam_factors ---
CREATE TABLE cbam_factors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  period INTEGER NOT NULL UNIQUE,
  eu_ets_price_eur_per_tco2 REAL NOT NULL,
  default_leakage_factor REAL DEFAULT 0,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

--- Table: cbam_imports ---
CREATE TABLE cbam_imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    import_period VARCHAR(20),
                    origin_country VARCHAR(100),
                    quantity DECIMAL(15,4),
                    quantity_unit VARCHAR(20),
                    customs_value DECIMAL(15,2),
                    currency VARCHAR(10),
                    embedded_emissions DECIMAL(15,4),
                    carbon_price_paid DECIMAL(15,2),
                    cbam_certificate_required BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (product_id) REFERENCES cbam_products(id)
                );

--- Table: cbam_innovation_links ---
CREATE TABLE cbam_innovation_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id INTEGER NOT NULL,
  period INTEGER NOT NULL,
  product_code TEXT NOT NULL,
  innovation_share_ratio REAL DEFAULT 0,
  attenuation_factor REAL DEFAULT 0.6,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(company_id, period, product_code),
  FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

--- Table: cbam_products ---
CREATE TABLE cbam_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    product_code VARCHAR(50) NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    hs_code VARCHAR(20),
                    cn_code VARCHAR(20),
                    sector VARCHAR(50),
                    production_route VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, period INTEGER DEFAULT 2024, trade_volume_tons REAL DEFAULT 0, baseline_emission_intensity REAL DEFAULT 0, post_innovation_emission_intensity REAL DEFAULT 0, domestic_carbon_price_eur_per_tco2 REAL DEFAULT 0, importing_region TEXT DEFAULT EU,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: cbam_registration ---
CREATE TABLE cbam_registration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                registration_number VARCHAR(50),
                status VARCHAR(50),
                registration_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: cbam_reports ---
CREATE TABLE cbam_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_period VARCHAR(20),
                    report_type VARCHAR(50),
                    total_imports DECIMAL(15,4),
                    total_emissions DECIMAL(15,4),
                    total_cbam_liability DECIMAL(15,2),
                    report_status VARCHAR(50),
                    submitted_at TIMESTAMP,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: cdp_climate_change ---
CREATE TABLE cdp_climate_change (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                );

--- Table: cdp_forests ---
CREATE TABLE cdp_forests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                );

--- Table: cdp_question_categories ---
CREATE TABLE cdp_question_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    questionnaire_type TEXT NOT NULL,
                    category_code TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    category_description TEXT,
                    weight REAL DEFAULT 1.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: cdp_questions ---
CREATE TABLE cdp_questions (
            id INTEGER PRIMARY KEY,
            category TEXT,
            question_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: cdp_responses ---
CREATE TABLE cdp_responses (
            id INTEGER PRIMARY KEY,
            company_id INTEGER,
            question_id INTEGER,
            response_text TEXT,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: cdp_scoring ---
CREATE TABLE cdp_scoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    questionnaire_type TEXT NOT NULL,
                    total_score REAL DEFAULT 0.0,
                    grade TEXT DEFAULT 'D',
                    disclosure_score REAL DEFAULT 0.0,
                    awareness_score REAL DEFAULT 0.0,
                    management_score REAL DEFAULT 0.0,
                    leadership_score REAL DEFAULT 0.0,
                    submission_date TIMESTAMP,
                    verification_date TIMESTAMP,
                    status TEXT DEFAULT 'Draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, questionnaire_type)
                );

--- Table: cdp_water_security ---
CREATE TABLE cdp_water_security (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                );

--- Table: ceo_messages ---
CREATE TABLE ceo_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message_type TEXT NOT NULL, -- 'annual', 'quarterly', 'sustainability', 'emergency'
                    year INTEGER NOT NULL,
                    quarter INTEGER, -- 1-4, NULL for annual
                    content TEXT NOT NULL,
                    key_achievements TEXT, -- JSON array
                    challenges TEXT, -- JSON array
                    future_commitments TEXT, -- JSON array
                    signature_name TEXT,
                    signature_title TEXT,
                    signature_date TEXT,
                    is_published INTEGER DEFAULT 0,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                );

--- Table: companies ---
CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  sector TEXT,
  country TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
, is_active INTEGER DEFAULT 1);

--- Table: company_benchmarks ---
CREATE TABLE company_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    sector_code TEXT NOT NULL,
                    metric_code TEXT NOT NULL,
                    company_value REAL NOT NULL,
                    sector_average REAL NOT NULL,
                    percentile REAL,
                    performance_level TEXT,
                    gap_to_average REAL,
                    gap_to_best REAL,
                    comparison_year INTEGER NOT NULL,
                    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, metric_code, comparison_year)
                );

--- Table: company_info ---
CREATE TABLE company_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER UNIQUE,
                sirket_adi TEXT,
                ticari_unvan TEXT,
                marka_isimleri TEXT,
                adres TEXT,
                ulke TEXT,
                sehir TEXT,
                posta_kodu TEXT,
                web TEXT,
                eposta TEXT,
                telefon TEXT,
                vergi_no TEXT,
                mersis_no TEXT,
                tuzel_yapi TEXT,
                mulkiyet_kontrol TEXT,
                borsa_durumu TEXT,
                kayitli_merkez TEXT,
                calisan_sayisi TEXT,
                calisan_cinsiyet_dagilimi TEXT,
                operasyon_sayisi TEXT,
                faaliyet_lokasyonlari TEXT,
                net_gelir TEXT,
                toplam_varliklar TEXT,
                pazarlar TEXT,
                tedarik_zinciri TEXT,
                is_iliskileri TEXT,
                upstream_downstream TEXT,
                yonetim_yapisi TEXT,
                en_yuksek_yonetim_organi TEXT,
                baskan_bilgisi TEXT,
                surdurulebilirlik_sorumluluklari TEXT,
                risk_yonetimi_rolu TEXT,
                cikar_catismalari TEXT,
                kritik_endise_iletisimi TEXT,
                yonetim_bilgisi_kapasitesi TEXT,
                performans_degerlendirme TEXT,
                ucret_politikalari TEXT,
                ucret_belirleme_sureci TEXT,
                yillik_ucret_orani TEXT,
                ust_duzey_beyan TEXT,
                politika_taahhutleri TEXT,
                politikalarin_yayilmasi TEXT,
                olumsuz_etki_tazmin TEXT,
                etik_endise_mekanizmalari TEXT,
                mevzuat_uyum TEXT,
                uyelik_dernekler TEXT,
                paydas_iletisim TEXT,
                toplu_sozlesme_orani TEXT,
                raporlama_donemi TEXT,
                raporlama_dongusu TEXT,
                irtibat_noktasi TEXT
            , vergi_dairesi TEXT, il TEXT, ilce TEXT, email TEXT, website TEXT, sektor TEXT, kurulusyili INTEGER, logo_path TEXT, aktif BOOLEAN DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

--- Table: company_kpis ---
CREATE TABLE company_kpis (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER, year INTEGER, category TEXT, kpi_code TEXT, kpi_name TEXT, value REAL, unit TEXT);

--- Table: company_modules ---
CREATE TABLE company_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_id INTEGER NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                FOREIGN KEY (module_id) REFERENCES modules (id)
            );

--- Table: company_policies ---
CREATE TABLE company_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    template_id INTEGER,
                    policy_name VARCHAR(255) NOT NULL,
                    policy_code VARCHAR(50),
                    category_id INTEGER,
                    content TEXT,
                    version VARCHAR(20),
                    status VARCHAR(50) DEFAULT 'Draft',
                    approval_date DATE,
                    approved_by VARCHAR(100),
                    review_date DATE,
                    file_path VARCHAR(500),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (template_id) REFERENCES policy_templates(id),
                    FOREIGN KEY (category_id) REFERENCES policy_categories(id)
                );

--- Table: company_profiles ---
CREATE TABLE company_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    sector TEXT,
                    logo_path TEXT,
                    logo_width INTEGER DEFAULT 200,
                    logo_height INTEGER DEFAULT 100,
                    primary_color TEXT DEFAULT '#1976D2',
                    secondary_color TEXT DEFAULT '#388E3C',
                    contact_email TEXT,
                    contact_phone TEXT,
                    address TEXT,
                    website TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: company_sasb_data ---
CREATE TABLE company_sasb_data (
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

--- Table: company_taxonomy_activities ---
CREATE TABLE company_taxonomy_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    activity_id INTEGER NOT NULL,
                    period VARCHAR(10),
                    revenue_share DECIMAL(5,2),
                    capex_share DECIMAL(5,2),
                    opex_share DECIMAL(5,2),
                    is_eligible BOOLEAN DEFAULT 0,
                    is_aligned BOOLEAN DEFAULT 0,
                    alignment_status VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (activity_id) REFERENCES eu_taxonomy_activities(id)
                );

--- Table: compliance_matrix ---
CREATE TABLE compliance_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_id INTEGER NOT NULL,
                    requirement VARCHAR(255) NOT NULL,
                    module_name VARCHAR(100),
                    metric_name VARCHAR(255),
                    target_value VARCHAR(100),
                    current_value VARCHAR(100),
                    compliance_status VARCHAR(50),
                    gap_analysis TEXT,
                    action_plan TEXT,
                    responsible_person VARCHAR(100),
                    due_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                );

--- Table: csrd_compliance_checklist ---
CREATE TABLE csrd_compliance_checklist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    requirement_category TEXT NOT NULL,
                    requirement_code TEXT NOT NULL,
                    requirement_description TEXT NOT NULL,
                    requirement_level TEXT DEFAULT 'zorunlu',
                    compliance_status TEXT DEFAULT 'baslanmadi',
                    evidence_reference TEXT,
                    responsible_person TEXT,
                    due_date DATE,
                    completed_date DATE,
                    notes TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: csrd_report_exports ---
CREATE TABLE csrd_report_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    export_type TEXT NOT NULL,
                    report_format TEXT NOT NULL,
                    reporting_period TEXT,
                    file_path TEXT,
                    export_status TEXT DEFAULT 'basarili',
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: custom_emission_factors ---
CREATE TABLE custom_emission_factors (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    scope TEXT NOT NULL,             -- scope1, scope2, scope3
                    category TEXT NOT NULL,          -- stationary, mobile, etc.
                    fuel_type TEXT NOT NULL,
                    factor_co2 REAL,
                    factor_ch4 REAL,
                    factor_n2o REAL,
                    factor_co2e REAL,
                    unit TEXT,
                    source TEXT,
                    valid_from DATE,
                    valid_until DATE,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: custom_mappings ---
CREATE TABLE custom_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    source_standard TEXT NOT NULL,
                    source_code TEXT NOT NULL,
                    target_standard TEXT NOT NULL,
                    target_code TEXT NOT NULL,
                    mapping_rationale TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                );

--- Table: custom_water_factors ---
CREATE TABLE custom_water_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factor_type TEXT NOT NULL,              -- blue_water, green_water, grey_water
                    water_source TEXT NOT NULL,             -- groundwater, surface_water, etc.
                    factor_name TEXT NOT NULL,
                    factor_value REAL NOT NULL,
                    unit TEXT NOT NULL,                     -- m3/m3, m3/kg, etc.
                    reference TEXT,                         -- Kaynak/standart
                    region TEXT,                            -- Bölgesel faktörler
                    validity_start DATE,
                    validity_end DATE,
                    is_active INTEGER DEFAULT 1,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: customer_surveys ---
CREATE TABLE customer_surveys (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            survey_name TEXT NOT NULL,
            survey_type TEXT, -- NPS, CSAT, CES
            survey_date TEXT,
            total_responses INTEGER DEFAULT 0,
            average_score REAL,
            promoter_percentage REAL, -- NPS için
            detractor_percentage REAL, -- NPS için
            passive_percentage REAL, -- NPS için
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: cybersecurity_incidents ---
CREATE TABLE cybersecurity_incidents (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                incident_type TEXT NOT NULL, -- Malware, Phishing, DDoS, Data Breach
                severity TEXT NOT NULL, -- Low, Medium, High, Critical
                description TEXT,
                incident_date TEXT,
                resolution_date TEXT,
                impact_assessment TEXT,
                response_time_hours REAL,
                financial_impact REAL,
                lessons_learned TEXT,
                prevention_measures TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: cybersecurity_trainings ---
CREATE TABLE cybersecurity_trainings (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                training_name TEXT NOT NULL,
                training_type TEXT, -- Awareness, Technical, Management
                participants_count INTEGER DEFAULT 0,
                training_hours REAL,
                completion_rate REAL, -- Tamamlanma oranı (%)
                effectiveness_score REAL, -- Etkinlik skoru (1-10)
                training_date TEXT,
                trainer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: data_assumptions ---
CREATE TABLE data_assumptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    assumption_type TEXT NOT NULL,
                    assumption_description TEXT NOT NULL,
                    justification TEXT,
                    impact_level TEXT DEFAULT 'medium',
                    alternative_scenarios TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                );

--- Table: data_change_audit_trail ---
CREATE TABLE data_change_audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_type TEXT NOT NULL,
                    change_reason TEXT,
                    changed_by INTEGER,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    session_id TEXT,
                    FOREIGN KEY (changed_by) REFERENCES users(id)
                );

--- Table: data_collection_methodology ---
CREATE TABLE data_collection_methodology (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    method_type TEXT NOT NULL,
                    method_description TEXT NOT NULL,
                    measurement_unit TEXT,
                    frequency TEXT,
                    sample_size INTEGER,
                    confidence_level REAL,
                    limitations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                );

--- Table: data_imports ---
CREATE TABLE data_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                import_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT,
                status TEXT DEFAULT 'pending',
                total_rows INTEGER DEFAULT 0,
                successful_rows INTEGER DEFAULT 0,
                failed_rows INTEGER DEFAULT 0,
                error_log TEXT,
                imported_by INTEGER,
                imported_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: data_ownership ---
CREATE TABLE data_ownership (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_category TEXT NOT NULL,
                    primary_owner_id INTEGER NOT NULL,
                    backup_owner_id INTEGER,
                    responsibilities TEXT,
                    last_review_date DATE,
                    next_review_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (primary_owner_id) REFERENCES users(id),
                    FOREIGN KEY (backup_owner_id) REFERENCES users(id)
                );

--- Table: data_quality_scores ---
CREATE TABLE data_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                quality_score REAL DEFAULT 0,
                total_records INTEGER DEFAULT 0,
                valid_records INTEGER DEFAULT 0,
                warning_records INTEGER DEFAULT 0,
                error_records INTEGER DEFAULT 0,
                calculated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: data_sources ---
CREATE TABLE data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_type TEXT NOT NULL,
                    data_identifier TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT,
                    source_document_path TEXT,
                    collection_date DATE,
                    data_owner_id INTEGER,
                    data_quality_level TEXT DEFAULT 'unverified',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_owner_id) REFERENCES users(id)
                );

--- Table: data_verification_records ---
CREATE TABLE data_verification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    verified_by INTEGER NOT NULL,
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_method TEXT,
                    verification_result TEXT DEFAULT 'approved',
                    verification_notes TEXT,
                    evidence_document_path TEXT,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id),
                    FOREIGN KEY (verified_by) REFERENCES users(id)
                );

--- Table: department_users ---
CREATE TABLE department_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    department TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'member', -- 'head', 'member', 'coordinator'
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: departments ---
CREATE TABLE departments (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          parent_department_id INTEGER,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP, code VARCHAR(50), description TEXT, is_active BOOLEAN DEFAULT 1, manager_id INTEGER, updated_at TEXT, created_by INTEGER, updated_by INTEGER,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
          FOREIGN KEY(parent_department_id) REFERENCES departments(id) ON DELETE SET NULL,
          UNIQUE(company_id, name)
        );

--- Table: digital_security_metrics ---
CREATE TABLE digital_security_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            iso27001_certified BOOLEAN DEFAULT 0, -- ISO 27001 sertifikası
            cybersecurity_training_hours REAL, -- Siber güvenlik eğitim saatleri
            data_breach_count INTEGER DEFAULT 0, -- Veri ihlali sayısı
            data_breach_severity TEXT, -- Düşük, Orta, Yüksek, Kritik
            digital_transformation_budget REAL, -- Dijital dönüşüm bütçesi
            ai_applications_count INTEGER DEFAULT 0, -- AI uygulama sayısı
            cloud_adoption_percentage REAL, -- Bulut kullanım oranı (%)
            automation_percentage REAL, -- Otomasyon oranı (%)
            digital_literacy_score REAL, -- Dijital okuryazarlık skoru (1-10)
            cybersecurity_incidents INTEGER DEFAULT 0, -- Siber güvenlik olayları
            incident_response_time REAL, -- Olay müdahale süresi (saat)
            backup_frequency TEXT, -- Yedekleme sıklığı
            disaster_recovery_plan BOOLEAN DEFAULT 0, -- Afet kurtarma planı
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, reporting_period TEXT, created_date TEXT, digital_transformation_score REAL,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: digital_signatures ---
CREATE TABLE digital_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    signer_id INTEGER NOT NULL,
                    signer_role TEXT NOT NULL,
                    signature_hash TEXT NOT NULL,
                    signature_type TEXT DEFAULT 'approval',
                    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    remarks TEXT,
                    FOREIGN KEY (document_id) REFERENCES evidence_documents(id),
                    FOREIGN KEY (signer_id) REFERENCES users(id)
                );

--- Table: digital_transformation_projects ---
CREATE TABLE digital_transformation_projects (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                project_type TEXT, -- AI, IoT, Cloud, Automation, Blockchain
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                status TEXT DEFAULT 'active', -- active, completed, cancelled
                roi_percentage REAL, -- Yatırım getirisi (%)
                digital_maturity_level TEXT, -- Başlangıç, Gelişen, Olgun, Lider
                sdg_mapping TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: distribution_lists ---
CREATE TABLE distribution_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    list_name TEXT NOT NULL,
                    description TEXT,
                    recipients TEXT NOT NULL,
                    cc_recipients TEXT,
                    bcc_recipients TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: double_materiality_assessment ---
CREATE TABLE double_materiality_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    impact_materiality_score REAL,
                    financial_materiality_score REAL,
                    double_materiality_level TEXT NOT NULL,
                    esrs_relevance TEXT,
                    stakeholder_impact TEXT,
                    business_impact TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: economic_value_distribution ---
CREATE TABLE economic_value_distribution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    revenue REAL NOT NULL,
                    operating_costs REAL,
                    employee_wages REAL,
                    payments_to_capital_providers REAL,
                    payments_to_governments REAL,
                    community_investments REAL,
                    retained_earnings REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: email_logs ---
CREATE TABLE email_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    to_email TEXT,
                    subject TEXT,
                    body TEXT,
                    status TEXT,
                    error TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: email_notifications ---
CREATE TABLE email_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                sent_status TEXT DEFAULT 'pending',
                sent_at TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: email_queue ---
CREATE TABLE email_queue (
                    id INTEGER PRIMARY KEY,
                    to_email TEXT NOT NULL,
                    cc TEXT,
                    bcc TEXT,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT DEFAULT 'queued',
                    tries INTEGER DEFAULT 0,
                    last_error TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    sent_at TEXT
                );

--- Table: email_verifications ---
CREATE TABLE email_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    verification_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

--- Table: emergency_drills ---
CREATE TABLE emergency_drills (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                drill_name TEXT NOT NULL,
                drill_type TEXT, -- Yangın, Deprem, Siber Saldırı, Kimyasal Sızıntı
                drill_date TEXT,
                participants_count INTEGER DEFAULT 0,
                duration_minutes INTEGER, -- Tatbikat süresi (dakika)
                success_rate REAL, -- Başarı oranı (%)
                lessons_learned TEXT, -- Öğrenilen dersler
                improvement_areas TEXT, -- İyileştirme alanları
                next_drill_date TEXT, -- Sonraki tatbikat tarihi
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: emergency_incidents ---
CREATE TABLE emergency_incidents (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                incident_type TEXT NOT NULL, -- Yangın, Deprem, Siber Saldırı, vb.
                severity TEXT NOT NULL, -- Düşük, Orta, Yüksek, Kritik
                incident_date TEXT,
                resolution_date TEXT,
                description TEXT,
                impact_assessment TEXT,
                response_time_minutes INTEGER, -- Müdahale süresi (dakika)
                financial_impact REAL, -- Mali etki (TL)
                lessons_learned TEXT,
                prevention_measures TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: emergency_management_metrics ---
CREATE TABLE emergency_management_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                year INTEGER,
                quarter INTEGER,
                
                -- Acil Durum Planları
                emergency_response_plan BOOLEAN,
                business_continuity_plan BOOLEAN,
                disaster_recovery_plan BOOLEAN,
                crisis_communication_plan BOOLEAN,
                plan_last_updated TEXT,
                plan_testing_frequency TEXT,
                
                -- Risk Değerlendirmesi
                risk_assessment_conducted BOOLEAN,
                risk_assessment_frequency TEXT,
                identified_risks_count INTEGER,
                high_risk_scenarios INTEGER,
                risk_mitigation_measures INTEGER,
                
                -- Acil Durum Ekip ve Eğitim
                emergency_response_team_size INTEGER,
                emergency_coordinator_appointed BOOLEAN,
                emergency_training_hours INTEGER,
                emergency_drill_frequency TEXT,
                last_emergency_drill_date TEXT,
                
                -- İletişim ve Uyarı Sistemleri
                emergency_communication_system BOOLEAN,
                alert_system_technology TEXT,
                stakeholder_notification_system BOOLEAN,
                backup_communication_methods TEXT,
                
                -- Kaynak ve Tesisler
                emergency_supplies_stocked BOOLEAN,
                emergency_facilities_count INTEGER,
                backup_power_systems BOOLEAN,
                water_emergency_supply_days INTEGER,
                food_emergency_supply_days INTEGER,
                
                -- İş Sürekliliği
                business_continuity_testing BOOLEAN,
                backup_data_center BOOLEAN,
                remote_work_capability REAL,
                supply_chain_risk_mitigation BOOLEAN,
                critical_process_identification BOOLEAN,
                
                -- Finansal Hazırlık
                emergency_fund_available BOOLEAN,
                emergency_fund_amount REAL,
                insurance_coverage_adequate BOOLEAN,
                business_interruption_insurance BOOLEAN,
                
                -- Toplum ve Çevre Desteği
                community_emergency_support BOOLEAN,
                environmental_impact_assessment BOOLEAN,
                local_authority_coordination BOOLEAN,
                volunteer_network_established BOOLEAN,
                
                -- Performans Metrikleri
                emergency_response_time_minutes INTEGER,
                business_recovery_time_hours INTEGER,
                employee_safety_incidents INTEGER,
                plan_effectiveness_score REAL,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (company_id) REFERENCES companies (id)
            );

--- Table: emergency_metrics ---
CREATE TABLE emergency_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            business_continuity_plan BOOLEAN DEFAULT 0, -- İş sürekliliği planı
            emergency_response_team BOOLEAN DEFAULT 0, -- Acil durum ekibi
            risk_assessment_matrix BOOLEAN DEFAULT 0, -- Risk değerlendirme matrisi
            emergency_drills_count INTEGER DEFAULT 0, -- Acil durum tatbikat sayısı
            drill_participation_rate REAL, -- Tatbikat katılım oranı (%)
            insurance_coverage REAL, -- Sigorta kapsamı (TL)
            emergency_contacts_count INTEGER DEFAULT 0, -- Acil durum iletişim sayısı
            evacuation_plan BOOLEAN DEFAULT 0, -- Tahliye planı
            communication_plan BOOLEAN DEFAULT 0, -- İletişim planı
            backup_systems_count INTEGER DEFAULT 0, -- Yedek sistem sayısı
            recovery_time_objective REAL, -- Kurtarma süre hedefi (saat)
            maximum_tolerable_downtime REAL, -- Maksimum kabul edilebilir kesinti (saat)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, reporting_period TEXT, created_date TEXT, emergency_drill_frequency INTEGER, risk_assessment_score REAL, crisis_management_team TEXT, insurance_coverage_score REAL,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: emission_projections ---
CREATE TABLE emission_projections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    scope1_emissions REAL DEFAULT 0,
                    scope2_emissions REAL DEFAULT 0,
                    scope3_emissions REAL DEFAULT 0,
                    total_emissions REAL DEFAULT 0,
                    emission_intensity REAL DEFAULT 0,
                    reduction_percentage REAL DEFAULT 0,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                );

--- Table: emission_reduction_categories ---
CREATE TABLE emission_reduction_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT NOT NULL,
                    description TEXT,
                    scope_type TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: emission_reduction_progress ---
CREATE TABLE emission_reduction_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    progress_date TEXT NOT NULL,
                    progress_percentage REAL NOT NULL,
                    actual_reduction REAL DEFAULT 0.0,
                    cost REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES emission_reduction_projects (id)
                );

--- Table: emission_reduction_projects ---
CREATE TABLE emission_reduction_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_description TEXT,
                    category_id INTEGER,
                    scope_type TEXT,
                    project_type TEXT,
                    start_date DATE,
                    end_date DATE,
                    expected_reduction REAL,
                    expected_reduction_unit TEXT DEFAULT 'tCO2e',
                    actual_reduction REAL,
                    actual_reduction_unit TEXT DEFAULT 'tCO2e',
                    investment_cost REAL,
                    cost_unit TEXT DEFAULT 'TL',
                    payback_period REAL,
                    project_status TEXT DEFAULT 'Planning',
                    progress_percentage REAL DEFAULT 0,
                    project_manager TEXT,
                    stakeholder TEXT,
                    methodology TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id),
                    FOREIGN KEY(category_id) REFERENCES emission_reduction_categories(id)
                );

--- Table: employee_certifications ---
CREATE TABLE employee_certifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    certification_name TEXT NOT NULL,
                    issuing_authority TEXT,
                    issue_date TEXT,
                    expiry_date TEXT,
                    renewal_required TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: employee_demographics ---
CREATE TABLE employee_demographics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    age_group TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    employee_count INTEGER NOT NULL,
                    percentage REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: employee_development ---
CREATE TABLE employee_development (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    development_type TEXT NOT NULL,
                    participant_count INTEGER NOT NULL,
                    total_hours REAL,
                    investment_amount REAL,
                    success_rate REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: employee_satisfaction ---
CREATE TABLE employee_satisfaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_year INTEGER NOT NULL,
                    survey_period TEXT NOT NULL,
                    satisfaction_category TEXT NOT NULL,
                    average_score REAL NOT NULL,
                    response_count INTEGER NOT NULL,
                    total_responses INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: employee_statistics ---
CREATE TABLE employee_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    total_employees INTEGER NOT NULL,
                    full_time_employees INTEGER,
                    part_time_employees INTEGER,
                    contract_employees INTEGER,
                    new_hires INTEGER,
                    departures INTEGER,
                    turnover_rate REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: employees ---
CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    position TEXT,
                    department TEXT,
                    gender TEXT,
                    age INTEGER,
                    salary REAL,
                    start_date TEXT,
                    year INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: energy_consumption ---
CREATE TABLE energy_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    energy_type TEXT NOT NULL,
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    cost REAL,
                    source TEXT,
                    location TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: energy_consumption_records ---
CREATE TABLE energy_consumption_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    facility_id INTEGER,
                    facility_name TEXT,
                    energy_type TEXT NOT NULL, -- 'electricity', 'natural_gas', 'diesel', 'gasoline', 'coal', 'renewable'
                    energy_source TEXT, -- 'grid', 'solar', 'wind', 'hydro', 'biomass', 'geothermal'
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL, -- 'kWh', 'm3', 'liter', 'ton'
                    measurement_date TEXT NOT NULL,
                    billing_period_start TEXT,
                    billing_period_end TEXT,
                    cost REAL,
                    currency TEXT DEFAULT 'TRY',
                    emission_factor REAL, -- kg CO2e per unit
                    co2_emissions REAL, -- calculated
                    energy_intensity REAL, -- per unit production
                    production_volume REAL, -- for intensity calculation
                    production_unit TEXT, -- 'ton', 'piece', 'm2'
                    data_source TEXT, -- 'meter_reading', 'bill', 'estimate'
                    notes TEXT,
                    recorded_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                , invoice_date TEXT, due_date TEXT, supplier TEXT);

--- Table: energy_efficiency_projects ---
CREATE TABLE energy_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    energy_savings REAL,
                    savings_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    co2_reduction REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: energy_kpis ---
CREATE TABLE energy_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_value REAL NOT NULL,
                    kpi_unit TEXT NOT NULL,
                    benchmark_value REAL,
                    benchmark_source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: energy_reports ---
CREATE TABLE energy_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_period TEXT NOT NULL, -- 'YYYY-MM' or 'YYYY'
                    report_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'annual'
                    total_consumption REAL,
                    total_cost REAL,
                    total_emissions REAL,
                    renewable_ratio REAL, -- percentage
                    energy_intensity REAL,
                    efficiency_score REAL, -- 0-100
                    key_findings TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    generated_by INTEGER,
                    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: energy_sources ---
CREATE TABLE energy_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL, -- 'renewable', 'fossil', 'nuclear'
                    energy_type TEXT NOT NULL,
                    capacity REAL, -- installed capacity
                    capacity_unit TEXT, -- 'kW', 'MW'
                    efficiency REAL, -- percentage
                    emission_factor REAL, -- kg CO2e per unit
                    is_active INTEGER DEFAULT 1,
                    installation_date TEXT,
                    decommission_date TEXT,
                    location TEXT,
                    supplier TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: energy_targets ---
CREATE TABLE energy_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_consumption REAL,
                    target_reduction_percent REAL,
                    target_consumption REAL,
                    renewable_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: enhanced_audit_log ---
CREATE TABLE enhanced_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    datetime_str TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    action TEXT NOT NULL,
                    actor_id INTEGER,
                    actor_username TEXT,
                    actor_ip TEXT,
                    target_type TEXT,
                    target_id TEXT,
                    details TEXT,
                    is_critical INTEGER DEFAULT 0,
                    duration_ms REAL,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    session_id TEXT,
                    user_agent TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: esg_policies ---
CREATE TABLE esg_policies (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          pillar TEXT NOT NULL,               -- 'E' | 'S' | 'G'
          policy_name TEXT NOT NULL,
          status TEXT DEFAULT 'Planned',      -- Planned/Approved/Published
          document_url TEXT,
          notes TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: esrs_company_data ---
CREATE TABLE esrs_company_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    topic_code TEXT,
                    datapoint_code TEXT,
                    value TEXT,
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: esrs_datapoints ---
CREATE TABLE esrs_datapoints (
                    datapoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_code TEXT,
                    datapoint_code TEXT,
                    datapoint_name TEXT,
                    datapoint_type TEXT,
                    FOREIGN KEY (topic_code) REFERENCES esrs_topics(code)
                );

--- Table: esrs_disclosures ---
CREATE TABLE esrs_disclosures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    esrs_standard TEXT NOT NULL,
                    disclosure_code TEXT NOT NULL,
                    disclosure_name TEXT NOT NULL,
                    is_required BOOLEAN DEFAULT 0,
                    is_material BOOLEAN DEFAULT 0,
                    completion_status TEXT DEFAULT 'tamamlanmadi',
                    disclosure_data TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: esrs_materiality ---
CREATE TABLE esrs_materiality (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                financial_materiality INTEGER DEFAULT 0,
                impact_materiality INTEGER DEFAULT 0,
                overall_score INTEGER DEFAULT 0,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

--- Table: esrs_requirements ---
CREATE TABLE esrs_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    esrs_standard TEXT NOT NULL,
                    requirement_number TEXT NOT NULL,
                    requirement_title TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    reporting_content TEXT,
                    data_sources TEXT,
                    assurance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: esrs_standards ---
CREATE TABLE esrs_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                title TEXT,
                category TEXT,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

--- Table: esrs_topics ---
CREATE TABLE esrs_topics (
                    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    UNIQUE(code)
                );

--- Table: eu_taxonomy_activities ---
CREATE TABLE eu_taxonomy_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_code VARCHAR(50) UNIQUE NOT NULL,
                    activity_name VARCHAR(255) NOT NULL,
                    activity_name_tr VARCHAR(255),
                    sector VARCHAR(100),
                    description TEXT,
                    nace_code VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: eu_taxonomy_alignment ---
CREATE TABLE eu_taxonomy_alignment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    activity_name TEXT NOT NULL,
                    activity_code TEXT,
                    environmental_objective TEXT NOT NULL,
                    substantial_contribution BOOLEAN DEFAULT 0,
                    dnsh_compliance BOOLEAN DEFAULT 0,
                    minimum_safeguards BOOLEAN DEFAULT 0,
                    aligned_percentage REAL DEFAULT 0,
                    revenue_euro REAL DEFAULT 0,
                    capex_euro REAL DEFAULT 0,
                    opex_euro REAL DEFAULT 0,
                    documentation TEXT,
                    assessment_year INTEGER,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: eu_taxonomy_compliance ---
CREATE TABLE eu_taxonomy_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    economic_activity TEXT NOT NULL,
                    taxonomy_code TEXT NOT NULL,
                    alignment_percentage REAL,
                    turnover_share REAL,
                    capex_share REAL,
                    opex_share REAL,
                    nfrd_requirement TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: evidence ---
CREATE TABLE evidence (
  id INTEGER PRIMARY KEY,
  response_id INTEGER NOT NULL,
  kind TEXT,                           -- dosya, url, belge
  url TEXT,
  description TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(response_id) REFERENCES responses(id) ON DELETE CASCADE
);

--- Table: evidence_documents ---
CREATE TABLE evidence_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by INTEGER,
                    related_data_item TEXT,
                    description TEXT,
                    is_verified BOOLEAN DEFAULT 0,
                    verified_by INTEGER,
                    verified_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (uploaded_by) REFERENCES users(id),
                    FOREIGN KEY (verified_by) REFERENCES auditors(id)
                );

--- Table: file_folders ---
CREATE TABLE file_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                parent_folder_id INTEGER,
                folder_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                description TEXT,
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (parent_folder_id) REFERENCES file_folders(id)
            );

--- Table: file_metadata ---
CREATE TABLE file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                meta_key TEXT NOT NULL,
                meta_value TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            );

--- Table: file_shares ---
CREATE TABLE file_shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                shared_with_user_id INTEGER,
                shared_with_company_id INTEGER,
                permission TEXT DEFAULT 'view',
                shared_by INTEGER,
                shared_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (file_id) REFERENCES files(id)
            );

--- Table: file_tag_relations ---
CREATE TABLE file_tag_relations (
                file_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                created_at TEXT,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES files(id),
                FOREIGN KEY (tag_id) REFERENCES file_tags(id)
            );

--- Table: file_tags ---
CREATE TABLE file_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                tag_color TEXT DEFAULT '#3498db',
                created_at TEXT
            );

--- Table: files ---
CREATE TABLE files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                folder_id INTEGER,
                file_name TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                mime_type TEXT,
                checksum TEXT,
                version INTEGER DEFAULT 1,
                parent_version_id INTEGER,
                description TEXT,
                uploaded_by INTEGER,
                uploaded_at TEXT,
                updated_at TEXT,
                is_deleted INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (folder_id) REFERENCES file_folders(id),
                FOREIGN KEY (parent_version_id) REFERENCES files(id)
            );

--- Table: financial_impact_simulation ---
CREATE TABLE financial_impact_simulation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    carbon_cost REAL DEFAULT 0,
                    energy_cost REAL DEFAULT 0,
                    capex_investment REAL DEFAULT 0,
                    opex_change REAL DEFAULT 0,
                    revenue_impact REAL DEFAULT 0,
                    net_financial_impact REAL DEFAULT 0,
                    roi_percentage REAL DEFAULT 0,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                );

--- Table: financial_performance ---
CREATE TABLE financial_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_assets REAL,
                    total_liabilities REAL,
                    equity REAL,
                    net_profit REAL,
                    operating_profit REAL,
                    ebitda REAL,
                    return_on_equity REAL,
                    return_on_assets REAL,
                    debt_to_equity_ratio REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: forecast_results ---
CREATE TABLE forecast_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    forecast_year INTEGER NOT NULL,
                    forecast_value REAL NOT NULL,
                    forecast_method TEXT NOT NULL,
                    confidence_interval_lower REAL,
                    confidence_interval_upper REAL,
                    confidence_level REAL DEFAULT 95.0,
                    assumptions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, metric_code, forecast_year, forecast_method)
                );

--- Table: form_fields ---
CREATE TABLE form_fields (
                    id INTEGER PRIMARY KEY,
                    form_id INTEGER NOT NULL,
                    field_type TEXT DEFAULT 'text',
                    label TEXT NOT NULL,
                    name TEXT NOT NULL,
                    options_json TEXT,
                    required INTEGER DEFAULT 0,
                    order_index INTEGER DEFAULT 0,
                    FOREIGN KEY (form_id) REFERENCES forms(id)
                );

--- Table: form_responses ---
CREATE TABLE form_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id TEXT NOT NULL,
                company_id INTEGER NOT NULL,
                response_data TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT,
                created_by INTEGER,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: form_submission_values ---
CREATE TABLE form_submission_values (
                    id INTEGER PRIMARY KEY,
                    submission_id INTEGER NOT NULL,
                    field_id INTEGER NOT NULL,
                    value_text TEXT,
                    value_number REAL,
                    value_choice TEXT,
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id),
                    FOREIGN KEY (field_id) REFERENCES form_fields(id)
                );

--- Table: form_submissions ---
CREATE TABLE form_submissions (
                    id INTEGER PRIMARY KEY,
                    form_id INTEGER NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id)
                );

--- Table: form_templates ---
CREATE TABLE form_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                standard TEXT,
                schema_json TEXT NOT NULL,
                created_at TEXT,
                updated_at TEXT
            );

--- Table: forms ---
CREATE TABLE forms (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    module TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: goal_assessments ---
CREATE TABLE goal_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    smart_score INTEGER, -- 1-5 rating for each SMART criteria
                    specific_score INTEGER, -- 1-5
                    measurable_score INTEGER, -- 1-5
                    achievable_score INTEGER, -- 1-5
                    relevant_score INTEGER, -- 1-5
                    time_bound_score INTEGER, -- 1-5
                    overall_assessment TEXT,
                    recommendations TEXT, -- JSON array
                    next_assessment_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES smart_goals(id)
                );

--- Table: goal_hierarchy ---
CREATE TABLE goal_hierarchy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_goal_id INTEGER NOT NULL,
                    child_goal_id INTEGER NOT NULL,
                    relationship_type TEXT DEFAULT 'supports', -- 'supports', 'enables', 'depends_on'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_goal_id) REFERENCES smart_goals(id),
                    FOREIGN KEY (child_goal_id) REFERENCES smart_goals(id)
                );

--- Table: goal_progress ---
CREATE TABLE goal_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL, -- 'YYYY-MM' or 'YYYY'
                    actual_value REAL,
                    target_value REAL,
                    achievement_rate REAL, -- percentage
                    progress_narrative TEXT,
                    challenges TEXT, -- JSON array
                    actions_taken TEXT, -- JSON array
                    next_steps TEXT, -- JSON array
                    reported_by INTEGER,
                    reported_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES strategic_goals(id)
                );

--- Table: goal_progress_tracking ---
CREATE TABLE goal_progress_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    tracking_date TEXT NOT NULL,
                    actual_value REAL NOT NULL,
                    target_value REAL,
                    progress_percentage REAL,
                    variance REAL, -- difference from target
                    variance_percentage REAL,
                    status_comment TEXT,
                    challenges_faced TEXT, -- JSON array
                    actions_taken TEXT, -- JSON array
                    next_actions TEXT, -- JSON array
                    reported_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES smart_goals(id)
                );

--- Table: gri_101_biodiversity ---
CREATE TABLE gri_101_biodiversity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_102_climate ---
CREATE TABLE gri_102_climate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_103_energy ---
CREATE TABLE gri_103_energy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_11_oil_gas ---
CREATE TABLE gri_11_oil_gas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_12_coal ---
CREATE TABLE gri_12_coal (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_13_agriculture ---
CREATE TABLE gri_13_agriculture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_14_mining ---
CREATE TABLE gri_14_mining (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    standard_id TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_description TEXT,
                    disclosure_requirements TEXT,
                    management_approach TEXT,
                    metrics TEXT,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    compliance_status TEXT DEFAULT 'Not Started',
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_1_foundation ---
CREATE TABLE gri_1_foundation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    reporting_frequency TEXT NOT NULL,
                    reporting_boundary TEXT NOT NULL,
                    contact_information TEXT,
                    external_assurance TEXT,
                    stakeholder_engagement TEXT,
                    material_topics TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, statement_of_use TEXT, assurance_provider TEXT, assurance_standard TEXT, assurance_scope TEXT, assurance_date TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_2_general_disclosures ---
CREATE TABLE gri_2_general_disclosures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    disclosure_number TEXT NOT NULL,
                    disclosure_title TEXT NOT NULL,
                    disclosure_content TEXT NOT NULL,
                    reporting_status TEXT NOT NULL,
                    data_quality TEXT,
                    external_verification TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, page_number INTEGER, omission_reason TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_3_content_index ---
CREATE TABLE gri_3_content_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    gri_standard TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    disclosure_number TEXT NOT NULL,
                    page_number INTEGER,
                    ommission_reason TEXT,
                    reporting_status TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, omission_reason TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_audit_log ---
CREATE TABLE gri_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT,
                    action_type TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT
                );

--- Table: gri_benchmarks ---
CREATE TABLE gri_benchmarks (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    scope TEXT,
                    value TEXT,
                    unit TEXT,
                    source TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_categories ---
CREATE TABLE gri_categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    group_name TEXT NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_digital_tools ---
CREATE TABLE gri_digital_tools (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    description TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_disclosures ---
CREATE TABLE gri_disclosures (
                id INTEGER PRIMARY KEY,
                standard_id INTEGER,
                disclosure_code TEXT,
                disclosure_title TEXT,
                disclosure_description TEXT,
                category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
            );

--- Table: gri_indicators ---
CREATE TABLE gri_indicators (
                    id INTEGER PRIMARY KEY,
                    standard_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    unit TEXT,
                    methodology TEXT,
                    reporting_requirement TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, priority TEXT, requirement_level TEXT, reporting_frequency TEXT, data_quality TEXT, audit_required TEXT, validation_required TEXT, digitalization_status TEXT, cost_level TEXT, time_requirement TEXT, expertise_requirement TEXT, sustainability_impact TEXT, legal_compliance TEXT, sector_specific TEXT, international_standard TEXT, metric_type TEXT, scale_unit TEXT, data_source_system TEXT, reporting_format TEXT, tsrs_esrs_mapping TEXT, un_sdg_mapping TEXT, gri_3_3_reference TEXT, impact_area TEXT, stakeholder_group TEXT,
                    FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
                );

--- Table: gri_kpis ---
CREATE TABLE gri_kpis (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    formula TEXT,
                    unit TEXT,
                    frequency TEXT,
                    owner TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_material_topics ---
CREATE TABLE gri_material_topics (
            id INTEGER PRIMARY KEY,
            topic_code TEXT,
            topic_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: gri_materiality_assessment ---
CREATE TABLE gri_materiality_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_category TEXT NOT NULL,
                    stakeholder_importance_score REAL,
                    business_impact_score REAL,
                    materiality_level TEXT NOT NULL,
                    reporting_boundary TEXT,
                    management_approach TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: gri_permissions ---
CREATE TABLE gri_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    allowed BOOLEAN DEFAULT 1,
                    conditions TEXT
                );

--- Table: gri_reporting_formats ---
CREATE TABLE gri_reporting_formats (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    extension TEXT NOT NULL,
                    description TEXT,
                    template_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_responses ---
CREATE TABLE gri_responses (
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
                );

--- Table: gri_risks ---
CREATE TABLE gri_risks (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    impact TEXT,
                    likelihood TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_sector_workflows ---
CREATE TABLE gri_sector_workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector_code TEXT NOT NULL,
                    sector_name TEXT NOT NULL,
                    description TEXT,
                    key_topics TEXT,
                    mandatory_indicators TEXT,
                    special_requirements TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_sectoral_index ---
CREATE TABLE gri_sectoral_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    standard_code TEXT UNIQUE NOT NULL,
                    standard_name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    description TEXT,
                    applicable_sectors TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_selections ---
CREATE TABLE gri_selections (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    indicator_id INTEGER NOT NULL,
                    selected INTEGER DEFAULT 0,
                    priority_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_sources ---
CREATE TABLE gri_sources (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    system TEXT,
                    description TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_standards ---
CREATE TABLE gri_standards (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                , type TEXT, sub_category TEXT);

--- Table: gri_targets ---
CREATE TABLE gri_targets (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    target_value TEXT,
                    unit TEXT,
                    method TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_units ---
CREATE TABLE gri_units (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    name_tr TEXT NOT NULL,
                    name_en TEXT,
                    category TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_user_roles ---
CREATE TABLE gri_user_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    permissions TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: gri_validation_rules ---
CREATE TABLE gri_validation_rules (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER,
                    rule_type TEXT NOT NULL,
                    rule_expression TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                );

--- Table: gri_workflow_steps ---
CREATE TABLE gri_workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    step_number INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    duration TEXT,
                    required_docs TEXT,
                    stakeholders TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES gri_sector_workflows(id)
                );

--- Table: hosting_surveys ---
CREATE TABLE hosting_surveys (
                    local_survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hosting_survey_id INTEGER,
                    survey_name TEXT,
                    company_name TEXT,
                    survey_type TEXT,
                    survey_url TEXT,
                    survey_token TEXT,
                    created_date DATETIME,
                    deadline_date DATE,
                    status TEXT,
                    last_sync_date DATETIME,
                    response_count INTEGER DEFAULT 0
                );

--- Table: hr_compensation ---
CREATE TABLE hr_compensation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    position_level TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    avg_salary REAL,
                    min_salary REAL,
                    max_salary REAL,
                    employee_count INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: hr_demographics ---
CREATE TABLE hr_demographics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    gender TEXT,
                    age_group TEXT,
                    employment_type TEXT,
                    position_level TEXT,
                    department TEXT,
                    count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: hr_diversity ---
CREATE TABLE hr_diversity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    value REAL,
                    unit TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: hr_employees ---
CREATE TABLE hr_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_count INTEGER,
                gender TEXT,
                department TEXT,
                age_group TEXT,
                year INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

--- Table: hr_targets ---
CREATE TABLE hr_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: hr_turnover ---
CREATE TABLE hr_turnover (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    period_month INTEGER,
                    new_hires INTEGER DEFAULT 0,
                    terminations INTEGER DEFAULT 0,
                    voluntary_exits INTEGER DEFAULT 0,
                    involuntary_exits INTEGER DEFAULT 0,
                    gender TEXT,
                    age_group TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: ifrs_s1_requirements ---
CREATE TABLE ifrs_s1_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    requirement_code TEXT NOT NULL,
                    requirement_title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    description TEXT,
                    disclosure_type TEXT,
                    measurement_basis TEXT,
                    reporting_frequency TEXT,
                    status TEXT DEFAULT 'Not Started',
                    implementation_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );

--- Table: ifrs_s2_climate ---
CREATE TABLE ifrs_s2_climate (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    disclosure_code TEXT NOT NULL,
                    disclosure_title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    description TEXT,
                    measurement_approach TEXT,
                    data_requirements TEXT,
                    reporting_frequency TEXT,
                    status TEXT DEFAULT 'Not Started',
                    implementation_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );

--- Table: iirc_capital_details ---
CREATE TABLE iirc_capital_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    capital_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT,
                    measurement_date DATE,
                    data_source TEXT,
                    verification_status TEXT DEFAULT 'Dogrulanmadi',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (capital_id) REFERENCES iirc_six_capitals(id)
                );

--- Table: iirc_capitals ---
CREATE TABLE iirc_capitals (
            id INTEGER PRIMARY KEY,
            capital_type TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: iirc_connectivity ---
CREATE TABLE iirc_connectivity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    source_capital TEXT NOT NULL,
                    target_capital TEXT NOT NULL,
                    connection_type TEXT NOT NULL,
                    connection_strength TEXT DEFAULT 'Orta',
                    description TEXT,
                    examples TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: iirc_report_content ---
CREATE TABLE iirc_report_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    section_code TEXT NOT NULL,
                    section_title TEXT NOT NULL,
                    content TEXT,
                    related_capitals TEXT,
                    completion_status REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, section_code)
                );

--- Table: iirc_report_templates ---
CREATE TABLE iirc_report_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_code TEXT UNIQUE NOT NULL,
                    template_name TEXT NOT NULL,
                    template_description TEXT,
                    sections TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: iirc_six_capitals ---
CREATE TABLE iirc_six_capitals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    capital_type TEXT NOT NULL,
                    capital_name TEXT NOT NULL,
                    current_value REAL DEFAULT 0.0,
                    change_from_previous REAL DEFAULT 0.0,
                    trend TEXT DEFAULT 'Stabil',
                    description TEXT,
                    metrics TEXT,
                    targets TEXT,
                    risks TEXT,
                    opportunities TEXT,
                    status TEXT DEFAULT 'Aktif',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, capital_type)
                );

--- Table: iirc_value_creation ---
CREATE TABLE iirc_value_creation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    story_element TEXT NOT NULL,
                    element_title TEXT NOT NULL,
                    content TEXT,
                    related_capitals TEXT,
                    supporting_data TEXT,
                    order_index INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'Taslak',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: iirc_value_drivers ---
CREATE TABLE iirc_value_drivers (
            id INTEGER PRIMARY KEY,
            driver_name TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: import_errors ---
CREATE TABLE import_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                import_id INTEGER NOT NULL,
                row_number INTEGER,
                error_type TEXT,
                error_message TEXT,
                row_data TEXT,
                created_at TEXT,
                FOREIGN KEY (import_id) REFERENCES data_imports(id)
            );

--- Table: import_mappings ---
CREATE TABLE import_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mapping_name TEXT UNIQUE NOT NULL,
                import_type TEXT NOT NULL,
                column_mappings TEXT NOT NULL,
                transformation_rules TEXT,
                created_at TEXT,
                updated_at TEXT
            );

--- Table: innovation_metrics ---
CREATE TABLE innovation_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            rd_investment_ratio REAL, -- Toplam ciro içindeki AR-GE oranı (%)
            rd_investment_amount REAL, -- AR-GE yatırım miktarı (TL)
            patent_applications INTEGER DEFAULT 0, -- Patent başvuru sayısı
            utility_models INTEGER DEFAULT 0, -- Faydalı model sayısı
            patents_granted INTEGER DEFAULT 0, -- Verilen patent sayısı
            ecodesign_integration BOOLEAN DEFAULT 0, -- Eko-tasarım entegrasyonu
            lca_implementation BOOLEAN DEFAULT 0, -- LCA uygulaması
            innovation_budget REAL, -- İnovasyon bütçesi (TL)
            innovation_projects INTEGER DEFAULT 0, -- Aktif inovasyon proje sayısı
            sustainability_innovation_ratio REAL, -- Sürdürülebilir inovasyon oranı (%)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, reporting_period TEXT, created_date TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: innovation_projects ---
CREATE TABLE innovation_projects (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            project_name TEXT NOT NULL,
            project_type TEXT, -- R&D, P&D, Sustainability, Digital
            description TEXT,
            start_date TEXT,
            end_date TEXT,
            budget REAL,
            status TEXT DEFAULT 'active', -- active, completed, cancelled
            sdg_mapping TEXT, -- İlgili SDG hedefleri
            sustainability_focus BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: intellectual_property ---
CREATE TABLE intellectual_property (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            ip_type TEXT NOT NULL, -- patent, utility_model, trademark, copyright
            title TEXT NOT NULL,
            application_number TEXT,
            application_date TEXT,
            grant_date TEXT,
            status TEXT, -- applied, granted, rejected, expired
            description TEXT,
            sdg_mapping TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: ip_blacklist ---
CREATE TABLE ip_blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL UNIQUE,
                reason TEXT,
                blocked_by TEXT,
                block_type TEXT DEFAULT 'manual',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: ip_whitelist ---
CREATE TABLE "ip_whitelist" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT NOT NULL UNIQUE,
                    description TEXT,
                    added_by TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: issb_action_plan ---
CREATE TABLE issb_action_plan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    gap_item TEXT,
                    standard TEXT,
                    module TEXT,
                    department TEXT,
                    responsible TEXT,
                    action_step TEXT,
                    due_date DATE,
                    status TEXT DEFAULT 'Beklemede',
                    dependencies TEXT,
                    owner_user_id INTEGER,
                    priority TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                , approval_status TEXT, approved_at TIMESTAMP);

--- Table: issb_action_plan_log ---
CREATE TABLE issb_action_plan_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_item_id INTEGER,
                    company_id INTEGER,
                    year INTEGER,
                    action TEXT,
                    changed_fields TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    changed_by INTEGER,
                    FOREIGN KEY(action_item_id) REFERENCES issb_action_plan(id)
                );

--- Table: issb_climate_data ---
CREATE TABLE issb_climate_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            governance_score INTEGER DEFAULT 0,
            strategy_score INTEGER DEFAULT 0,
            risk_management_score INTEGER DEFAULT 0,
            metrics_targets_score INTEGER DEFAULT 0,
            climate_risks TEXT,
            climate_opportunities TEXT,
            financial_impact REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );

--- Table: issb_data_sources ---
CREATE TABLE issb_data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    data_source_name TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    frequency TEXT,
                    responsible_department TEXT,
                    data_quality_score INTEGER DEFAULT 0,
                    last_updated DATE,
                    is_automated BOOLEAN DEFAULT 0,
                    notes TEXT
                );

--- Table: issb_disclosures ---
CREATE TABLE issb_disclosures (
            id INTEGER PRIMARY KEY,
            disclosure_code TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: issb_reporting_status ---
CREATE TABLE issb_reporting_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    reporting_period TEXT NOT NULL,
                    ifrs_s1_compliance_percentage REAL DEFAULT 0.0,
                    ifrs_s2_compliance_percentage REAL DEFAULT 0.0,
                    overall_compliance_percentage REAL DEFAULT 0.0,
                    readiness_level TEXT DEFAULT 'Not Ready',
                    last_assessment_date DATE,
                    next_review_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: kpi_definitions ---
CREATE TABLE kpi_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_code TEXT NOT NULL, -- unique identifier
                    description TEXT,
                    category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    unit TEXT NOT NULL,
                    calculation_method TEXT, -- formula or method
                    data_source TEXT,
                    frequency TEXT DEFAULT 'monthly',
                    target_value REAL,
                    baseline_value REAL,
                    benchmark_value REAL, -- industry benchmark
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: license_history ---
CREATE TABLE license_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id INTEGER,
                action TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                performed_by TEXT,
                ip_address TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (license_id) REFERENCES "licenses_old"(id)
            );

--- Table: licenses ---
CREATE TABLE licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                license_type TEXT NOT NULL DEFAULT 'trial',
                company_name TEXT NOT NULL,
                contact_email TEXT,
                contact_phone TEXT,
                issued_date TEXT DEFAULT CURRENT_TIMESTAMP,
                expiry_date TEXT,
                max_users INTEGER DEFAULT 5,
                max_companies INTEGER DEFAULT 1,
                enabled_modules TEXT,
                hardware_id TEXT,
                signature TEXT,
                is_active INTEGER DEFAULT 1,
                activation_date TEXT,
                last_check_date TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: licenses_old ---
CREATE TABLE "licenses_old" (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,
  mode TEXT,                           -- trial/standard/enterprise
  expires_at TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

--- Table: login_attempts ---
CREATE TABLE login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT,
                success INTEGER DEFAULT 0,
                failure_reason TEXT,
                user_agent TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: map_gri_tsrs ---
CREATE TABLE map_gri_tsrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gri_standard TEXT NOT NULL,
                gri_disclosure TEXT,
                tsrs_section TEXT,
                tsrs_metric TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            , relation_type TEXT, notes TEXT);

--- Table: map_sdg_gri ---
CREATE TABLE map_sdg_gri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_indicator_code TEXT NOT NULL,
                gri_standard TEXT NOT NULL,
                gri_disclosure TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            , relation_type TEXT, notes TEXT);

--- Table: map_sdg_tsrs ---
CREATE TABLE map_sdg_tsrs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_indicator_code TEXT NOT NULL,
                tsrs_section TEXT,
                tsrs_metric TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            , relation_type TEXT, notes TEXT);

--- Table: map_tsrs_gri ---
CREATE TABLE map_tsrs_gri (
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

--- Table: map_tsrs_sdg ---
CREATE TABLE map_tsrs_sdg (
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

--- Table: mapping_suggestions ---
CREATE TABLE mapping_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_standard TEXT NOT NULL,
                    source_code TEXT NOT NULL,
                    target_standard TEXT NOT NULL,
                    target_code TEXT NOT NULL,
                    confidence_score REAL,
                    suggestion_reason TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: materiality_assessments ---
CREATE TABLE materiality_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_name TEXT NOT NULL,
                    stakeholder_category TEXT NOT NULL,
                    assessment_data TEXT,
                    priority_scores TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: materiality_matrix ---
CREATE TABLE materiality_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    stakeholder_priority REAL NOT NULL,
                    business_impact REAL NOT NULL,
                    materiality_level TEXT NOT NULL,
                    quadrant TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                );

--- Table: materiality_responses ---
CREATE TABLE materiality_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT,
                    stakeholder_email TEXT,
                    stakeholder_organization TEXT,
                    stakeholder_role TEXT,
                    topic_code TEXT NOT NULL,
                    topic_name TEXT,
                    importance_score INTEGER,
                    impact_score INTEGER,
                    comment TEXT,
                    response_date TIMESTAMP,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: materiality_topics ---
CREATE TABLE materiality_topics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            sdg_mapping TEXT,
            priority_score REAL DEFAULT 0,
            stakeholder_impact REAL DEFAULT 0,
            business_impact REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: materiality_updates ---
CREATE TABLE materiality_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    update_type TEXT NOT NULL,
                    previous_score REAL,
                    new_score REAL,
                    change_reason TEXT,
                    update_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: message_templates ---
CREATE TABLE message_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    template_content TEXT NOT NULL, -- JSON template
                    variables TEXT, -- JSON array of variable names
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: message_variables ---
CREATE TABLE message_variables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    variable_name TEXT NOT NULL,
                    variable_value TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES ceo_messages(id)
                );

--- Table: mfa_settings ---
CREATE TABLE mfa_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_secret TEXT,
                    backup_codes TEXT,
                    recovery_email TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: missing_data_alerts ---
CREATE TABLE missing_data_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    data_field TEXT NOT NULL,
                    field_description TEXT,
                    importance_level TEXT DEFAULT 'orta',
                    alert_status TEXT DEFAULT 'aktif',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                );

--- Table: module_restrictions ---
CREATE TABLE module_restrictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_id INTEGER,
                module_name TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                max_usage_count INTEGER,
                current_usage_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (license_id) REFERENCES "licenses_old"(id)
            );

--- Table: module_states ---
CREATE TABLE module_states (
                    module_key TEXT PRIMARY KEY,
                    enabled BOOLEAN NOT NULL DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                );

--- Table: modules ---
CREATE TABLE modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_code TEXT UNIQUE NOT NULL,
                module_name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                category TEXT,
                display_order INTEGER,
                is_core INTEGER DEFAULT 0,
                default_enabled INTEGER DEFAULT 1
            );

--- Table: modules_backup ---
CREATE TABLE modules_backup(
  id INT,
  module_code TEXT,
  module_name TEXT,
  description TEXT,
  icon TEXT,
  category TEXT,
  display_order INT,
  is_core INT,
  default_enabled INT
);

--- Table: notifications ---
CREATE TABLE notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        message TEXT,
        type TEXT DEFAULT 'info',
        related_task_id INTEGER,
        is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (related_task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );

--- Table: ohs_incidents ---
CREATE TABLE ohs_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    incident_date TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT,
                    days_lost INTEGER DEFAULT 0,
                    fatality INTEGER DEFAULT 0,
                    gender TEXT,
                    department TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: ohs_training ---
CREATE TABLE ohs_training (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    training_type TEXT NOT NULL,
                    participants INTEGER DEFAULT 0,
                    hours REAL DEFAULT 0,
                    cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: online_surveys ---
CREATE TABLE online_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_title TEXT NOT NULL,
                    survey_description TEXT,
                    target_groups TEXT NOT NULL,
                    survey_link TEXT UNIQUE NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    total_questions INTEGER DEFAULT 0,
                    response_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: opportunities ---
CREATE TABLE opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_name TEXT NOT NULL,
            category TEXT,
            score INTEGER,
            action_plan TEXT,
            owner TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

--- Table: opportunity_assessments ---
CREATE TABLE opportunity_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessor_name TEXT NOT NULL,
                    potential_value TEXT,
                    probability_level TEXT NOT NULL,
                    implementation_effort TEXT NOT NULL,
                    opportunity_score INTEGER NOT NULL,
                    assessment_rationale TEXT,
                    implementation_progress TEXT, -- percentage
                    status_change TEXT, -- if any
                    next_assessment_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (opportunity_id) REFERENCES sustainability_opportunities(id)
                );

--- Table: password_reset_tokens ---
CREATE TABLE password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: password_resets ---
CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    reset_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

--- Table: penetration_tests ---
CREATE TABLE penetration_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    test_date DATETIME NOT NULL,
                    tester_name TEXT,
                    vulnerabilities_found INTEGER DEFAULT 0,
                    critical_vulnerabilities INTEGER DEFAULT 0,
                    high_vulnerabilities INTEGER DEFAULT 0,
                    medium_vulnerabilities INTEGER DEFAULT 0,
                    low_vulnerabilities INTEGER DEFAULT 0,
                    test_report_path TEXT,
                    recommendations TEXT,
                    status TEXT DEFAULT 'Completed',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

--- Table: performance_evaluations ---
CREATE TABLE performance_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    evaluation_year INTEGER NOT NULL,
                    evaluation_period TEXT NOT NULL,
                    overall_rating REAL NOT NULL,
                    goal_achievement REAL,
                    competency_score REAL,
                    development_needs TEXT,
                    career_planning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: performance_reviews ---
CREATE TABLE performance_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    reviewed_employees INTEGER DEFAULT 0,
                    total_employees INTEGER,
                    gender TEXT,
                    position_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: permissions ---
CREATE TABLE permissions (
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,           -- manage_users, edit_sdg, publish_reports...
  description TEXT
, name VARCHAR(100), display_name VARCHAR(150), module TEXT, action TEXT, resource TEXT, is_active INTEGER DEFAULT 1);

--- Table: physical_risks ---
CREATE TABLE physical_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    risk_type TEXT NOT NULL,
                    risk_event TEXT NOT NULL,
                    affected_locations TEXT,
                    likelihood TEXT DEFAULT 'orta',
                    impact TEXT DEFAULT 'orta',
                    financial_impact_min REAL DEFAULT 0,
                    financial_impact_max REAL DEFAULT 0,
                    timeframe TEXT,
                    adaptation_measures TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                );

--- Table: policy_categories ---
CREATE TABLE policy_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_code VARCHAR(50) UNIQUE NOT NULL,
                    category_name VARCHAR(255) NOT NULL,
                    category_name_tr VARCHAR(255),
                    description TEXT,
                    icon VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: policy_framework_mapping ---
CREATE TABLE policy_framework_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_id INTEGER NOT NULL,
                    framework_type VARCHAR(50) NOT NULL,
                    framework_code VARCHAR(100),
                    alignment_level VARCHAR(50),
                    notes TEXT,
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                );

--- Table: policy_module_mapping ---
CREATE TABLE policy_module_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    policy_id INTEGER NOT NULL,
                    module_name VARCHAR(100) NOT NULL,
                    metric_name VARCHAR(255),
                    target_value VARCHAR(100),
                    mapping_type VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (policy_id) REFERENCES company_policies(id)
                );

--- Table: policy_templates ---
CREATE TABLE policy_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_code VARCHAR(50) UNIQUE NOT NULL,
                    template_name VARCHAR(255) NOT NULL,
                    template_name_tr VARCHAR(255),
                    category_id INTEGER,
                    description TEXT,
                    content TEXT,
                    version VARCHAR(20),
                    language VARCHAR(10) DEFAULT 'tr',
                    file_path VARCHAR(500),
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES policy_categories(id)
                );

--- Table: portal_access_logs ---
CREATE TABLE portal_access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stakeholder_id INTEGER NOT NULL,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    action_type TEXT,
                    details TEXT,
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                );

--- Table: prioritization_results ---
CREATE TABLE prioritization_results (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            total_score REAL NOT NULL,
            priority_level TEXT NOT NULL, -- high, medium, low
            calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(topic_id) REFERENCES materiality_topics(id) ON DELETE CASCADE
        );

--- Table: project_impacts ---
CREATE TABLE project_impacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    impact_type TEXT NOT NULL,
                    impact_description TEXT,
                    impact_value REAL,
                    impact_unit TEXT,
                    measurement_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(project_id) REFERENCES emission_reduction_projects(id)
                );

--- Table: project_progress_records ---
CREATE TABLE project_progress_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    record_date DATE,
                    progress_percentage REAL,
                    actual_reduction REAL,
                    cost_incurred REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(project_id) REFERENCES emission_reduction_projects(id)
                );

--- Table: quality_certifications ---
CREATE TABLE quality_certifications (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            certification_type TEXT NOT NULL, -- ISO 9001, ISO 14001, vb.
            certification_body TEXT, -- Sertifika veren kuruluş
            certificate_number TEXT,
            issue_date TEXT,
            expiry_date TEXT,
            status TEXT DEFAULT 'active', -- active, expired, suspended
            scope TEXT, -- Sertifika kapsamı
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: quality_improvement_projects ---
CREATE TABLE quality_improvement_projects (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                project_type TEXT, -- Six Sigma, Lean, Kaizen, vb.
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'active', -- active, completed, cancelled
                cost_savings REAL, -- Maliyet tasarrufu
                quality_improvement REAL, -- Kalite iyileştirme oranı
                sdg_mapping TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: quality_metrics ---
CREATE TABLE quality_metrics (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            iso9001_certified BOOLEAN DEFAULT 0, -- ISO 9001 sertifikası
            iso14001_certified BOOLEAN DEFAULT 0, -- ISO 14001 sertifikası
            iso45001_certified BOOLEAN DEFAULT 0, -- ISO 45001 sertifikası
            customer_complaint_rate REAL, -- Müşteri şikayet oranı (%)
            customer_complaint_count INTEGER DEFAULT 0, -- Şikayet sayısı
            product_recall_count INTEGER DEFAULT 0, -- Ürün geri çağırma sayısı
            nps_score REAL, -- Net Promoter Score
            customer_satisfaction_score REAL, -- Müşteri memnuniyet skoru (1-10)
            quality_error_rate REAL, -- Kalite kontrol hata oranı (%)
            defect_rate REAL, -- Defekt oranı (%)
            first_pass_yield REAL, -- İlk geçiş verimliliği (%)
            supplier_quality_score REAL, -- Tedarikçi kalite skoru (1-10)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, reporting_period TEXT, created_date TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: question_bank ---
CREATE TABLE question_bank (
          id INTEGER PRIMARY KEY,
          indicator_code TEXT NOT NULL,
          q1 TEXT, q2 TEXT, q3 TEXT,
          default_unit TEXT,
          default_frequency TEXT,
          default_owner TEXT,
          default_source TEXT
        );

--- Table: question_responses ---
CREATE TABLE question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_number INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT,
                answered_at TEXT,
                gri_connection TEXT,
                tsrs_connection TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            );

--- Table: rate_limits ---
CREATE TABLE rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                window_start TEXT DEFAULT CURRENT_TIMESTAMP,
                last_request TEXT DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0,
                UNIQUE(resource_type, identifier)
            );

--- Table: recurring_task_templates ---
CREATE TABLE recurring_task_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL, -- 'monthly', 'quarterly', 'yearly', 'custom'
                    department TEXT NOT NULL,
                    task_type TEXT DEFAULT 'data_collection',
                    priority TEXT DEFAULT 'medium',
                    estimated_hours INTEGER DEFAULT 2,
                    deadline_days INTEGER DEFAULT 14,
                    recurring_type TEXT NOT NULL, -- 'monthly', 'quarterly', 'yearly', 'weekly'
                    recurring_day INTEGER, -- Ayın kaçıncı günü (1-31)
                    recurring_weekday INTEGER, -- Haftanın kaçıncı günü (0-6, Pazartesi=0)
                    recurring_interval INTEGER DEFAULT 1, -- Kaç ayda/yılda bir
                    form_template TEXT, -- JSON form şablonu
                    validation_rules TEXT, -- JSON validasyon kuralları
                    notification_days TEXT, -- JSON: [7, 3, 1] hatırlatma günleri
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    last_executed TEXT,
                    next_execution TEXT
                );

--- Table: recycling_projects ---
CREATE TABLE recycling_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    waste_types TEXT,
                    start_date DATE,
                    end_date DATE,
                    status TEXT DEFAULT 'Planning',
                    investment_amount REAL DEFAULT 0.0,
                    expected_savings REAL DEFAULT 0.0,
                    recycling_rate_before REAL DEFAULT 0.0,
                    recycling_rate_target REAL DEFAULT 0.0,
                    current_recycling_rate REAL DEFAULT 0.0,
                    environmental_impact TEXT,
                    economic_benefits TEXT,
                    challenges TEXT,
                    lessons_learned TEXT,
                    next_steps TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: renewable_energy ---
CREATE TABLE renewable_energy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    renewable_type TEXT NOT NULL,
                    capacity REAL,
                    capacity_unit TEXT,
                    generation REAL,
                    generation_unit TEXT,
                    self_consumption REAL,
                    grid_feed REAL,
                    cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: report_approval_workflow ---
CREATE TABLE report_approval_workflow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    report_version INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'taslak',
                    submitted_by INTEGER,
                    submitted_at TIMESTAMP,
                    approver_id INTEGER,
                    approved_at TIMESTAMP,
                    approval_notes TEXT,
                    rejection_reason TEXT,
                    FOREIGN KEY (report_id) REFERENCES report_versions(id)
                );

--- Table: report_categories ---
CREATE TABLE report_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    icon VARCHAR(20),
                    color VARCHAR(20),
                    is_active BOOLEAN DEFAULT 1
                );

--- Table: report_distributions ---
CREATE TABLE report_distributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    recipient_email VARCHAR(255),
                    recipient_name VARCHAR(100),
                    distribution_method VARCHAR(20),
                    sent_at TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'Pending',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, company_id INTEGER, distribution_name VARCHAR(100), recipient_type VARCHAR(20), distribution_status VARCHAR(20), updated_at TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                );

--- Table: report_email_history ---
CREATE TABLE report_email_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    recipient_email TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'gonderildi',
                    error_message TEXT,
                    FOREIGN KEY (report_id) REFERENCES report_registry(id)
                );

--- Table: report_email_log ---
CREATE TABLE report_email_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scheduled_report_id INTEGER,
                    report_version_id INTEGER,
                    sent_to TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    email_subject TEXT,
                    email_status TEXT DEFAULT 'sent',
                    error_message TEXT,
                    FOREIGN KEY (scheduled_report_id) REFERENCES scheduled_reports(id),
                    FOREIGN KEY (report_version_id) REFERENCES report_versions(id)
                );

--- Table: report_history ---
CREATE TABLE report_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                template_key TEXT NOT NULL,
                output_format TEXT NOT NULL,
                output_path TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                meta TEXT,             -- JSON: ek bilgiler
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );

--- Table: report_metrics ---
CREATE TABLE report_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id INTEGER NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value DECIMAL(15,4),
                    metric_unit VARCHAR(50),
                    metric_type VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES reports(id)
                );

--- Table: report_registry ---
CREATE TABLE report_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    reporting_period TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    tags TEXT,
                    description TEXT
                );

--- Table: report_schedules ---
CREATE TABLE report_schedules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    schedule_name VARCHAR(100) NOT NULL,
                    frequency VARCHAR(20) NOT NULL,
                    frequency_value INTEGER,
                    start_date DATE,
                    end_date DATE,
                    time_of_day TIME,
                    recipients TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, company_id INTEGER, updated_at TIMESTAMP, deleted_at TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES report_templates(id)
                );

--- Table: report_templates ---
CREATE TABLE report_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    template_type VARCHAR(20) NOT NULL,
                    data_source VARCHAR(100),
                    template_config TEXT,
                    output_formats TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: report_versions ---
CREATE TABLE report_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    checksum TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_current BOOLEAN DEFAULT 1,
                    change_notes TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: reports ---
CREATE TABLE reports (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL,
  type TEXT NOT NULL,                  -- sdg | sdg_gri | sdg_gri_tsrs
  period TEXT NOT NULL,
  payload_json TEXT,                   -- oluşturma parametreleri
  file_path TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP, is_locked INTEGER DEFAULT 0, deleted_at TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
);

--- Table: reset_tokens ---
CREATE TABLE reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_hash TEXT NOT NULL,
                requested_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts_left INTEGER NOT NULL DEFAULT 5,
                used_at TEXT,
                request_ip TEXT,
                sent_via TEXT DEFAULT 'email',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id)
            );

--- Table: responses ---
CREATE TABLE responses (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL,
  indicator_id INTEGER NOT NULL,
  period TEXT NOT NULL,                -- 2024, 2024Q1 vb.
  answer_json TEXT,                    -- soru-yanıt seti
  value_num REAL,                      -- sayısal ana KPI (opsiyonel)
  progress_pct INTEGER DEFAULT 0,
  request_status TEXT DEFAULT 'Gönderilmedi',  -- Gönderildi/İncelemede/Cevaplandı
  policy_flag TEXT DEFAULT 'Hayır',            -- Politika/Belge Var mı? (Evet/Hayır)
  evidence_url TEXT,
  approved_by_owner TEXT,              -- E/H
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP, response TEXT,
  FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
  FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE,
  UNIQUE(company_id, indicator_id, period)
);

--- Table: risk_assessments ---
CREATE TABLE risk_assessments (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            risk_category TEXT NOT NULL, -- Doğal, Teknolojik, İnsan, Finansal
            risk_description TEXT NOT NULL,
            probability_score INTEGER, -- Olasılık skoru (1-5)
            impact_score INTEGER, -- Etki skoru (1-5)
            risk_level TEXT, -- Düşük, Orta, Yüksek, Kritik
            mitigation_measures TEXT, -- Azaltma önlemleri
            responsible_person TEXT, -- Sorumlu kişi
            review_date TEXT, -- İnceleme tarihi
            status TEXT DEFAULT 'active', -- active, mitigated, closed
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: risk_opportunity_matrix ---
CREATE TABLE risk_opportunity_matrix (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    matrix_name TEXT NOT NULL,
                    description TEXT,
                    matrix_data TEXT NOT NULL, -- JSON matrix data
                    assessment_date TEXT NOT NULL,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: risks ---
CREATE TABLE risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_name TEXT NOT NULL,
            category TEXT,
            likelihood INTEGER,
            impact INTEGER,
            score INTEGER,
            mitigation TEXT,
            owner TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

--- Table: role_permissions ---
CREATE TABLE "role_permissions" (id INTEGER PRIMARY KEY AUTOINCREMENT, role_id INTEGER NOT NULL, permission_id INTEGER NOT NULL, granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, granted_by INTEGER, FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE, FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE, FOREIGN KEY (granted_by) REFERENCES users(id), UNIQUE(role_id, permission_id));

--- Table: roles ---
CREATE TABLE roles (
  id INTEGER PRIMARY KEY,
  name TEXT UNIQUE NOT NULL            -- super_admin, admin, user
, display_name VARCHAR(100) DEFAULT '', description TEXT, is_system_role BOOLEAN DEFAULT 0, is_active BOOLEAN DEFAULT 1, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, created_by INTEGER, updated_by INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

--- Table: safety_audits ---
CREATE TABLE safety_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    audit_date TEXT NOT NULL,
                    audit_type TEXT NOT NULL,
                    auditor_name TEXT,
                    audit_scope TEXT,
                    compliance_score REAL,
                    non_conformities INTEGER,
                    observations INTEGER,
                    recommendations INTEGER,
                    follow_up_date TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: safety_incidents ---
CREATE TABLE safety_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    incident_date TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity_level TEXT NOT NULL,
                    location TEXT,
                    department TEXT,
                    employee_id INTEGER,
                    description TEXT,
                    root_cause TEXT,
                    corrective_actions TEXT,
                    prevention_measures TEXT,
                    lost_work_days INTEGER,
                    medical_treatment TEXT,
                    investigation_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: safety_kpis ---
CREATE TABLE safety_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    kpi_name TEXT NOT NULL,
                    kpi_value REAL NOT NULL,
                    kpi_unit TEXT NOT NULL,
                    benchmark_value REAL,
                    target_value REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: safety_targets ---
CREATE TABLE safety_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: safety_trainings ---
CREATE TABLE safety_trainings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    training_date TEXT NOT NULL,
                    training_type TEXT NOT NULL,
                    training_topic TEXT NOT NULL,
                    trainer_name TEXT,
                    participant_count INTEGER NOT NULL,
                    duration_hours REAL,
                    training_method TEXT,
                    assessment_score REAL,
                    certification_validity TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: sasb_disclosure_topics ---
CREATE TABLE sasb_disclosure_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id INTEGER NOT NULL,
    topic_code TEXT NOT NULL,              -- Örn: GHG-EM, DATA-SEC
    topic_name TEXT NOT NULL,              -- Örn: GHG Emissions, Data Security
    category TEXT,                         -- Environment, Social Capital, Human Capital, Business Model, Leadership
    is_material INTEGER DEFAULT 1,         -- Bu sektör için materyal mi?
    description TEXT,
    FOREIGN KEY (sector_id) REFERENCES sasb_sectors(id) ON DELETE CASCADE
);

--- Table: sasb_financial_materiality ---
CREATE TABLE sasb_financial_materiality (
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

--- Table: sasb_gri_mapping ---
CREATE TABLE sasb_gri_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sasb_metric_code TEXT NOT NULL,
    gri_standard TEXT,                     -- Örn: GRI 305
    gri_disclosure TEXT,                   -- Örn: 305-1
    mapping_strength TEXT,                 -- Strong, Moderate, Weak
    notes TEXT
);

--- Table: sasb_industries ---
CREATE TABLE sasb_industries (
            id INTEGER PRIMARY KEY,
            industry_code TEXT,
            industry_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: sasb_materiality ---
CREATE TABLE sasb_materiality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            sector_id INTEGER,
            topic_id INTEGER,
            materiality_score INTEGER DEFAULT 0,
            disclosure_quality INTEGER DEFAULT 0,
            impact_level TEXT DEFAULT 'medium',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );

--- Table: sasb_metric_responses ---
CREATE TABLE sasb_metric_responses (
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
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP, response TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (metric_id) REFERENCES sasb_metrics(id) ON DELETE CASCADE
);

--- Table: sasb_metrics ---
CREATE TABLE sasb_metrics (
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

--- Table: sasb_sectors ---
CREATE TABLE sasb_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_code TEXT NOT NULL UNIQUE,      -- Örn: TC-SI, HC-BP
    sector_name TEXT NOT NULL,             -- Örn: Software & IT Services, Biotechnology & Pharmaceuticals
    industry_group TEXT NOT NULL,          -- Örn: Technology & Communications, Healthcare
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

--- Table: scenario_analyses ---
CREATE TABLE scenario_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scenario_name TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    base_year INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    description TEXT,
                    assumptions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: scenario_comparisons ---
CREATE TABLE scenario_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    comparison_name TEXT NOT NULL,
                    base_scenario_id INTEGER NOT NULL,
                    alternative_scenario_id INTEGER NOT NULL,
                    comparison_metrics TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (base_scenario_id) REFERENCES scenario_analyses(id),
                    FOREIGN KEY (alternative_scenario_id) REFERENCES scenario_analyses(id)
                );

--- Table: scheduled_reports ---
CREATE TABLE scheduled_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    schedule_frequency TEXT NOT NULL,
                    schedule_day INTEGER,
                    schedule_time TEXT,
                    last_generated TIMESTAMP,
                    next_generation TIMESTAMP,
                    email_recipients TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: scheduler_job_history ---
CREATE TABLE scheduler_job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scheduled_report_id INTEGER NOT NULL,
                    job_run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success',
                    execution_time_seconds REAL,
                    error_message TEXT,
                    report_version_id INTEGER,
                    FOREIGN KEY (scheduled_report_id) REFERENCES scheduled_reports(id),
                    FOREIGN KEY (report_version_id) REFERENCES report_versions(id)
                );

--- Table: scope3_categories ---
CREATE TABLE scope3_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_number INTEGER UNIQUE NOT NULL,
                    category_name TEXT NOT NULL,
                    description TEXT,
                    scope_type TEXT DEFAULT 'Indirect',
                    is_upstream BOOLEAN DEFAULT 1,
                    is_downstream BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: scope3_emissions ---
CREATE TABLE scope3_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    activity_data REAL,
                    activity_unit TEXT,
                    emission_factor REAL,
                    emission_factor_unit TEXT,
                    total_emissions REAL,
                    reporting_period TEXT,
                    data_source TEXT,
                    methodology TEXT,
                    uncertainty_level TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id),
                    FOREIGN KEY(category_id) REFERENCES scope3_categories(id)
                );

--- Table: scope3_targets ---
CREATE TABLE scope3_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    category_id INTEGER,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    target_year INTEGER,
                    baseline_emissions REAL,
                    target_emissions REAL,
                    reduction_percentage REAL,
                    target_description TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id),
                    FOREIGN KEY(category_id) REFERENCES scope3_categories(id)
                );

--- Table: sdg10_inequality_data ---
CREATE TABLE sdg10_inequality_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, wage_gap_ratio REAL, disabled_employee_count REAL, diversity_programs TEXT, equal_opportunity_policies REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg11_cities_data ---
CREATE TABLE sdg11_cities_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, green_building_ratio REAL, public_transport_usage REAL, community_development_projects TEXT, urban_infrastructure_investment REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg12_consumption_data ---
CREATE TABLE sdg12_consumption_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, total_waste REAL, hazardous_waste REAL, recycled_waste REAL, recycling_rate REAL, circular_economy_projects TEXT, waste_reduction_target REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg13_climate_data ---
CREATE TABLE sdg13_climate_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, scope1_emissions REAL, scope2_emissions REAL, scope3_emissions REAL, total_emissions REAL, emission_intensity REAL, climate_action_plan TEXT, carbon_neutrality_target_year REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg14_ocean_data ---
CREATE TABLE sdg14_ocean_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, marine_protection_projects TEXT, ocean_pollution_prevention REAL, sustainable_fishery_support REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg15_biodiversity_data ---
CREATE TABLE sdg15_biodiversity_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, land_conservation_area REAL, reforestation_area REAL, biodiversity_projects TEXT, habitat_protection REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg16_peace_data ---
CREATE TABLE sdg16_peace_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, anticorruption_training REAL, ethics_policy TEXT, transparency_score REAL, grievance_mechanism REAL, corruption_incidents REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg17_partnership_data ---
CREATE TABLE sdg17_partnership_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, partnerships_count REAL, ngo_collaborations REAL, public_private_partnerships REAL, knowledge_sharing_platforms REAL, sdg_investment REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg2_hunger_data ---
CREATE TABLE sdg2_hunger_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, food_security_programs TEXT, agricultural_support REAL, nutrition_programs TEXT, local_food_procurement REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg3_health_data ---
CREATE TABLE sdg3_health_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, health_insurance_coverage REAL, occupational_health_programs TEXT, mental_health_support REAL, health_safety_training_hours REAL, workplace_accidents REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg4_education_data ---
CREATE TABLE sdg4_education_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, training_hours_total REAL, training_hours_per_employee REAL, training_investment REAL, scholarship_programs TEXT, intern_count REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg5_gender_data ---
CREATE TABLE sdg5_gender_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, female_employee_ratio REAL, female_management_ratio REAL, gender_pay_gap REAL, parental_leave_days REAL, gender_equality_programs TEXT, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg6_water_data ---
CREATE TABLE sdg6_water_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, water_consumption_total REAL, water_recycled REAL, water_recycling_rate REAL, wastewater_treatment REAL, water_saving_projects TEXT, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg8_employment_data ---
CREATE TABLE sdg8_employment_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, total_employees REAL, new_hires REAL, turnover_rate REAL, permanent_employees REAL, temporary_employees REAL, parttime_employees REAL, average_wage REAL, economic_value_generated REAL, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg9_innovation_data ---
CREATE TABLE sdg9_innovation_data (id INTEGER PRIMARY KEY, company_id INTEGER, task_id INTEGER, reporting_year TEXT, rd_investment REAL, rd_investment_ratio REAL, patent_count REAL, innovation_projects TEXT, digital_transformation_projects TEXT, notes TEXT, is_draft INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

--- Table: sdg_data_quality_scores ---
CREATE TABLE sdg_data_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                completeness_score REAL DEFAULT 0.0,
                accuracy_score REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,
                timeliness_score REAL DEFAULT 0.0,
                overall_quality_score REAL DEFAULT 0.0,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_goal_performance_scores ---
CREATE TABLE sdg_goal_performance_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                performance_score REAL NOT NULL,
                improvement_rate REAL DEFAULT 0.0,
                benchmark_score REAL,
                industry_average REAL,
                measurement_date TEXT NOT NULL,
                calculation_method TEXT DEFAULT 'weighted_average',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_goal_progress ---
CREATE TABLE sdg_goal_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                sdg_title TEXT NOT NULL,
                total_indicators INTEGER DEFAULT 0,
                completed_indicators INTEGER DEFAULT 0,
                in_progress_indicators INTEGER DEFAULT 0,
                not_started_indicators INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                UNIQUE(company_id, sdg_no)
            );

--- Table: sdg_goals ---
CREATE TABLE sdg_goals (
  id INTEGER PRIMARY KEY,
  code INTEGER NOT NULL UNIQUE,        -- 1..17
  title_tr TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

--- Table: sdg_indicator_analytics ---
CREATE TABLE sdg_indicator_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                completion_score REAL DEFAULT 0.0,
                quality_score REAL DEFAULT 0.0,
                timeliness_score REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,
                overall_score REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                trend_direction TEXT DEFAULT 'stable',
                risk_level TEXT DEFAULT 'low',
                priority_level TEXT DEFAULT 'medium',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_indicator_progress_details ---
CREATE TABLE sdg_indicator_progress_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                target_code TEXT NOT NULL,
                target_title TEXT NOT NULL,
                question_1_status TEXT DEFAULT 'not_answered',
                question_2_status TEXT DEFAULT 'not_answered',
                question_3_status TEXT DEFAULT 'not_answered',
                question_1_answer_date TEXT,
                question_2_answer_date TEXT,
                question_3_answer_date TEXT,
                completion_percentage REAL DEFAULT 0.0,
                last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_indicator_status ---
CREATE TABLE sdg_indicator_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                target_code TEXT NOT NULL,
                target_title TEXT NOT NULL,
                question_1_answered BOOLEAN DEFAULT FALSE,
                question_2_answered BOOLEAN DEFAULT FALSE,
                question_3_answered BOOLEAN DEFAULT FALSE,
                total_questions INTEGER DEFAULT 3,
                answered_questions INTEGER DEFAULT 0,
                completion_percentage REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_indicators ---
CREATE TABLE sdg_indicators (
  id INTEGER PRIMARY KEY,
  target_id INTEGER NOT NULL,
  code TEXT NOT NULL,                  -- 1.1.1, 7.2.1 ...
  title_tr TEXT NOT NULL,
  unit TEXT,                           -- % , tCO2e, m3 vb.
  frequency TEXT DEFAULT 'Yıllık',
  topic TEXT,                          -- enerji, emisyon, su...
  FOREIGN KEY(target_id) REFERENCES sdg_targets(id) ON DELETE CASCADE,
  UNIQUE(target_id, code)
);

--- Table: sdg_kpi_metrics ---
CREATE TABLE sdg_kpi_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                kpi_name TEXT NOT NULL,
                metric_description TEXT,
                measurement_frequency TEXT,
                data_source TEXT,
                target_value REAL,
                current_value REAL,
                unit TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: sdg_performance_metrics ---
CREATE TABLE sdg_performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                measurement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                target_value REAL,
                actual_vs_target REAL,
                improvement_rate REAL,
                benchmark_value REAL,
                industry_percentile REAL,
                calculation_method TEXT,
                data_source TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_performance_metrics_detailed ---
CREATE TABLE sdg_performance_metrics_detailed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                metric_category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                target_value REAL,
                actual_vs_target REAL,
                improvement_rate REAL,
                benchmark_value REAL,
                industry_percentile REAL,
                measurement_date TEXT NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                calculation_method TEXT,
                data_source TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_progress_trends ---
CREATE TABLE sdg_progress_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                measurement_date TEXT NOT NULL,
                completion_percentage REAL NOT NULL,
                answered_questions INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                new_answers INTEGER DEFAULT 0,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_question_bank ---
CREATE TABLE sdg_question_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_text TEXT NOT NULL,
                question_type_id INTEGER NOT NULL,
                difficulty_level TEXT DEFAULT 'medium',
                is_required BOOLEAN DEFAULT 1,
                points INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP, validation_rules TEXT, help_text TEXT, options TEXT, correct_answer TEXT,
                FOREIGN KEY (question_type_id) REFERENCES sdg_question_types(id)
            );

--- Table: sdg_question_categories ---
CREATE TABLE sdg_question_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: sdg_question_responses ---
CREATE TABLE sdg_question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                response_text TEXT,
                response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                is_validated BOOLEAN DEFAULT 0,
                validation_notes TEXT,
                FOREIGN KEY (question_id) REFERENCES sdg_question_bank(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_question_types ---
CREATE TABLE sdg_question_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT UNIQUE NOT NULL,
                description TEXT,
                input_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            , validation_rules TEXT);

--- Table: sdg_responses ---
CREATE TABLE sdg_responses (
            id INTEGER PRIMARY KEY,
            company_id INTEGER,
            indicator_id INTEGER,
            value REAL,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: sdg_revision_metadata ---
CREATE TABLE sdg_revision_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    revision_year INTEGER NOT NULL,
                    revision_date DATE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    applied_by VARCHAR(100),
                    backup_path TEXT,
                    changes_summary TEXT,
                    notes TEXT
                );

--- Table: sdg_risk_analysis ---
CREATE TABLE sdg_risk_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                risk_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_description TEXT,
                mitigation_strategy TEXT,
                impact_assessment TEXT,
                probability_assessment TEXT,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_targets ---
CREATE TABLE sdg_targets (
  id INTEGER PRIMARY KEY,
  goal_id INTEGER NOT NULL,
  code TEXT NOT NULL,                  -- 1.1, 7.2, ...
  title_tr TEXT NOT NULL,
  FOREIGN KEY(goal_id) REFERENCES sdg_goals(id) ON DELETE CASCADE,
  UNIQUE(goal_id, code)
);

--- Table: sdg_trend_analysis ---
CREATE TABLE sdg_trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                analysis_period TEXT NOT NULL,
                trend_type TEXT NOT NULL,
                trend_strength REAL NOT NULL,
                trend_direction TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                forecast_value REAL,
                forecast_date TEXT,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_validation_results ---
CREATE TABLE sdg_validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                rule_id INTEGER NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                validation_status TEXT NOT NULL,
                error_message TEXT,
                suggested_fix TEXT,
                severity_level TEXT,
                FOREIGN KEY (rule_id) REFERENCES sdg_validation_rules(id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: sdg_validation_rules ---
CREATE TABLE sdg_validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_description TEXT,
                validation_expression TEXT NOT NULL,
                error_message TEXT,
                severity_level TEXT DEFAULT 'warning',
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: sections ---
CREATE TABLE sections (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          department_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
          FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE,
          UNIQUE(company_id, department_id, name)
        );

--- Table: sector_averages ---
CREATE TABLE sector_averages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector_code TEXT NOT NULL,
                    sector_name TEXT NOT NULL,
                    metric_code TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_category TEXT NOT NULL,
                    average_value REAL NOT NULL,
                    median_value REAL,
                    min_value REAL,
                    max_value REAL,
                    std_deviation REAL,
                    unit TEXT,
                    sample_size INTEGER,
                    data_year INTEGER NOT NULL,
                    data_source TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sector_code, metric_code, data_year)
                );

--- Table: sector_trends ---
CREATE TABLE sector_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector_code TEXT NOT NULL,
                    metric_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    value REAL NOT NULL,
                    yoy_change REAL,
                    trend_direction TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(sector_code, metric_code, year)
                );

--- Table: security_audit_log ---
CREATE TABLE security_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                actor TEXT,
                action TEXT,
                details TEXT
            );

--- Table: security_audit_logs ---
CREATE TABLE security_audit_logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                username TEXT,
                event TEXT NOT NULL,
                ok INTEGER,
                meta TEXT
            );

--- Table: security_events ---
CREATE TABLE security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_description TEXT,
                    severity TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    additional_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, description TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: security_logs ---
CREATE TABLE security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                event_type TEXT,
                success INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: security_settings ---
CREATE TABLE security_settings (
                    id INTEGER PRIMARY KEY,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: selections ---
CREATE TABLE selections (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL,
  goal_id INTEGER,
  target_id INTEGER,
  indicator_id INTEGER,
  selected INTEGER DEFAULT 0,          -- 0/1
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
  FOREIGN KEY(goal_id) REFERENCES sdg_goals(id),
  FOREIGN KEY(target_id) REFERENCES sdg_targets(id),
  FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id)
);

--- Table: session_actions ---
CREATE TABLE session_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    action_description TEXT,
                    module_name TEXT,
                    ip_address TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES session_recordings(session_id)
                );

--- Table: session_recordings ---
CREATE TABLE session_recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    login_time DATETIME,
                    logout_time DATETIME,
                    actions_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: settings ---
CREATE TABLE settings (
  id INTEGER PRIMARY KEY,
  key TEXT UNIQUE NOT NULL,
  value TEXT
);

--- Table: skdm_carbon ---
CREATE TABLE skdm_carbon (
            id INTEGER PRIMARY KEY,
            category TEXT,
            value REAL,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: skdm_carbon_management ---
CREATE TABLE skdm_carbon_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_emissions REAL NOT NULL,
                    scope1_emissions REAL DEFAULT 0,
                    scope2_emissions REAL DEFAULT 0,
                    scope3_emissions REAL DEFAULT 0,
                    reduction_target REAL,
                    reduction_achieved REAL DEFAULT 0,
                    carbon_price REAL,
                    offset_purchased REAL DEFAULT 0,
                    renewable_energy_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_emission_projects ---
CREATE TABLE skdm_emission_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    expected_reduction REAL NOT NULL,
                    actual_reduction REAL DEFAULT 0,
                    investment_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Planning',
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_scope3_categories ---
CREATE TABLE skdm_scope3_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category_code TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    emissions REAL NOT NULL,
                    data_quality TEXT DEFAULT 'Low',
                    calculation_method TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_stakeholder_management ---
CREATE TABLE skdm_stakeholder_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    engagement_level TEXT DEFAULT 'Low',
                    satisfaction_score INTEGER DEFAULT 0,
                    last_contact_date DATE,
                    next_contact_date DATE,
                    key_concerns TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_stakeholders ---
CREATE TABLE skdm_stakeholders (
            id INTEGER PRIMARY KEY,
            name TEXT,
            group_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: skdm_suppliers ---
CREATE TABLE skdm_suppliers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            risk_level TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: skdm_supply_chain ---
CREATE TABLE skdm_supply_chain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    suppliers_assessed INTEGER DEFAULT 0,
                    suppliers_sustainable_percentage REAL DEFAULT 0,
                    supply_chain_emissions REAL DEFAULT 0,
                    supplier_audits INTEGER DEFAULT 0,
                    ethical_sourcing_score INTEGER DEFAULT 0,
                    local_sourcing_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_waste ---
CREATE TABLE skdm_waste (
            id INTEGER PRIMARY KEY,
            waste_type TEXT,
            amount REAL,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: skdm_waste_management ---
CREATE TABLE skdm_waste_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_waste_generated REAL NOT NULL,
                    waste_recycled_percentage REAL DEFAULT 0,
                    waste_reduced_percentage REAL DEFAULT 0,
                    hazardous_waste_percentage REAL DEFAULT 0,
                    circular_economy_score INTEGER DEFAULT 0,
                    waste_to_energy_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: skdm_water ---
CREATE TABLE skdm_water (
            id INTEGER PRIMARY KEY,
            metric TEXT,
            value REAL,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: skdm_water_management ---
CREATE TABLE skdm_water_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_water_consumption REAL NOT NULL,
                    water_reuse_percentage REAL DEFAULT 0,
                    water_efficiency_score INTEGER DEFAULT 0,
                    water_risk_level TEXT DEFAULT 'Low',
                    water_conservation_projects INTEGER DEFAULT 0,
                    wastewater_treatment_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: smart_goals ---
CREATE TABLE smart_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    goal_title TEXT NOT NULL,
                    description TEXT,
                    goal_category TEXT NOT NULL, -- 'strategic', 'operational', 'sustainability', 'financial'
                    goal_owner TEXT NOT NULL, -- person responsible
                    department TEXT NOT NULL,
                    
                    -- SMART Criteria
                    specific_description TEXT NOT NULL, -- What exactly will be accomplished?
                    measurable_metrics TEXT NOT NULL, -- How will success be measured?
                    achievable_rationale TEXT NOT NULL, -- Why is this goal achievable?
                    relevant_justification TEXT NOT NULL, -- Why is this goal important?
                    time_bound_deadline TEXT NOT NULL, -- When will this be completed?
                    
                    -- Goal Details
                    baseline_value REAL,
                    target_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    measurement_frequency TEXT DEFAULT 'monthly', -- 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
                    data_source TEXT, -- Where will data come from?
                    
                    -- Status and Progress
                    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'on_track', 'at_risk', 'completed', 'cancelled'
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
                    start_date TEXT NOT NULL,
                    target_date TEXT NOT NULL,
                    completion_date TEXT,
                    
                    -- Alignment
                    aligned_with_strategy TEXT, -- strategy name or reference
                    supports_sdg TEXT, -- JSON array of SDG numbers
                    supports_gri TEXT, -- JSON array of GRI indicators
                    supports_tsrs TEXT, -- JSON array of TSRS indicators
                    
                    -- Tracking
                    current_value REAL,
                    progress_percentage REAL DEFAULT 0,
                    last_updated TEXT,
                    next_review_date TEXT,
                    
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                );

--- Table: sqlite_sequence ---
CREATE TABLE sqlite_sequence(name,seq);

--- Table: sqlite_stat1 ---
CREATE TABLE sqlite_stat1(tbl,idx,stat);

--- Table: stakeholder_action_plans ---
CREATE TABLE stakeholder_action_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    owner TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'open',            -- open, in_progress, closed
                    stakeholder_id INTEGER,
                    engagement_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id),
                    FOREIGN KEY (engagement_id) REFERENCES stakeholder_engagements(id)
                );

--- Table: stakeholder_commitments ---
CREATE TABLE stakeholder_commitments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    meeting_id INTEGER,
                    commitment_title TEXT NOT NULL,
                    commitment_description TEXT,
                    responsible_person TEXT,
                    target_stakeholder_group TEXT,
                    due_date DATE,
                    priority TEXT DEFAULT 'orta',
                    status TEXT DEFAULT 'acik',
                    progress_percentage INTEGER DEFAULT 0,
                    completion_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (meeting_id) REFERENCES stakeholder_meetings(id)
                );

--- Table: stakeholder_communication_plans ---
CREATE TABLE stakeholder_communication_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    communication_channel TEXT NOT NULL,   -- Email, Toplantı, Webinar, Rapor, etc.
                    frequency TEXT,                        -- Haftalık, Aylık, Çeyreklik
                    owner TEXT,                            -- Sorumlu kişi/birim
                    next_action TEXT,                      -- Bir sonraki adım
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                );

--- Table: stakeholder_complaints ---
CREATE TABLE stakeholder_complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    complaint_date TEXT NOT NULL,
                    channel TEXT,                          -- Email, Telefon, Portal, etc.
                    description TEXT NOT NULL,
                    severity TEXT,                         -- Düşük/Orta/Yüksek
                    status TEXT DEFAULT 'open',
                    resolution TEXT,
                    resolved_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                );

--- Table: stakeholder_engagements ---
CREATE TABLE stakeholder_engagements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER NOT NULL,
                    engagement_date TEXT NOT NULL,
                    engagement_type TEXT NOT NULL,
                    engagement_topic TEXT NOT NULL,
                    participants TEXT,
                    outcomes TEXT,
                    follow_up_actions TEXT,
                    satisfaction_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                );

--- Table: stakeholder_feedback ---
CREATE TABLE stakeholder_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    feedback_type TEXT NOT NULL,
                    feedback_category TEXT,
                    feedback_text TEXT NOT NULL,
                    rating INTEGER,
                    attachment_path TEXT,
                    status TEXT DEFAULT 'yeni',
                    responded_by INTEGER,
                    response_text TEXT,
                    responded_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                );

--- Table: stakeholder_meetings ---
CREATE TABLE stakeholder_meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    meeting_title TEXT NOT NULL,
                    meeting_type TEXT NOT NULL,
                    meeting_date DATETIME NOT NULL,
                    duration_minutes INTEGER DEFAULT 60,
                    location TEXT,
                    meeting_link TEXT,
                    agenda TEXT,
                    participants TEXT,
                    minutes_of_meeting TEXT,
                    action_items TEXT,
                    status TEXT DEFAULT 'planlandı',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: stakeholder_prioritization_scores ---
CREATE TABLE stakeholder_prioritization_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_id INTEGER NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    priority_score REAL NOT NULL,
                    weighted_score REAL NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
                );

--- Table: stakeholder_survey_templates ---
CREATE TABLE stakeholder_survey_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    stakeholder_category TEXT,
                    questions_json TEXT NOT NULL,          -- JSON soru listesi
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: stakeholder_surveys ---
CREATE TABLE stakeholder_surveys (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            survey_name TEXT NOT NULL,
            stakeholder_category TEXT NOT NULL,
            survey_data TEXT, -- JSON format
            total_responses INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

--- Table: stakeholder_weights ---
CREATE TABLE stakeholder_weights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    weight REAL NOT NULL,
                    influence_level TEXT NOT NULL,
                    engagement_frequency TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: stakeholders ---
CREATE TABLE stakeholders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    contact_person TEXT,
                    contact_email TEXT,
                    contact_phone TEXT,
                    organization TEXT,
                    sector TEXT,
                    influence_level TEXT,
                    interest_level TEXT,
                    engagement_frequency TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP, portal_enabled BOOLEAN DEFAULT 0,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: standard_mappings ---
CREATE TABLE standard_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_standard TEXT NOT NULL,
            source_code TEXT NOT NULL,
            source_title TEXT,
            source_description TEXT,
            target_standard TEXT NOT NULL,
            target_code TEXT NOT NULL,
            target_title TEXT,
            target_description TEXT,
            mapping_type TEXT DEFAULT 'direct',
            mapping_strength TEXT DEFAULT 'strong',
            notes TEXT,
            verified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

--- Table: strategic_goals ---
CREATE TABLE strategic_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    goal_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    goal_title TEXT NOT NULL,
                    description TEXT,
                    target_year INTEGER,
                    baseline_year INTEGER,
                    baseline_value REAL,
                    target_value REAL,
                    unit TEXT,
                    measurement_frequency TEXT DEFAULT 'annual', -- 'monthly', 'quarterly', 'annual'
                    responsible_department TEXT,
                    kpi_formula TEXT,
                    progress_tracking_method TEXT,
                    is_critical INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active', -- 'active', 'completed', 'paused', 'cancelled'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                );

--- Table: strategic_initiatives ---
CREATE TABLE strategic_initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    description TEXT,
                    category TEXT, -- 'program', 'project', 'partnership', 'investment'
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
                    start_date TEXT,
                    end_date TEXT,
                    budget REAL,
                    responsible_department TEXT,
                    expected_outcomes TEXT, -- JSON array
                    success_metrics TEXT, -- JSON array
                    status TEXT DEFAULT 'planned', -- 'planned', 'active', 'completed', 'cancelled'
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                );

--- Table: strategies ---
CREATE TABLE strategies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vision TEXT,
            mission TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

--- Table: strategy_assessments ---
CREATE TABLE strategy_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessment_type TEXT NOT NULL, -- 'quarterly', 'annual', 'mid_term', 'final'
                    overall_progress REAL, -- percentage
                    strengths TEXT, -- JSON array
                    weaknesses TEXT, -- JSON array
                    opportunities TEXT, -- JSON array
                    threats TEXT, -- JSON array
                    recommendations TEXT, -- JSON array
                    assessed_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (strategy_id) REFERENCES sustainability_strategies(id)
                );

--- Table: supplier_assessments ---
CREATE TABLE supplier_assessments (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    assessment_date DATE NOT NULL,
                    assessment_period TEXT,          -- 2024-Q1, 2024, etc.
                    environmental_score REAL,        -- 0-100
                    social_score REAL,               -- 0-100
                    governance_score REAL,           -- 0-100
                    quality_score REAL,              -- 0-100
                    total_score REAL NOT NULL,       -- Ağırlıklı toplam (0-100)
                    risk_level TEXT,                 -- low, medium, high, critical
                    responses_json TEXT,             -- Detaylı cevaplar
                    strengths TEXT,                  -- Güçlü yönler (JSON)
                    weaknesses TEXT,                 -- Zayıf yönler (JSON)
                    recommendation TEXT,             -- Öneri
                    next_assessment_date DATE,
                    assessed_by TEXT,
                    approved_by TEXT,
                    approved_at TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                );

--- Table: supplier_audits ---
CREATE TABLE supplier_audits (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    audit_date DATE NOT NULL,
                    audit_type TEXT,                 -- scheduled, unannounced, follow_up
                    audit_focus TEXT,                -- environmental, social, quality, all
                    auditor_name TEXT,
                    findings_count INTEGER DEFAULT 0,
                    critical_findings INTEGER DEFAULT 0,
                    major_findings INTEGER DEFAULT 0,
                    minor_findings INTEGER DEFAULT 0,
                    audit_result TEXT,               -- pass, conditional, fail
                    corrective_actions TEXT,         -- JSON
                    follow_up_required BOOLEAN DEFAULT 0,
                    follow_up_date DATE,
                    audit_report_file TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                );

--- Table: supplier_performance ---
CREATE TABLE supplier_performance (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    on_time_delivery_pct REAL,       -- Zamanında teslimat %
                    quality_reject_rate REAL,        -- Kalite red oranı %
                    response_time_hours REAL,        -- Ortalama yanıt süresi (saat)
                    price_competitiveness REAL,      -- Fiyat rekabetçiliği (1-10)
                    flexibility_score REAL,          -- Esneklik skoru (1-10)
                    innovation_score REAL,           -- İnovasyon skoru (1-10)
                    overall_satisfaction REAL,       -- Genel memnuniyet (1-10)
                    issues_count INTEGER DEFAULT 0,
                    complaints_count INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                );

--- Table: suppliers ---
CREATE TABLE suppliers (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    supplier_code TEXT UNIQUE,
                    supplier_name TEXT NOT NULL,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    country TEXT,
                    city TEXT,
                    supplier_type TEXT,              -- raw_material, service, logistics, etc.
                    category TEXT,                   -- strategic, preferred, standard
                    is_local BOOLEAN DEFAULT 0,      -- Yerel tedarikçi mi?
                    annual_spend REAL,               -- Yıllık harcama
                    spend_currency TEXT DEFAULT 'TRY',
                    payment_terms TEXT,              -- Ödeme koşulları
                    contract_start_date DATE,
                    contract_end_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: supply_chain_metrics ---
CREATE TABLE supply_chain_metrics (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    total_suppliers_count INTEGER,
                    active_suppliers_count INTEGER,
                    local_suppliers_count INTEGER,
                    local_supplier_pct REAL,         -- Yerel tedarikçi oranı (%)
                    sustainable_suppliers_count INTEGER,
                    sustainable_supplier_pct REAL,   -- Sürdürülebilir tedarikçi oranı (%)
                    total_procurement_spend REAL,
                    local_procurement_spend REAL,
                    avg_supplier_score REAL,         -- Ortalama tedarikçi skoru
                    high_risk_suppliers_count INTEGER,
                    new_suppliers_added INTEGER,
                    suppliers_terminated INTEGER,
                    supplier_audit_count INTEGER,
                    child_labor_risk_assessed BOOLEAN DEFAULT 0,
                    supply_chain_carbon_footprint REAL,  -- tCO2e
                    sustainable_packaging_pct REAL,  -- Sürdürülebilir ambalaj oranı
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, period)
                );

--- Table: survey_answers ---
CREATE TABLE survey_answers (
                    id INTEGER PRIMARY KEY,
                    response_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT,
                    answer_number REAL,
                    answer_choice TEXT,
                    FOREIGN KEY (response_id) REFERENCES survey_responses(id),
                    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
                );

--- Table: survey_assignments ---
CREATE TABLE survey_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_id INTEGER NOT NULL,
                    assigned_to INTEGER NOT NULL,
                    assigned_by INTEGER,
                    due_date TEXT,
                    status TEXT DEFAULT 'Bekliyor',
                    completed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (survey_id) REFERENCES surveys(id)
                );

--- Table: survey_questions ---
CREATE TABLE survey_questions (
                    id INTEGER PRIMARY KEY,
                    survey_id INTEGER NOT NULL,
                    q_type TEXT DEFAULT 'text',
                    text TEXT NOT NULL,
                    options_json TEXT,
                    required INTEGER DEFAULT 0,
                    order_index INTEGER DEFAULT 0,
                    FOREIGN KEY (survey_id) REFERENCES surveys(id)
                );

--- Table: survey_responses ---
CREATE TABLE survey_responses (
                    id INTEGER PRIMARY KEY,
                    survey_id INTEGER NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP, response TEXT,
                    FOREIGN KEY (survey_id) REFERENCES surveys(id)
                );

--- Table: survey_stakeholders ---
CREATE TABLE survey_stakeholders (
                    stakeholder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    organization TEXT,
                    role TEXT,
                    phone TEXT,
                    category TEXT,
                    notes TEXT,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                );

--- Table: survey_templates ---
CREATE TABLE survey_templates (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        , category TEXT DEFAULT "Genel");

--- Table: surveys ---
CREATE TABLE surveys (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: sustainability_opportunities ---
CREATE TABLE sustainability_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    opportunity_title TEXT NOT NULL,
                    description TEXT,
                    opportunity_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance'
                    opportunity_type TEXT NOT NULL, -- 'innovation', 'market', 'partnership', 'efficiency', 'reputation'
                    potential_value TEXT, -- monetary or qualitative
                    probability_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'very_high'
                    implementation_effort TEXT NOT NULL, -- 'low', 'medium', 'high'
                    opportunity_score INTEGER, -- calculated from value * probability / effort
                    expected_benefits TEXT,
                    required_resources TEXT, -- JSON array
                    implementation_plan TEXT, -- JSON array
                    success_metrics TEXT, -- JSON array
                    responsible_department TEXT,
                    opportunity_owner TEXT,
                    assessment_date TEXT NOT NULL,
                    target_implementation_date TEXT,
                    status TEXT DEFAULT 'identified', -- 'identified', 'evaluating', 'implementing', 'realized', 'cancelled'
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                );

--- Table: sustainability_risks ---
CREATE TABLE sustainability_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    risk_title TEXT NOT NULL,
                    description TEXT,
                    risk_category TEXT NOT NULL, -- 'environmental', 'social', 'economic', 'governance', 'operational'
                    risk_type TEXT NOT NULL, -- 'strategic', 'operational', 'financial', 'compliance', 'reputational'
                    impact_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
                    probability_level TEXT NOT NULL, -- 'low', 'medium', 'high', 'very_high'
                    risk_score INTEGER, -- calculated from impact * probability
                    potential_impact TEXT,
                    root_causes TEXT, -- JSON array
                    affected_stakeholders TEXT, -- JSON array
                    current_controls TEXT, -- JSON array
                    mitigation_measures TEXT, -- JSON array
                    responsible_department TEXT,
                    risk_owner TEXT,
                    assessment_date TEXT NOT NULL,
                    next_assessment_date TEXT,
                    status TEXT DEFAULT 'active', -- 'active', 'mitigated', 'closed', 'transferred'
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                );

--- Table: sustainability_strategies ---
CREATE TABLE sustainability_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    strategy_name TEXT NOT NULL,
                    description TEXT,
                    vision TEXT,
                    mission TEXT,
                    core_values TEXT, -- JSON array
                    strategic_pillars TEXT, -- JSON array
                    time_horizon INTEGER DEFAULT 5, -- years
                    start_year INTEGER NOT NULL,
                    end_year INTEGER NOT NULL,
                    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'completed', 'archived'
                    approval_date TEXT,
                    approved_by INTEGER,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT
                );

--- Table: sustainability_targets ---
CREATE TABLE sustainability_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_category TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    achievement_status TEXT,
                    progress_percentage REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: system_logs ---
CREATE TABLE system_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  level TEXT NOT NULL,
  module TEXT,
  message TEXT NOT NULL,
  user_id INTEGER,
  company_id INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL
);

--- Table: system_settings ---
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    data_type VARCHAR(20) DEFAULT 'string',
    is_encrypted BOOLEAN DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER, value_type TEXT DEFAULT 'string', category TEXT DEFAULT 'general', is_system INTEGER DEFAULT 0,
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

--- Table: target_forecasts ---
CREATE TABLE target_forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    target_value REAL NOT NULL,
                    target_year INTEGER NOT NULL,
                    estimated_achievement_year INTEGER,
                    probability_of_achievement REAL,
                    required_annual_change REAL,
                    risk_level TEXT,
                    recommendations TEXT,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: task_assignments ---
CREATE TABLE task_assignments (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    role TEXT DEFAULT 'assignee',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );

--- Table: task_attachments ---
CREATE TABLE task_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        uploaded_by INTEGER NOT NULL,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    );

--- Table: task_comments ---
CREATE TABLE task_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

--- Table: task_deliverables ---
CREATE TABLE task_deliverables (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER NOT NULL,
                    file_path TEXT,
                    notes TEXT,
                    submitted_by INTEGER,
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );

--- Table: task_events ---
CREATE TABLE task_events (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    data_json TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );

--- Table: task_templates ---
CREATE TABLE task_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL, -- 'SDG', 'GRI', 'TSRS'
                    indicator_code TEXT, -- 'SDG_1_1', 'GRI_302-1', 'TSRS_E1-1'
                    department TEXT NOT NULL, -- 'İnsan Kaynakları', 'Üretim', 'Satınalma'
                    task_type TEXT DEFAULT 'data_collection', -- 'data_collection', 'review', 'approval'
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
                    estimated_hours INTEGER DEFAULT 2,
                    deadline_days INTEGER DEFAULT 14, -- Kaç gün sonra deadline
                    is_recurring INTEGER DEFAULT 0, -- 0: tek seferlik, 1: tekrarlayan
                    recurring_type TEXT, -- 'monthly', 'quarterly', 'yearly'
                    form_template TEXT, -- JSON form şablonu
                    validation_rules TEXT, -- JSON validasyon kuralları
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                );

--- Table: tasks ---
CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        assigned_to INTEGER NOT NULL,
        assigned_by INTEGER,
        department_id INTEGER,
        related_module TEXT,
        related_item TEXT,
        deadline TEXT,
        priority TEXT DEFAULT 'Normal',
        status TEXT DEFAULT 'Bekliyor',
        progress INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        notes TEXT, related_item_type TEXT, company_id INTEGER, due_date TEXT, created_by INTEGER,
        FOREIGN KEY (assigned_to) REFERENCES users(id),
        FOREIGN KEY (assigned_by) REFERENCES users(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    );

--- Table: tax_contributions ---
CREATE TABLE tax_contributions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    corporate_tax REAL,
                    payroll_tax REAL,
                    vat_collected REAL,
                    property_tax REAL,
                    other_taxes REAL,
                    total_tax_paid REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: taxonomy_framework_mapping ---
CREATE TABLE taxonomy_framework_mapping (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_code VARCHAR(50) NOT NULL,
                    objective_code VARCHAR(10) NOT NULL,
                    sdg_target VARCHAR(20),
                    gri_disclosure VARCHAR(50),
                    tsrs_metric VARCHAR(50),
                    mapping_rationale TEXT,
                    FOREIGN KEY (activity_code) REFERENCES eu_taxonomy_activities(activity_code)
                );

--- Table: taxonomy_kpis ---
CREATE TABLE taxonomy_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period VARCHAR(10),
                    total_revenue DECIMAL(15,2),
                    eligible_revenue DECIMAL(15,2),
                    aligned_revenue DECIMAL(15,2),
                    total_capex DECIMAL(15,2),
                    eligible_capex DECIMAL(15,2),
                    aligned_capex DECIMAL(15,2),
                    total_opex DECIMAL(15,2),
                    eligible_opex DECIMAL(15,2),
                    aligned_opex DECIMAL(15,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: taxonomy_objective_alignment ---
CREATE TABLE taxonomy_objective_alignment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_activity_id INTEGER NOT NULL,
                    objective_code VARCHAR(10) NOT NULL,
                    substantial_contribution BOOLEAN DEFAULT 0,
                    dnsh_compliance BOOLEAN DEFAULT 0,
                    minimum_safeguards BOOLEAN DEFAULT 0,
                    evidence TEXT,
                    assessment_date DATE,
                    assessed_by VARCHAR(100),
                    FOREIGN KEY (company_activity_id) REFERENCES company_taxonomy_activities(id)
                );

--- Table: tcfd_climate_risks ---
CREATE TABLE tcfd_climate_risks (
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

--- Table: tcfd_disclosures ---
CREATE TABLE tcfd_disclosures (
            id INTEGER PRIMARY KEY,
            code TEXT,
            section TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: tcfd_governance ---
CREATE TABLE tcfd_governance (
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

--- Table: tcfd_metrics ---
CREATE TABLE tcfd_metrics (
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

--- Table: tcfd_reports ---
CREATE TABLE tcfd_reports (
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

--- Table: tcfd_risk_management ---
CREATE TABLE tcfd_risk_management (
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

--- Table: tcfd_risk_templates ---
CREATE TABLE tcfd_risk_templates (
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

--- Table: tcfd_risks ---
CREATE TABLE tcfd_risks (
            id INTEGER PRIMARY KEY,
            risk_name TEXT,
            category TEXT,
            severity TEXT,
            year INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: tcfd_scenario_templates ---
CREATE TABLE tcfd_scenario_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_name TEXT NOT NULL,
    scenario_source TEXT,
    temperature_target REAL,
    time_horizon INTEGER,
    description TEXT,
    assumptions TEXT,
    is_default INTEGER DEFAULT 0
);

--- Table: tcfd_scenarios ---
CREATE TABLE tcfd_scenarios (
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

--- Table: tcfd_strategy ---
CREATE TABLE tcfd_strategy (
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

--- Table: tcfd_target_progress ---
CREATE TABLE tcfd_target_progress (
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

--- Table: tcfd_targets ---
CREATE TABLE tcfd_targets (
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

--- Table: template_execution_history ---
CREATE TABLE template_execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    execution_date TEXT NOT NULL,
                    task_id INTEGER, -- Oluşturulan görev ID'si
                    status TEXT DEFAULT 'success', -- 'success', 'failed', 'skipped'
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (template_id) REFERENCES recurring_task_templates(id)
                );

--- Table: threat_detection ---
CREATE TABLE threat_detection (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    threat_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    description TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    detection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

--- Table: training_programs ---
CREATE TABLE training_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    program_name TEXT NOT NULL,
                    category TEXT,
                    participants INTEGER DEFAULT 0,
                    hours_per_person REAL DEFAULT 0,
                    total_hours REAL,
                    cost REAL,
                    gender TEXT,
                    position_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                , supplier TEXT, invoice_date TEXT, payment_due_date TEXT, currency TEXT DEFAULT 'TRY', total_cost REAL, status TEXT DEFAULT 'active');

--- Table: training_records ---
CREATE TABLE training_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_name TEXT,
                hours REAL,
                participants INTEGER,
                date DATE,
                category TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

--- Table: transition_risks ---
CREATE TABLE transition_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_id INTEGER NOT NULL,
                    risk_category TEXT NOT NULL,
                    risk_description TEXT NOT NULL,
                    likelihood TEXT DEFAULT 'orta',
                    impact TEXT DEFAULT 'orta',
                    financial_impact_min REAL DEFAULT 0,
                    financial_impact_max REAL DEFAULT 0,
                    timeframe TEXT,
                    mitigation_strategy TEXT,
                    FOREIGN KEY (scenario_id) REFERENCES scenario_analyses(id)
                );

--- Table: trend_data ---
CREATE TABLE trend_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    actual_value REAL NOT NULL,
                    predicted_value REAL,
                    prediction_accuracy REAL,
                    data_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, metric_code, year)
                );

--- Table: tsrs_disclosures ---
CREATE TABLE tsrs_disclosures (
            id INTEGER PRIMARY KEY,
            code TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: tsrs_indicators ---
CREATE TABLE tsrs_indicators (
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

--- Table: tsrs_kpis ---
CREATE TABLE tsrs_kpis (
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

--- Table: tsrs_materiality_assessment ---
CREATE TABLE tsrs_materiality_assessment (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            indicator_id INTEGER NOT NULL,
            assessment_period TEXT NOT NULL,
            impact_score INTEGER,
            financial_score INTEGER,
            is_material BOOLEAN,
            material_type TEXT,
            stakeholder_input TEXT,
            assessment_rationale TEXT,
            approved_by TEXT,
            approved_at TEXT,
            UNIQUE(company_id, indicator_id, assessment_period)
        );

--- Table: tsrs_metrics ---
CREATE TABLE tsrs_metrics (
                id INTEGER PRIMARY KEY,
                section_id INTEGER,
                metric_code TEXT,
                metric_title TEXT,
                metric_description TEXT,
                unit TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES tsrs_sections(id)
            );

--- Table: tsrs_performance_data ---
CREATE TABLE tsrs_performance_data (
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

--- Table: tsrs_report_templates ---
CREATE TABLE tsrs_report_templates (
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

--- Table: tsrs_reports ---
CREATE TABLE tsrs_reports (
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

--- Table: tsrs_responses ---
CREATE TABLE tsrs_responses (
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, response TEXT,
    FOREIGN KEY (indicator_id) REFERENCES tsrs_indicators(id) ON DELETE CASCADE,
    UNIQUE(company_id, indicator_id, reporting_period)
);

--- Table: tsrs_risks ---
CREATE TABLE tsrs_risks (
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

--- Table: tsrs_sections ---
CREATE TABLE tsrs_sections (
                id INTEGER PRIMARY KEY,
                section_code TEXT UNIQUE,
                section_title TEXT,
                section_description TEXT,
                category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

--- Table: tsrs_stakeholder_engagement ---
CREATE TABLE tsrs_stakeholder_engagement (
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

--- Table: tsrs_stakeholder_groups ---
CREATE TABLE tsrs_stakeholder_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,                 -- Paydaş grubu adı
    description TEXT,                           -- Açıklama
    engagement_method TEXT,                     -- Katılım yöntemi
    frequency VARCHAR(50),                      -- Katılım sıklığı
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--- Table: tsrs_standards ---
CREATE TABLE tsrs_standards (
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

--- Table: tsrs_targets ---
CREATE TABLE tsrs_targets (
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

--- Table: ungc_compliance ---
CREATE TABLE ungc_compliance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                principle_id VARCHAR(10) NOT NULL,
                compliance_level VARCHAR(20) DEFAULT 'None',
                evidence_count INTEGER DEFAULT 0,
                score REAL DEFAULT 0.0,
                last_assessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: ungc_cop_data ---
CREATE TABLE ungc_cop_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            cop_level TEXT DEFAULT 'learner',
            human_rights_score INTEGER DEFAULT 0,
            labour_score INTEGER DEFAULT 0,
            environment_score INTEGER DEFAULT 0,
            anti_corruption_score INTEGER DEFAULT 0,
            submission_date TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        );

--- Table: ungc_evidence ---
CREATE TABLE ungc_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                principle_id VARCHAR(10) NOT NULL,
                evidence_type VARCHAR(50) NOT NULL,
                evidence_description TEXT,
                evidence_source VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: ungc_kpi_data ---
CREATE TABLE ungc_kpi_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_id VARCHAR(20) NOT NULL,
                    value REAL NOT NULL,
                    period VARCHAR(10) NOT NULL,
                    evidence_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(company_id, kpi_id, period)
                );

--- Table: ungc_principles ---
CREATE TABLE ungc_principles (
            id INTEGER PRIMARY KEY,
            principle_code TEXT,
            name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

--- Table: ungc_reminders ---
CREATE TABLE ungc_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                reminder_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: user_departments ---
CREATE TABLE user_departments (
          user_id INTEGER NOT NULL,
          department_id INTEGER NOT NULL,
          role TEXT,
          PRIMARY KEY(user_id, department_id),
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
          FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE
        );

--- Table: user_group_memberships ---
CREATE TABLE user_group_memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    joined_by INTEGER,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (joined_by) REFERENCES users(id),
    UNIQUE(user_id, group_id)
);

--- Table: user_groups ---
CREATE TABLE user_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

--- Table: user_module_progress ---
CREATE TABLE user_module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company_id INTEGER,
                module_code TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_title TEXT,
                status TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                UNIQUE(company_id, user_id, module_code, step_id)
            );

--- Table: user_permissions ---
CREATE TABLE user_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(user_id, permission_id)
);

--- Table: user_profiles ---
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    language VARCHAR(10) DEFAULT 'tr',
    timezone VARCHAR(50) DEFAULT 'Europe/Istanbul',
    date_format VARCHAR(20) DEFAULT 'DD.MM.YYYY',
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled BOOLEAN DEFAULT 1,
    email_notifications BOOLEAN DEFAULT 1,
    dashboard_layout TEXT,
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

--- Table: user_roles ---
CREATE TABLE "user_roles" (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, role_id INTEGER NOT NULL, assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, assigned_by INTEGER, expires_at TIMESTAMP, is_active BOOLEAN DEFAULT 1, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE, FOREIGN KEY (assigned_by) REFERENCES users(id), UNIQUE(user_id, role_id));

--- Table: user_sdg_selections ---
CREATE TABLE user_sdg_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES sdg_goals(id) ON DELETE CASCADE,
                UNIQUE(company_id, goal_id)
            );

--- Table: user_sessions ---
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

--- Table: user_settings ---
CREATE TABLE user_settings (
                    user_id INTEGER PRIMARY KEY,
                    onboarding_completed INTEGER DEFAULT 0,
                    theme TEXT DEFAULT 'default',
                    language TEXT DEFAULT 'tr',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                , show_welcome_banner INTEGER DEFAULT 1, show_onboarding INTEGER DEFAULT 1);

--- Table: user_surveys ---
CREATE TABLE user_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    template_id INTEGER NOT NULL,
                    assigned_by INTEGER,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'assigned',
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (template_id) REFERENCES survey_templates(id)
                );

--- Table: users ---
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  display_name TEXT,
  email TEXT UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT DEFAULT 'user',            -- hızlı erişim
  is_active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
, first_name VARCHAR(50) DEFAULT '', last_name VARCHAR(50) DEFAULT '', phone VARCHAR(20), department VARCHAR(100), position VARCHAR(100), avatar_path VARCHAR(255), is_verified BOOLEAN DEFAULT 0, last_login TIMESTAMP, login_attempts INTEGER DEFAULT 0, locked_until TIMESTAMP, created_by INTEGER, updated_by INTEGER, totp_secret TEXT, totp_enabled INTEGER DEFAULT 0, backup_codes TEXT, must_change_password INTEGER DEFAULT 0, deleted_at INTEGER, updated_at TEXT, is_superadmin INTEGER DEFAULT 0, tour_completed INTEGER DEFAULT 0, role_name TEXT DEFAULT 'User', pw_hash_version VARCHAR(20) DEFAULT "sha256", first_login INTEGER DEFAULT 1, failed_attempts INTEGER DEFAULT 0);

--- Table: validation_results ---
CREATE TABLE validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                field_name TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                error_message TEXT,
                validated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );

--- Table: validation_rules ---
CREATE TABLE validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                field_name TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_config TEXT,
                error_message TEXT,
                severity TEXT DEFAULT 'error',
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            );

--- Table: verification_records ---
CREATE TABLE verification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    data_item TEXT NOT NULL,
                    data_value TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    auditor_id INTEGER,
                    verification_date TIMESTAMP,
                    verification_notes TEXT,
                    confidence_level TEXT,
                    evidence_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (auditor_id) REFERENCES auditors(id)
                );

--- Table: vulnerability_details ---
CREATE TABLE vulnerability_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    vulnerability_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    affected_component TEXT,
                    remediation_steps TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES penetration_tests(id)
                );

--- Table: waste_categories ---
CREATE TABLE waste_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    waste_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    hazardous TEXT,
                    recycling_potential TEXT,
                    disposal_method TEXT,
                    environmental_impact TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: waste_generation ---
CREATE TABLE waste_generation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    waste_type TEXT NOT NULL,
                    waste_category TEXT NOT NULL,
                    waste_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    disposal_method TEXT,
                    disposal_cost REAL,
                    location TEXT,
                    hazardous_status TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_metrics ---
CREATE TABLE waste_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    total_waste_generated REAL DEFAULT 0.0,
                    total_waste_disposed REAL DEFAULT 0.0,
                    total_waste_recycled REAL DEFAULT 0.0,
                    recycling_rate REAL DEFAULT 0.0,
                    waste_reduction_rate REAL DEFAULT 0.0,
                    circular_economy_index REAL DEFAULT 0.0,
                    waste_cost REAL DEFAULT 0.0,
                    waste_revenue REAL DEFAULT 0.0,
                    carbon_footprint REAL DEFAULT 0.0,
                    hazardous_waste_ratio REAL DEFAULT 0.0,
                    organic_waste_ratio REAL DEFAULT 0.0,
                    recyclable_waste_ratio REAL DEFAULT 0.0,
                    data_quality_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_records ---
CREATE TABLE waste_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    waste_type_id INTEGER NOT NULL,
                    waste_code TEXT NOT NULL,
                    waste_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    source_location TEXT,
                    generation_source TEXT,
                    disposal_method TEXT,
                    recycling_rate REAL DEFAULT 0.0,
                    disposal_cost REAL DEFAULT 0.0,
                    carbon_footprint REAL DEFAULT 0.0,
                    data_quality TEXT DEFAULT 'Estimated',
                    evidence_file TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, invoice_date TEXT, due_date TEXT, supplier TEXT,
                    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_recycling ---
CREATE TABLE waste_recycling (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    waste_type TEXT NOT NULL,
                    recycled_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    recycling_method TEXT,
                    recycling_rate REAL,
                    revenue REAL,
                    location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_reduction_projects ---
CREATE TABLE waste_reduction_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    waste_reduction REAL,
                    reduction_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_reduction_targets ---
CREATE TABLE waste_reduction_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_name TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    waste_category TEXT,
                    waste_type_id INTEGER,
                    base_year INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    base_quantity REAL NOT NULL,
                    target_quantity REAL NOT NULL,
                    reduction_percentage REAL,
                    target_unit TEXT NOT NULL,
                    status TEXT DEFAULT 'Active',
                    progress REAL DEFAULT 0.0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_reports ---
CREATE TABLE waste_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    report_data TEXT,
                    file_path TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_targets ---
CREATE TABLE waste_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_generation REAL,
                    target_reduction_percent REAL,
                    target_generation REAL,
                    recycling_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: waste_types ---
CREATE TABLE waste_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    waste_code TEXT UNIQUE NOT NULL,
                    waste_name TEXT NOT NULL,
                    waste_category TEXT NOT NULL,
                    hazard_level TEXT DEFAULT 'Non-hazardous',
                    recycling_potential TEXT DEFAULT 'Medium',
                    disposal_method TEXT,
                    environmental_impact TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: water_consumption ---
CREATE TABLE water_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    consumption_type TEXT NOT NULL,
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    cost REAL,
                    source TEXT,
                    location TEXT,
                    quality_parameters TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: water_efficiency_projects ---
CREATE TABLE water_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    water_savings REAL,
                    savings_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: water_kpis ---
CREATE TABLE water_kpis (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    total_withdrawal_m3 REAL NOT NULL,
                    total_discharge_m3 REAL NOT NULL,
                    total_consumption_m3 REAL NOT NULL,
                    recycle_rate_percent REAL,
                    intensity_m3_per_output REAL,      -- output_value'a göre yoğunluk
                    output_value REAL,
                    output_unit TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, period)
                );

--- Table: water_quality ---
CREATE TABLE water_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    location TEXT NOT NULL,
                    parameter_name TEXT NOT NULL,
                    parameter_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    standard_limit REAL,
                    compliance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: water_quality_monitoring ---
CREATE TABLE water_quality_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    monitoring_date DATE NOT NULL,
                    water_source TEXT NOT NULL,              -- intake, discharge, process
                    location TEXT NOT NULL,                  -- Ölçüm noktası
                    parameter_name TEXT NOT NULL,            -- pH, TDS, BOD, COD, etc.
                    parameter_value REAL NOT NULL,
                    parameter_unit TEXT NOT NULL,            -- mg/L, pH, NTU, etc.
                    measurement_method TEXT,                 -- Ölçüm metodu
                    standard_limit REAL,                     -- Standart limit değer
                    compliance_status TEXT,                  -- compliant, non_compliant, warning
                    responsible_lab TEXT,                    -- Sorumlu laboratuvar
                    certification TEXT,                      -- Laboratuvar sertifikası
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: water_recycling ---
CREATE TABLE water_recycling (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    recycling_type TEXT NOT NULL,
                    recycled_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    treatment_method TEXT,
                    reuse_purpose TEXT,
                    cost_savings REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: water_reports ---
CREATE TABLE water_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT,                        -- annual, quarterly, water_footprint
                    total_blue_water REAL,
                    total_green_water REAL,
                    total_grey_water REAL,
                    total_water_footprint REAL NOT NULL,     -- Toplam su ayak izi (m³)
                    water_intensity REAL,                    -- Su yoğunluğu (m³/ürün birimi)
                    recycling_rate REAL,                     -- Geri dönüşüm oranı
                    efficiency_ratio REAL,                   -- Verimlilik oranı
                    water_stress_level TEXT,                 -- low, medium, high, critical
                    sdg_6_progress REAL,                     -- SDG 6 ilerleme skoru (0-100)
                    boundary_description TEXT,               -- Sistem sınırları
                    methodology TEXT,                        -- Hesaplama metodolojisi
                    verification_status TEXT,                -- unverified, third_party, internal
                    verifier_name TEXT,
                    verification_date DATE,
                    report_file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: water_sources ---
CREATE TABLE water_sources (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    source_type TEXT NOT NULL,         -- municipal, groundwater, surface, recycled
                    description TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: water_targets ---
CREATE TABLE water_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_consumption REAL,
                    target_reduction_percent REAL,
                    target_consumption REAL,
                    recycling_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: water_usages ---
CREATE TABLE water_usages (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,              -- 2024, 2024Q1, 2024-06
                    category TEXT,                     -- production, cooling, sanitary, irrigation
                    withdrawal_m3 REAL DEFAULT 0,
                    discharge_m3 REAL DEFAULT 0,
                    recycled_m3 REAL DEFAULT 0,
                    output_value REAL,                 -- üretim miktarı / gelir / benzeri
                    output_unit TEXT,                  -- t, kg, $, vb.
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                );

--- Table: web_survey_responses ---
CREATE TABLE web_survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                web_survey_id INTEGER NOT NULL,
                respondent_email TEXT,
                respondent_name TEXT,
                response_data TEXT,
                submitted_at TIMESTAMP,
                processed BOOLEAN DEFAULT 0,
                processed_at TIMESTAMP,
                FOREIGN KEY (web_survey_id) REFERENCES web_surveys (id)
            );

--- Table: web_surveys ---
CREATE TABLE web_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                module_name TEXT NOT NULL,
                sub_module TEXT,
                survey_name TEXT NOT NULL,
                survey_token TEXT UNIQUE NOT NULL,
                web_survey_id INTEGER,
                survey_url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deadline_date DATE,
                status TEXT DEFAULT 'active',
                response_count INTEGER DEFAULT 0,
                last_sync TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            );

--- Table: whatif_scenarios ---
CREATE TABLE whatif_scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scenario_name TEXT NOT NULL,
                    scenario_description TEXT,
                    metric_code TEXT NOT NULL,
                    baseline_value REAL NOT NULL,
                    change_percentage REAL NOT NULL,
                    projected_value REAL NOT NULL,
                    impact_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

--- Table: xbrl_tagging_metadata ---
CREATE TABLE xbrl_tagging_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_point_name TEXT NOT NULL,
                    esrs_reference TEXT,
                    xbrl_tag TEXT,
                    data_type TEXT,
                    unit_of_measure TEXT,
                    value_numeric REAL,
                    value_text TEXT,
                    reporting_period TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: yearly_comparisons ---
CREATE TABLE yearly_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    data_field TEXT NOT NULL,
                    current_year INTEGER NOT NULL,
                    current_value REAL,
                    previous_year INTEGER,
                    previous_value REAL,
                    change_amount REAL,
                    change_percentage REAL,
                    anomaly_detected BOOLEAN DEFAULT 0,
                    anomaly_reason TEXT,
                    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

