
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
