--- Table: audit_logs ---
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

--- Table: biodiversity_impact_assessment ---
CREATE TABLE biodiversity_impact_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    impact_type TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    affected_species TEXT,
                    mitigation_measures TEXT,
                    monitoring_plan TEXT,
                    compliance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: biodiversity_projects ---
CREATE TABLE biodiversity_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    project_area REAL,
                    area_unit TEXT,
                    target_species TEXT,
                    expected_benefits TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: biodiversity_sites ---
CREATE TABLE biodiversity_sites (company_id INTEGER, site_name TEXT, proximity_to_protected_area BOOLEAN);

--- Table: biodiversity_species ---
CREATE TABLE biodiversity_species (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    species_name TEXT NOT NULL,
                    species_type TEXT NOT NULL,
                    conservation_status TEXT,
                    habitat_requirements TEXT,
                    population_count INTEGER,
                    last_survey_date TEXT,
                    threat_factors TEXT,
                    protection_measures TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: biodiversity_targets ---
CREATE TABLE biodiversity_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    baseline_unit TEXT,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: board_members ---
CREATE TABLE board_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    member_name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    member_type TEXT NOT NULL,
                    appointment_date TEXT,
                    term_end_date TEXT,
                    independence_status TEXT,
                    expertise_area TEXT,
                    gender TEXT,
                    age INTEGER,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: carbon_targets ---
CREATE TABLE carbon_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_emissions REAL,
                    target_reduction_percent REAL,
                    target_emissions REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
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

--- Table: companies ---
CREATE TABLE companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sector TEXT,
            employee_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

--- Table: csrd_materiality ---
CREATE TABLE csrd_materiality (company_id INTEGER, topic TEXT, impact_score REAL, financial_score REAL);

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

--- Table: departments ---
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    parent_department_id INTEGER,
    manager_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    FOREIGN KEY (parent_department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

--- Table: double_materiality_assessment ---
CREATE TABLE double_materiality_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    topic_code TEXT NOT NULL,
                    topic_name TEXT NOT NULL,
                    esrs_reference TEXT,
                    impact_materiality_score INTEGER DEFAULT 0,
                    impact_rationale TEXT,
                    financial_materiality_score INTEGER DEFAULT 0,
                    financial_rationale TEXT,
                    overall_material BOOLEAN DEFAULT 0,
                    stakeholder_input TEXT,
                    assessment_date DATE,
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

--- Table: ecosystem_services ---
CREATE TABLE ecosystem_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    service_type TEXT NOT NULL,
                    service_value REAL,
                    value_unit TEXT,
                    measurement_method TEXT,
                    beneficiary TEXT,
                    location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
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

--- Table: emission_factors ---
CREATE TABLE emission_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    fuel_type TEXT,
                    factor_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    scope INTEGER,
                    country TEXT,
                    source_reference TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

--- Table: esrs_compliance ---
CREATE TABLE esrs_compliance (company_id INTEGER, standard_id TEXT, status TEXT);

--- Table: esrs_datapoints ---
CREATE TABLE esrs_datapoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                standard_id INTEGER,
                datapoint TEXT,
                value TEXT,
                unit TEXT,
                year INTEGER,
                FOREIGN KEY (standard_id) REFERENCES esrs_standards(id)
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

--- Table: esrs_standards ---
CREATE TABLE esrs_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                title TEXT,
                category TEXT,
                description TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

--- Table: governance_committees ---
CREATE TABLE governance_committees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    committee_name TEXT NOT NULL,
                    committee_type TEXT NOT NULL,
                    chair_person TEXT,
                    member_count INTEGER,
                    meeting_frequency TEXT,
                    responsibilities TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: governance_policies ---
CREATE TABLE governance_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    policy_name TEXT NOT NULL,
                    policy_type TEXT NOT NULL,
                    version TEXT,
                    effective_date TEXT,
                    review_date TEXT,
                    approval_authority TEXT,
                    compliance_requirements TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: governance_structure ---
CREATE TABLE governance_structure (company_id INTEGER, member_name TEXT, role TEXT, independent BOOLEAN);

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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
                );

--- Table: gri_performance ---
CREATE TABLE gri_performance (company_id INTEGER, indicator_code TEXT, value TEXT, year INTEGER);

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

--- Table: gri_standards ---
CREATE TABLE gri_standards (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: habitat_areas ---
CREATE TABLE habitat_areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    habitat_name TEXT NOT NULL,
                    habitat_type TEXT NOT NULL,
                    area_size REAL NOT NULL,
                    area_unit TEXT NOT NULL,
                    location TEXT,
                    coordinates TEXT,
                    biodiversity_value TEXT,
                    protection_status TEXT,
                    management_plan TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
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
CREATE TABLE iirc_capitals (company_id INTEGER, year INTEGER, capital_type TEXT, value TEXT);

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

--- Table: map_gri_tsrs ---
CREATE TABLE map_gri_tsrs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gri_standard TEXT NOT NULL,
                    gri_disclosure TEXT,
                    tsrs_section TEXT,
                    tsrs_metric TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: map_sdg_gri ---
CREATE TABLE map_sdg_gri (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_indicator_code TEXT NOT NULL,
                    gri_standard TEXT NOT NULL,
                    gri_disclosure TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: map_sdg_tsrs ---
CREATE TABLE map_sdg_tsrs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_indicator_code TEXT NOT NULL,
                    tsrs_section TEXT,
                    tsrs_metric TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: ohs_incidents ---
CREATE TABLE ohs_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT,
                date DATE,
                severity TEXT,
                description TEXT,
                lost_time_days INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

--- Table: permissions ---
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    module VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(100),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
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

--- Table: responses ---
CREATE TABLE responses (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                indicator_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                answer_json TEXT,
                value_num REAL,
                progress_pct INTEGER DEFAULT 0,
                request_status TEXT DEFAULT 'Gönderilmedi',
                policy_flag TEXT DEFAULT 'Hayır',
                evidence_url TEXT,
                approved_by_owner TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE,
                UNIQUE(company_id, indicator_id, period)
            );

--- Table: role_permissions ---
CREATE TABLE role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(role_id, permission_id)
);

--- Table: roles ---
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
);

--- Table: scope1_emissions ---
CREATE TABLE scope1_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    emission_source TEXT NOT NULL,
                    fuel_type TEXT,
                    fuel_consumption REAL,
                    fuel_unit TEXT,
                    emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: scope2_emissions ---
CREATE TABLE scope2_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    energy_source TEXT NOT NULL,
                    energy_consumption REAL,
                    energy_unit TEXT,
                    grid_emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: scope3_emissions ---
CREATE TABLE scope3_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    activity_data REAL,
                    activity_unit TEXT,
                    emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

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

--- Table: sdg_goals ---
CREATE TABLE sdg_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code INTEGER UNIQUE NOT NULL,
                    title_tr TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: sdg_indicators ---
CREATE TABLE sdg_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    title_tr TEXT NOT NULL,
                    data_source TEXT,
                    measurement_frequency TEXT,
                    related_sectors TEXT,
                    related_funds TEXT,
                    kpi_metric TEXT,
                    implementation_requirement TEXT,
                    notes TEXT,
                    request_status TEXT,
                    status TEXT,
                    progress_percentage REAL,
                    completeness_percentage REAL,
                    policy_document_exists TEXT,
                    data_quality TEXT,
                    incentive_readiness_score REAL,
                    readiness_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (target_id) REFERENCES sdg_targets(id)
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

--- Table: sdg_progress ---
CREATE TABLE sdg_progress (company_id INTEGER, goal_id INTEGER, progress REAL, year INTEGER);

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
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_type_id) REFERENCES sdg_question_types(id)
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
                    validation_rules TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

