import sqlite3
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def add_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    indexes_to_create = [
        # TSRS Indexes
        ("tsrs_responses", "indicator_id", "idx_tsrs_responses_indicator_id"),
        ("tsrs_targets", "indicator_id", "idx_tsrs_targets_indicator_id"),
        ("tsrs_risks", "standard_id", "idx_tsrs_risks_standard_id"),
        ("map_tsrs_esrs", "tsrs_indicator_id", "idx_map_tsrs_esrs_tsrs_indicator_id"),
        ("tsrs_stakeholder_engagement", "stakeholder_group_id", "idx_tsrs_stakeholder_engagement_stakeholder_group_id"),
        ("tsrs_reports", "template_id", "idx_tsrs_reports_template_id"),
        ("tsrs_kpis", "indicator_id", "idx_tsrs_kpis_indicator_id"),
        ("tsrs_performance_data", "kpi_id", "idx_tsrs_performance_data_kpi_id"),
        
        # Performance Indexes for Multi-tenancy
        ("companies", "id", "idx_companies_id"),
        ("users", "company_id", "idx_users_company_id"),
        ("users", "username", "idx_users_username"),
        ("licenses", "company_id", "idx_licenses_company_id"),
        ("licenses", "license_key", "idx_licenses_key"),
        
        # Module Indexes (Common Filters)
        ("energy_consumption", "company_id", "idx_energy_company_id"),
        ("water_consumption", "company_id", "idx_water_company_id"),
        ("waste_generation", "company_id", "idx_waste_company_id"),
        ("carbon_emission_factors", "source_type", "idx_carbon_factors_source"),
        ("audit_logs", "company_id", "idx_audit_company_id"),
        ("audit_logs", "timestamp", "idx_audit_timestamp")
    ]

    print(f"Adding {len(indexes_to_create)} missing indexes...")

    added_count = 0
    for table, col, idx_name in indexes_to_create:
        try:
            # Check if index exists first (to avoid error)
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{idx_name}'")
            if cursor.fetchone():
                print(f"  - Index {idx_name} already exists. Skipping.")
                continue

            sql = f"CREATE INDEX {idx_name} ON {table}({col})"
            cursor.execute(sql)
            print(f"  ✅ Created index: {idx_name}")
            added_count += 1
        except Exception as e:
            print(f"  ❌ Error creating {idx_name}: {e}")

    conn.commit()
    conn.close()
    print(f"\nDone. Added {added_count} indexes.")

if __name__ == "__main__":
    add_indexes()
