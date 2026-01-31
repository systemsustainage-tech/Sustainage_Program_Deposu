import sqlite3
import os
import sys
import logging

# Define database path
DB_PATH = '/var/www/sustainage/sustainage.db'

def fix_stakeholder_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Creating stakeholder tables...")

        # 1. stakeholders
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholders (
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # 2. stakeholder_engagements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_engagements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                stakeholder_id INTEGER NOT NULL,
                engagement_date TEXT NOT NULL,
                engagement_type TEXT NOT NULL,
                engagement_topic TEXT NOT NULL,
                participants TEXT,
                outcomes TEXT,
                satisfaction_score REAL,
                follow_up_required BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
            )
        """)

        # 3. stakeholder_surveys
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                survey_name TEXT NOT NULL,
                survey_period TEXT NOT NULL,
                survey_type TEXT NOT NULL,
                stakeholder_group TEXT NOT NULL,
                response_count INTEGER,
                total_invitations INTEGER,
                response_rate REAL,
                overall_satisfaction REAL,
                key_findings TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # 4. stakeholder_complaints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_complaints (
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
            )
        """)

        # 5. stakeholder_survey_templates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_survey_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                template_name TEXT NOT NULL,
                stakeholder_category TEXT,
                questions_json TEXT NOT NULL,          -- JSON soru listesi
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # 6. stakeholder_action_plans
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_action_plans (
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
            )
        """)

        # 7. stakeholder_communication_plans
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_communication_plans (
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
            )
        """)

        conn.commit()
        print("Tables created successfully.")

        # Insert Sample Data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM stakeholders")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample data...")
            
            # Sample Stakeholders
            stakeholders_data = [
                (1, 'Ahmet Yılmaz', 'Employees', 'Ahmet Yılmaz', 'ahmet@sirket.com', '5551234567', 'Şirket İçi', 'Internal', 'High', 'High', 'Weekly'),
                (1, 'XYZ Tedarik A.Ş.', 'Suppliers', 'Mehmet Demir', 'mehmet@xyz.com', '5559876543', 'XYZ Tedarik', 'Logistics', 'Medium', 'High', 'Monthly'),
                (1, 'Yerel Yönetim', 'Government', 'Ayşe Kaya', 'ayse@belediye.gov.tr', '5551112233', 'Belediye', 'Public', 'High', 'Medium', 'Quarterly'),
                (1, 'Yeşil Doğa STK', 'NGO', 'Can Yıldız', 'can@yesildoga.org', '5554445566', 'Yeşil Doğa', 'Environment', 'Low', 'High', 'Ad-hoc')
            ]
            
            cursor.executemany("""
                INSERT INTO stakeholders 
                (company_id, stakeholder_name, stakeholder_type, contact_person, contact_email, contact_phone, organization, sector, influence_level, interest_level, engagement_frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, stakeholders_data)
            
            # Get inserted IDs
            cursor.execute("SELECT id FROM stakeholders WHERE company_id = 1")
            stakeholder_ids = [row[0] for row in cursor.fetchall()]
            
            # Sample Engagements
            if len(stakeholder_ids) >= 2:
                engagements_data = [
                    (1, stakeholder_ids[0], '2023-10-15', 'Meeting', 'Annual Review', 'All staff', 'Positive feedback', 4.5, 0),
                    (1, stakeholder_ids[1], '2023-11-20', 'Email', 'Supply Chain Audit', 'Procurement', 'Audit scheduled', 4.0, 1),
                    (1, stakeholder_ids[2], '2023-12-05', 'Workshop', 'Sustainability Goals', 'CSR Team', 'Goals aligned', 4.8, 0)
                ]
                cursor.executemany("""
                    INSERT INTO stakeholder_engagements
                    (company_id, stakeholder_id, engagement_date, engagement_type, engagement_topic, participants, outcomes, satisfaction_score, follow_up_required)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, engagements_data)

            # Sample Surveys
            surveys_data = [
                (1, 'Çalışan Memnuniyeti 2023', '2023-Q4', 'Satisfaction', 'Employees', 150, 200, 75.0, 4.2, 'Genel memnuniyet yüksek, yemekhane şikayetleri var.'),
                (1, 'Tedarikçi Sürdürülebilirlik Anketi', '2023-H2', 'Sustainability', 'Suppliers', 45, 60, 75.0, 3.8, 'Karbon ayak izi verileri eksik.')
            ]
            cursor.executemany("""
                INSERT INTO stakeholder_surveys
                (company_id, survey_name, survey_period, survey_type, stakeholder_group, response_count, total_invitations, response_rate, overall_satisfaction, key_findings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, surveys_data)
            
            # Sample Complaints
            if len(stakeholder_ids) >= 1:
                complaints_data = [
                    (1, stakeholder_ids[0], '2023-12-10', 'Email', 'Ofis sıcaklığı çok düşük', 'Low', 'open', None, None)
                ]
                cursor.executemany("""
                    INSERT INTO stakeholder_complaints
                    (company_id, stakeholder_id, complaint_date, channel, description, severity, status, resolution, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, complaints_data)

            conn.commit()
            print("Sample data inserted successfully.")
        else:
            print("Tables already contain data, skipping sample data insertion.")

        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    fix_stakeholder_schema()
