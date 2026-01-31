
import sqlite3
import os
import sys
import hashlib

# Remote path
DB_PATH = "/var/www/sustainage/sustainage.db"

def get_compat_hash(password):
    salt = 'sustainage_salt'
    hash_hex = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}:{hash_hex}"

def init_tables():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # --- Core Tables ---
        print("Creating Core tables...")
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if default company exists
        cursor.execute("SELECT count(*) FROM companies")
        if cursor.fetchone()[0] == 0:
            print("Inserting default company...")
            cursor.execute("INSERT INTO companies (name, industry) VALUES ('Demo Company', 'Technology')")
            conn.commit()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                email TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if default user exists
        cursor.execute("SELECT count(*) FROM users WHERE username='admin'")
        if cursor.fetchone()[0] == 0:
            print("Inserting default admin user...")
            pw_hash = get_compat_hash('admin123')
            cursor.execute("INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)", 
                          ('admin', pw_hash, 'admin', 'admin@example.com'))
            conn.commit()
        else:
            print("Updating admin password...")
            pw_hash = get_compat_hash('admin123')
            cursor.execute("UPDATE users SET password_hash=? WHERE username='admin'", (pw_hash,))
            conn.commit()
            
        # User Companies (link user to company)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                assigned_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                UNIQUE(user_id, company_id)
            )
        """)

        # Rate Limits Table (Critical for Login)
        print("Creating Rate Limits table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_type TEXT NOT NULL,
                identifier TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0,
                UNIQUE(resource_type, identifier)
            )
        """)
        
        # Link admin to Demo Company
        cursor.execute("SELECT id FROM users WHERE username='admin'")
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM companies WHERE name='Demo Company'")
        company_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM user_companies WHERE user_id=? AND company_id=?", (user_id, company_id))
        if cursor.fetchone()[0] == 0:
            print("Linking admin to Demo Company...")
            cursor.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (?, ?, 1)", (user_id, company_id))
            conn.commit()

        # --- CBAM Tables ---
        print("Creating CBAM tables...")
        
        # CBAM ürünleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbam_products (
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
            )
        """)

        # CBAM emisyon verileri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbam_emissions (
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
            )
        """)

        # CBAM ithalat verileri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbam_imports (
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
            )
        """)

        # CBAM raporları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cbam_reports (
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
            )
        """)

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cbam_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period INTEGER NOT NULL,
                eu_ets_price_eur_per_tco2 REAL NOT NULL,
                default_leakage_factor REAL DEFAULT 0.6,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(period)
            )
            """
        )

        # --- CSRD Tables ---
        print("Creating CSRD tables...")

        # ESRS açıklama takibi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS esrs_disclosures (
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
            )
        """)

        # Çift önemlendirme değerlendirmesi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS double_materiality_assessment (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # AB Taxonomy uygunluk
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eu_taxonomy_alignment (
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS eu_taxonomy_objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alignment_id INTEGER NOT NULL,
                objective_code TEXT NOT NULL,
                is_primary BOOLEAN DEFAULT 0,
                FOREIGN KEY (alignment_id) REFERENCES eu_taxonomy_alignment(id)
            )
        """)

        # CSRD uyum kontrol listesi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS csrd_compliance_checklist (
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
            )
        """)

        conn.commit()
        print("All tables created successfully.")

    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_tables()
