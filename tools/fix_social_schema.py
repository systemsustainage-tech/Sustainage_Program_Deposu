import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Fixing employee_satisfaction table...")
    
    # Check existing columns
    cur.execute("PRAGMA table_info(employee_satisfaction)")
    columns = [col[1] for col in cur.fetchall()]
    
    cols_to_add = {
        'turnover_rate': 'REAL',
        'participation_rate': 'REAL',
        'comments': 'TEXT',
        'survey_date': 'DATE',
        'year': 'INTEGER', # In case survey_year is not enough or to align with my code
        'satisfaction_score': 'REAL' # To align with my code if average_score is not enough
    }

    for col_name, col_type in cols_to_add.items():
        if col_name not in columns:
            try:
                print(f"Adding column {col_name}...")
                cur.execute(f"ALTER TABLE employee_satisfaction ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
