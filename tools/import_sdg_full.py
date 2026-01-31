import sqlite3
import pandas as pd
import json
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')
JSON_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_data.json')
EXCEL_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'SDG_16_169_232.xlsx')

def import_data():
    print(f"Connecting to DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Import Goals from JSON (has EN and TR)
    print(f"Loading Goals from {JSON_PATH}...")
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            goals_data = json.load(f)
        
        goals_map = {} # Code -> ID mapping
        
        for goal in goals_data.get('goals', []):
            code = str(goal['goal_number'])
            title_en = goal.get('title_en', '')
            title_tr = goal.get('title_tr', '')
            desc_en = goal.get('description', '')
            desc_tr = "" # JSON might not have TR description
            icon = goal.get('icon', '')

            # Check if goal exists (update if so) or insert
            # We prefer INSERT OR REPLACE or check existence. 
            # But schema has UNIQUE constraint on code.
            
            # Simple approach: Delete existing to be clean? No, we just cleared schema.
            # But duplicate runs might fail. So let's use INSERT OR REPLACE.
            
            print(f"Inserting Goal {code}: {title_en}")
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_goals (code, name_tr, name_en, description_tr, description_en, icon)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, title_tr, title_en, desc_tr, desc_en, icon))
            
            # Get the ID. If replace happened, rowid changes.
            cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (code,))
            goals_map[code] = cursor.fetchone()[0]
            
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    # 2. Import Targets and Indicators from Excel
    print(f"Loading Excel from {EXCEL_PATH}...")
    
    try:
        xls = pd.ExcelFile(EXCEL_PATH)
        target_sheet = None
        
        # Find the correct sheet
        for sheet in xls.sheet_names:
            df_preview = pd.read_excel(xls, sheet_name=sheet, nrows=1)
            # Normalize cols
            cols = [str(c).strip() for c in df_preview.columns]
            if 'Alt Hedef Kodu' in cols:
                target_sheet = sheet
                break
        
        if not target_sheet:
            print("Could not find a sheet with 'Alt Hedef Kodu' column.")
            print("Available sheets:", xls.sheet_names)
            return

        print(f"Processing sheet: {target_sheet}")
        df = pd.read_excel(xls, sheet_name=target_sheet)
        
        # Normalize column names
        df.columns = [str(c).strip() for c in df.columns]
        
        targets_map = {} # Code -> ID
        
        # Track counts
        t_count = 0
        i_count = 0
        
        for index, row in df.iterrows():
            # Goal Code
            goal_code = str(row['SDG No'])
            # Handle float/int conversion if necessary (e.g. 1.0 -> 1)
            if goal_code.endswith('.0'):
                goal_code = goal_code[:-2]
                
            if goal_code not in goals_map:
                # Sometimes rows are empty or headers repeated
                continue
            
            goal_id = goals_map[goal_code]
            
            # Target
            target_code = str(row['Alt Hedef Kodu'])
            target_name_tr = str(row['Alt Hedef Tanımı (TR)'])
            
            # Ensure target exists
            if target_code not in targets_map:
                cursor.execute("""
                    INSERT OR IGNORE INTO sdg_targets (code, name_tr, parent_id)
                    VALUES (?, ?, ?)
                """, (target_code, target_name_tr, goal_id))
                
                # Retrieve ID
                cursor.execute("SELECT id FROM sdg_targets WHERE code = ?", (target_code,))
                res = cursor.fetchone()
                if res:
                    targets_map[target_code] = res[0]
                    t_count += 1
            
            if target_code in targets_map:
                target_id = targets_map[target_code]
                
                # Indicator
                indicator_code = str(row['Gösterge Kodu'])
                if pd.isna(indicator_code) or indicator_code == 'nan':
                    continue
                    
                indicator_name_tr = str(row['Gösterge Tanımı (TR)'])
                gri_map = str(row.get('GRI Bağlantısı', ''))
                tsrs_map = str(row.get('TSRS Bağlantısı', ''))
                
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_indicators (code, name_tr, parent_id, gri_mapping, tsrs_mapping)
                    VALUES (?, ?, ?, ?, ?)
                """, (indicator_code, indicator_name_tr, target_id, gri_map, tsrs_map))
                i_count += 1

        conn.commit()
        print(f"Imported {len(goals_map)} Goals, {t_count} Targets, {i_count} Indicators.")
        
    except Exception as e:
        print(f"Error loading Excel: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()
    print("Data import completed.")

if __name__ == "__main__":
    import_data()
