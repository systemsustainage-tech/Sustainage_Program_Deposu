import sqlite3
import os
import sys

# Define DB path based on environment or hardcode for remote
DB_PATH = '/var/www/sustainage/sustainage.db'
SDG_SOURCE_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def patch_db():
    global DB_PATH
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Try finding it in current directory or instance
        if os.path.exists('sustainage.db'):
            DB_PATH = 'sustainage.db'
        elif os.path.exists('instance/sustainage.db'):
            DB_PATH = 'instance/sustainage.db'
        else:
            print("Could not locate sustainage.db")
            return

    print(f"Connecting to {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    except Exception as e:
        print(f"Failed to connect to DB: {e}")
        return

    # 1. Check survey_responses for stakeholder_group
    try:
        cursor.execute("PRAGMA table_info(survey_responses)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'stakeholder_group' not in columns:
            print("Adding stakeholder_group to survey_responses...")
            cursor.execute("ALTER TABLE survey_responses ADD COLUMN stakeholder_group TEXT")
            print("Added stakeholder_group.")
        else:
            print("stakeholder_group already exists in survey_responses.")
    except Exception as e:
        print(f"Error patching survey_responses: {e}")

    # 2. Check sdg_goals and Import if missing
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sdg_goals'")
        if not cursor.fetchone():
            print("sdg_goals table missing. Attempting to import from sdg_desktop.sqlite...")
            
            if not os.path.exists(SDG_SOURCE_PATH):
                print(f"Source SDG DB not found at {SDG_SOURCE_PATH}")
                # Try relative path just in case
                if os.path.exists('backend/data/sdg_desktop.sqlite'):
                    SDG_SOURCE_PATH_REAL = 'backend/data/sdg_desktop.sqlite'
                else:
                    print("Could not find sdg_desktop.sqlite to import from.")
                    SDG_SOURCE_PATH_REAL = None
            else:
                SDG_SOURCE_PATH_REAL = SDG_SOURCE_PATH

            if SDG_SOURCE_PATH_REAL:
                print(f"Attaching {SDG_SOURCE_PATH_REAL}...")
                cursor.execute(f"ATTACH DATABASE '{SDG_SOURCE_PATH_REAL}' AS sdg_db")
                
                # Copy tables
                tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators']
                for table in tables:
                    print(f"Copying {table}...")
                    cursor.execute(f"CREATE TABLE main.{table} AS SELECT * FROM sdg_db.{table}")
                
                cursor.execute("DETACH DATABASE sdg_db")
                print("SDG tables imported successfully.")
                
                # Verify name_tr exists in the imported table
                cursor.execute("PRAGMA table_info(sdg_goals)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'name_tr' not in columns:
                     print("Imported sdg_goals missing name_tr. Adding...")
                     cursor.execute("ALTER TABLE sdg_goals ADD COLUMN name_tr TEXT")
                     if 'title' in columns:
                         cursor.execute("UPDATE sdg_goals SET name_tr = title")
                     elif 'name' in columns:
                         cursor.execute("UPDATE sdg_goals SET name_tr = name")
            else:
                print("Skipping SDG import due to missing source.")
        else:
            print("sdg_goals table exists.")
            # Check for name_tr
            cursor.execute("PRAGMA table_info(sdg_goals)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'name_tr' not in columns:
                print("Adding name_tr to sdg_goals...")
                cursor.execute("ALTER TABLE sdg_goals ADD COLUMN name_tr TEXT")
                if 'title' in columns:
                     cursor.execute("UPDATE sdg_goals SET name_tr = title")
                elif 'name' in columns:
                     cursor.execute("UPDATE sdg_goals SET name_tr = name")
                print("Added name_tr.")
            else:
                print("name_tr already exists in sdg_goals.")
                
    except Exception as e:
        print(f"Error patching sdg_goals: {e}")

    # 3. Check esrs_materiality for impact_score
    try:
        cursor.execute("PRAGMA table_info(esrs_materiality)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'impact_score' not in columns:
            print("Adding impact_score to esrs_materiality...")
            cursor.execute("ALTER TABLE esrs_materiality ADD COLUMN impact_score REAL DEFAULT 0")
            print("Added impact_score.")
        else:
            print("impact_score already exists in esrs_materiality.")
    except Exception as e:
        print(f"Error patching esrs_materiality: {e}")
        
    # 4. Check stakeholders for stakeholder_group
    try:
        cursor.execute("PRAGMA table_info(stakeholders)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'stakeholder_group' not in columns:
             print("Adding stakeholder_group to stakeholders table (precautionary)...")
             cursor.execute("ALTER TABLE stakeholders ADD COLUMN stakeholder_group TEXT")
             print("Added stakeholder_group to stakeholders.")
        else:
            print("stakeholder_group already exists in stakeholders.")
    except Exception as e:
        print(f"Error patching stakeholders: {e}")

    conn.commit()
    conn.close()
    print("Database patch completed.")

if __name__ == "__main__":
    patch_db()
