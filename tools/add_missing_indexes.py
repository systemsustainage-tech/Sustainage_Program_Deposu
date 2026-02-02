import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'sustainage.db')

def add_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    indexes_to_create = [
        ("tsrs_responses", "indicator_id", "idx_tsrs_responses_indicator_id"),
        ("tsrs_targets", "indicator_id", "idx_tsrs_targets_indicator_id"),
        ("tsrs_risks", "standard_id", "idx_tsrs_risks_standard_id"),
        ("map_tsrs_esrs", "tsrs_indicator_id", "idx_map_tsrs_esrs_tsrs_indicator_id"),
        ("tsrs_stakeholder_engagement", "stakeholder_group_id", "idx_tsrs_stakeholder_engagement_stakeholder_group_id"),
        ("tsrs_reports", "template_id", "idx_tsrs_reports_template_id"),
        ("tsrs_kpis", "indicator_id", "idx_tsrs_kpis_indicator_id"),
        ("tsrs_performance_data", "kpi_id", "idx_tsrs_performance_data_kpi_id")
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
