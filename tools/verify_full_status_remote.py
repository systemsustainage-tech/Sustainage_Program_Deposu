import sqlite3
import os
import sys

# DB Path on remote server
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def verify():
    print("--- Verifying Remote DB Status ---")
    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 1. Survey Stats
        print("\n[1] Survey Stats:")
        try:
            cur.execute("SELECT COUNT(*) FROM surveys WHERE status='active'")
            active = cur.fetchone()[0]
            print(f"Active Surveys: {active}")
            
            cur.execute("SELECT SUM(response_count) FROM surveys")
            res = cur.fetchone()[0]
            print(f"Total Responses (from surveys table): {res}")

            cur.execute("SELECT COUNT(*) FROM survey_responses")
            real_res = cur.fetchone()[0]
            print(f"Real Responses (from survey_responses table): {real_res}")
            
            # Check latest survey columns
            cur.execute("SELECT id, title, created_at FROM surveys WHERE status='active' ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
            print(f"Latest Active Survey: {row}")
            
        except Exception as e:
            print(f"Error checking surveys: {e}")

        # 2. ESRS Schema
        print("\n[2] ESRS Schema:")
        try:
            cur.execute("PRAGMA table_info(esrs_assessments)")
            columns = [r[1] for r in cur.fetchall()]
            required = ['governance_notes', 'strategy_notes', 'impact_risk_notes', 'metrics_notes']
            missing = [c for c in required if c not in columns]
            
            if missing:
                print(f"FAIL: Missing ESRS columns: {missing}")
            else:
                print("PASS: All ESRS note columns present.")
                
        except Exception as e:
            print(f"Error checking ESRS schema: {e}")

        conn.close()
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    verify()
