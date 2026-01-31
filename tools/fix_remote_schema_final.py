import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def add_column_if_not_exists(cursor, table, column, definition):
    try:
        cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
    except sqlite3.OperationalError:
        print(f"Adding {column} to {table}...")
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print("Success.")
        except Exception as e:
            print(f"Failed: {e}")
    except Exception as e:
        # Table might not exist
        if "no such table" in str(e):
             print(f"Table {table} does not exist. Skipping column {column}.")
        else:
             print(f"Error checking {column} in {table}: {e}")

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting schema fix...")

    # 1. audit_logs.resource
    add_column_if_not_exists(cursor, "audit_logs", "resource", "TEXT")

    # 2. employee_satisfaction columns
    add_column_if_not_exists(cursor, "employee_satisfaction", "satisfaction_score", "REAL")
    add_column_if_not_exists(cursor, "employee_satisfaction", "year", "INTEGER")

    # CSRD Records (Correct table name: csrd_materiality)
    # Note: Removing DEFAULT CURRENT_TIMESTAMP to avoid SQLite "non-constant default" error on ALTER TABLE
    add_column_if_not_exists(cursor, "csrd_materiality", "created_at", "TIMESTAMP")

    # EU Taxonomy (Correct table name: taxonomy_activities)
    add_column_if_not_exists(cursor, "taxonomy_activities", "turnover_aligned", "REAL")

    # 5. esrs_materiality.impact_score
    add_column_if_not_exists(cursor, "esrs_materiality", "impact_score", "REAL")

    # Stakeholder Engagement (Plural)
    add_column_if_not_exists(cursor, "stakeholder_engagements", "stakeholder_group", "TEXT")

    # Stakeholder Engagement (Singular - kept for legacy/typo fallback if table exists)
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stakeholder_engagement'")
        if cursor.fetchone():
            add_column_if_not_exists(cursor, "stakeholder_engagement", "stakeholder_group", "TEXT")
    except:
        pass
    
    conn.commit()
    conn.close()
    print("Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