--- Table: sdg_targets ---
CREATE TABLE sdg_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    title_tr TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (goal_id) REFERENCES sdg_goals(id)
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

--- Table: selections ---
CREATE TABLE selections (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                goal_id INTEGER,
                target_id INTEGER,
                indicator_id INTEGER,
                selected INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(goal_id) REFERENCES sdg_goals(id),
                FOREIGN KEY(target_id) REFERENCES sdg_targets(id),
                FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id)
            );

--- Table: sqlite_sequence ---
CREATE TABLE sqlite_sequence(name,seq);

--- Table: suppliers ---
CREATE TABLE suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    supplier_name TEXT NOT NULL,
                    supplier_type TEXT NOT NULL,
                    country TEXT,
                    certification_status TEXT,
                    sustainability_score REAL,
                    risk_level TEXT,
                    last_assessment_date TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                );

--- Table: supply_chain_assessments ---
CREATE TABLE supply_chain_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    assessment_type TEXT NOT NULL,
                    environmental_score REAL,
                    social_score REAL,
                    governance_score REAL,
                    overall_score REAL,
                    improvement_areas TEXT,
                    action_plan TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
                );

--- Table: supply_chain_risks ---
CREATE TABLE supply_chain_risks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    risk_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    impact_assessment TEXT,
                    mitigation_measures TEXT,
                    monitoring_frequency TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
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
    updated_by INTEGER,
    FOREIGN KEY (updated_by) REFERENCES users(id)
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

--- Table: taxonomy_alignment ---
CREATE TABLE taxonomy_alignment (company_id INTEGER, activity_name TEXT, alignment_percentage REAL);

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

--- Table: user_companies ---
CREATE TABLE user_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT 0,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    UNIQUE(user_id, company_id)
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
CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id),
    UNIQUE(user_id, role_id)
);

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

--- Table: users ---
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(100),
    position VARCHAR(100),
    avatar_path VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    last_login TIMESTAMP,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP,
    failed_attempts INTEGER DEFAULT 0,
    totp_secret_encrypted TEXT,
    totp_backup_codes TEXT,
    must_change_password INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (updated_by) REFERENCES users(id)
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

--- Table: licenses ---
CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    license_key TEXT UNIQUE NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    max_users INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (company_id) REFERENCES companies(id)
);


--- Table: password_reset_tokens ---
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

--- Table: temp_access_tokens ---
CREATE TABLE temp_access_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

--- Table: report_templates ---
CREATE TABLE report_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    template_name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    template_content TEXT,
    template_variables TEXT,
    language_code TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--- Table: report_sections ---
CREATE TABLE report_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    section_name TEXT NOT NULL,
    section_content TEXT,
    section_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES report_templates(id)
);

--- Table: report_generation_log ---
CREATE TABLE report_generation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    user_id INTEGER,
    template_id INTEGER,
    report_type TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    file_path TEXT,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (template_id) REFERENCES report_templates(id)
);

--- Table: report_customizations ---
CREATE TABLE report_customizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    template_id INTEGER,
    custom_settings TEXT, -- JSON storage for colors, fonts, logos etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES report_templates(id)
);
