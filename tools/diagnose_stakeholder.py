import sqlite3
import os
import sys

# Define database path
DB_PATH = '/var/www/sustainage/sustainage.db'

def check_stakeholder_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # List of tables to check
        tables = [
            'stakeholders', 
            'stakeholder_engagements', 
            'stakeholder_surveys', 
            'stakeholder_complaints',
            'stakeholder_survey_templates',
            'stakeholder_action_plans',
            'online_surveys'
        ]
        
        print(f"Checking tables in {DB_PATH}...")
        
        for table in tables:
            print(f"\n--- Table: {table} ---")
            
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"Status: MISSING")
                continue
                
            print(f"Status: EXISTS")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Row count: {count}")
            except Exception as e:
                print(f"Error counting rows: {e}")
                
            # Get schema
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                print("Columns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
            except Exception as e:
                print(f"Error getting schema: {e}")
                
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    check_stakeholder_tables()
