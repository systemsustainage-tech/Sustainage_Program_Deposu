import sqlite3
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.database import DB_PATH
except ImportError:
    # Fallback if config not found
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

if not os.path.exists(os.path.dirname(DB_PATH)):
    print(f"Database directory does not exist: {os.path.dirname(DB_PATH)}")
    sys.exit(1)

COMPANY_INFO_FIELDS = [
    "name", "legal_name", "trading_name", "description", "business_model",
    "key_products_services", "markets_served", "sector", "industry_code",
    "industry_description", "company_size", "employee_count", "isic_code",
    "registration_number", "tax_number", "legal_form", "establishment_date",
    "ownership_type", "parent_company", "subsidiaries", "stock_exchange",
    "ticker_symbol", "fiscal_year_end", "reporting_period", "annual_revenue",
    "currency", "auditor", "sustainability_strategy", "material_topics",
    "stakeholder_groups", "esg_rating_agency", "esg_rating", "certifications",
    "memberships", "headquarters_address", "city", "postal_code", "country",
    "phone", "email", "website", "sustainability_contact",
    # New fields
    "vizyon", "misyon", "degerler", "tesisler_ozet", "kilometre_taslari_ozet",
    "urun_hizmet_ozet", "karbon_profili_ozet", "uyelikler_ozet", "oduller_ozet",
    # Turkish fields mapping
    "sirket_adi", "ticari_unvan", "vergi_no", "vergi_dairesi",
    "telefon", "calisan_sayisi", "aktif", "sektor",
    "il", "ilce", "posta_kodu", "adres"
]

def migrate():
    print(f"Migrating database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER UNIQUE
        )
    """)
    
    # Get existing columns
    cur.execute("PRAGMA table_info(company_info)")
    existing_cols = {row[1] for row in cur.fetchall()}
    print(f"Existing columns: {existing_cols}")
    
    # Add missing columns
    added_count = 0
    for col in COMPANY_INFO_FIELDS + ["updated_at"]:
        if col in existing_cols or col in ("id", "company_id"):
            continue
        try:
            print(f"Adding column: {col}")
            cur.execute(f"ALTER TABLE company_info ADD COLUMN {col} TEXT")
            added_count += 1
        except Exception as e:
            print(f"Error adding column {col}: {e}")
            
    conn.commit()
    conn.close()
    print(f"Migration completed. Added {added_count} columns.")

if __name__ == "__main__":
    migrate()
