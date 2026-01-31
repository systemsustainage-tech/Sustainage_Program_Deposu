import sqlite3
import os
import sys
import logging

# Define database path
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Connecting to database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Fix esrs_materiality table
        print("Checking esrs_materiality table...")
        try:
            cursor.execute("SELECT * FROM esrs_materiality LIMIT 1")
            columns = [description[0] for description in cursor.description]
            print(f"Current columns in esrs_materiality: {columns}")
            
            missing_cols = []
            if 'impact_score' not in columns: missing_cols.append(('impact_score', 'INTEGER'))
            if 'likelihood' not in columns: missing_cols.append(('likelihood', 'INTEGER'))
            if 'financial_effect' not in columns: missing_cols.append(('financial_effect', 'TEXT'))
            if 'environmental_effect' not in columns: missing_cols.append(('environmental_effect', 'TEXT'))
            
            for col, type_ in missing_cols:
                print(f"Adding column {col} to esrs_materiality...")
                cursor.execute(f"ALTER TABLE esrs_materiality ADD COLUMN {col} {type_}")
        except Exception as e:
            print(f"Error checking esrs_materiality: {e}")
            # If table doesn't exist, maybe create it? But error said "no such column", so table exists.

        # 2. Fix sdg_indicators table
        print("Checking sdg_indicators table...")
        try:
            cursor.execute("SELECT * FROM sdg_indicators LIMIT 1")
            columns = [description[0] for description in cursor.description]
            print(f"Current columns in sdg_indicators: {columns}")
            
            if 'name_tr' not in columns:
                print("Adding column name_tr to sdg_indicators...")
                cursor.execute("ALTER TABLE sdg_indicators ADD COLUMN name_tr TEXT")
                # Optionally copy name_en to name_tr or something?
                # cursor.execute("UPDATE sdg_indicators SET name_tr = name_en WHERE name_tr IS NULL") 
                # (Assuming name_en exists, but let's just add the column for now to prevent crash)
        except Exception as e:
            print(f"Error checking sdg_indicators: {e}")

        # 3. Fix stakeholders table
        print("Checking stakeholders table...")
        try:
            cursor.execute("SELECT * FROM stakeholders LIMIT 1")
            columns = [description[0] for description in cursor.description]
            print(f"Current columns in stakeholders: {columns}")
            
            if 'stakeholder_group' not in columns:
                print("Adding column stakeholder_group to stakeholders...")
                cursor.execute("ALTER TABLE stakeholders ADD COLUMN stakeholder_group TEXT")
        except Exception as e:
            print(f"Error checking stakeholders: {e}")
            
        # 4. Fix csrd_materiality table (just in case)
        print("Checking csrd_materiality table...")
        try:
            cursor.execute("SELECT * FROM csrd_materiality LIMIT 1")
            columns = [description[0] for description in cursor.description]
            print(f"Current columns in csrd_materiality: {columns}")
            
            if 'impact_score' not in columns:
                print("Adding column impact_score to csrd_materiality...")
                cursor.execute("ALTER TABLE csrd_materiality ADD COLUMN impact_score INTEGER")
            if 'financial_score' not in columns:
                print("Adding column financial_score to csrd_materiality...")
                cursor.execute("ALTER TABLE csrd_materiality ADD COLUMN financial_score INTEGER")
        except Exception as e:
            print(f"Error checking csrd_materiality: {e}")

        conn.commit()
        conn.close()
        print("Schema fix completed successfully.")

    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    fix_schema()
