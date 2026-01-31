import sqlite3
import json
import os
import sys

# Remote path
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
JSON_PATH = '/var/www/sustainage/backend/data/sdg_data_dump.json'

def update_sdg_module():
    print(f"Connecting to {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create Master Tables (Goals, Targets, Indicators)
    print("Creating Master Tables...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code INTEGER UNIQUE NOT NULL,
            title_tr TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES sdg_goals(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            data_source TEXT,
            measurement_frequency TEXT,
            related_sectors TEXT,
            related_funds TEXT,
            kpi_metric TEXT,
            implementation_requirement TEXT,
            notes TEXT,
            request_status TEXT,
            status TEXT,
            progress_percentage REAL,
            completeness_percentage REAL,
            policy_document_exists TEXT,
            data_quality TEXT,
            incentive_readiness_score REAL,
            readiness_level TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES sdg_targets(id)
        )
    """)

    # 2. Create sdg_responses Table (Renamed from responses)
    print("Creating sdg_responses Table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_responses (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            indicator_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            answer_json TEXT,
            value_num REAL,
            progress_pct INTEGER DEFAULT 0,
            request_status TEXT DEFAULT 'Gönderilmedi',
            policy_flag TEXT DEFAULT 'Hayır',
            evidence_url TEXT,
            approved_by_owner TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE,
            UNIQUE(company_id, indicator_id, period)
        )
    """)

    # 3. Create user_sdg_selections
    print("Creating user_sdg_selections Table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sdg_selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            goal_id INTEGER NOT NULL,
            selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (goal_id) REFERENCES sdg_goals(id) ON DELETE CASCADE,
            UNIQUE(company_id, goal_id)
        )
    """)

    # 4. Populate Data
    print(f"Reading data from {JSON_PATH}...")
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        conn.close()
        return

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        conn.close()
        return

    # Goals
    if 'sdg_goals' in data:
        print(f"Populating {len(data['sdg_goals'])} goals...")
        for g in data['sdg_goals']:
            try:
                cursor.execute("INSERT OR REPLACE INTO sdg_goals (id, code, title_tr, created_at) VALUES (?, ?, ?, ?)",
                               (g['id'], g['code'], g['title_tr'], g.get('created_at')))
            except Exception as e:
                print(f"Error inserting goal {g.get('code')}: {e}")

    # Targets
    if 'sdg_targets' in data:
        print(f"Populating {len(data['sdg_targets'])} targets...")
        for t in data['sdg_targets']:
            try:
                cursor.execute("INSERT OR REPLACE INTO sdg_targets (id, goal_id, code, title_tr, created_at) VALUES (?, ?, ?, ?, ?)",
                               (t['id'], t['goal_id'], t['code'], t['title_tr'], t.get('created_at')))
            except Exception as e:
                print(f"Error inserting target {t.get('code')}: {e}")

    # Indicators
    if 'sdg_indicators' in data:
        print(f"Populating {len(data['sdg_indicators'])} indicators...")
        for i in data['sdg_indicators']:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO sdg_indicators 
                    (id, target_id, code, title_tr, created_at, data_source, measurement_frequency, related_sectors, related_funds, kpi_metric) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (i['id'], i['target_id'], i['code'], i['title_tr'], i.get('created_at'),
                      i.get('data_source'), i.get('measurement_frequency'), i.get('related_sectors'), i.get('related_funds'), i.get('kpi_metric')))
            except Exception as e:
                print(f"Error inserting indicator {i.get('code')}: {e}")

    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM sdg_goals")
    print(f"Goals count: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM sdg_targets")
    print(f"Targets count: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM sdg_indicators")
    print(f"Indicators count: {cursor.fetchone()[0]}")
    
    conn.close()
    print("SDG Module Update Complete.")

if __name__ == "__main__":
    update_sdg_module()
