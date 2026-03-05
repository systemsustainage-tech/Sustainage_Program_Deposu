import sqlite3
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def add_reporting_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    indexes_to_create = [
        # Report Templates
        ("report_templates", "company_id", "idx_report_templates_company"),
        ("report_templates", "status", "idx_report_templates_status"),
        
        # Generated Reports
        ("generated_reports", "company_id", "idx_generated_reports_company"),
        ("generated_reports", "template_id", "idx_generated_reports_template"),
        ("generated_reports", "status", "idx_generated_reports_status"),
        ("generated_reports", "created_at", "idx_generated_reports_created"),
        
        # Audit Logs (Critical for security/history)
        ("audit_logs", "company_id", "idx_audit_logs_company"),
        ("audit_logs", "user_id", "idx_audit_logs_user"),
        ("audit_logs", "created_at", "idx_audit_logs_created"),
        ("audit_logs", "action", "idx_audit_logs_action"),
        
        # Notifications
        ("notifications", "user_id", "idx_notifications_user"),
        ("notifications", "is_read", "idx_notifications_read"),
        ("notifications", "created_at", "idx_notifications_created"),
        
        # Tasks (Workflow)
        ("tasks", "company_id", "idx_tasks_company"),
        ("tasks", "assigned_to", "idx_tasks_assigned"),
        ("tasks", "status", "idx_tasks_status"),
        ("tasks", "due_date", "idx_tasks_due_date")
    ]

    print(f"Adding {len(indexes_to_create)} reporting/audit indexes...")

    added_count = 0
    for table, col, idx_name in indexes_to_create:
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"  ⚠️ Table {table} does not exist. Skipping index {idx_name}.")
                continue

            # Check if index exists
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
    add_reporting_indexes()
