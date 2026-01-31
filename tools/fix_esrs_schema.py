import os
import sqlite3
import sys

def get_db_path():
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.database import DB_PATH
        # Prefer desktop DB if present on remote
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return DB_PATH
    except Exception:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.name == 'nt':
            return os.path.join(base_dir, 'backend', 'data', 'sdg_desktop.sqlite')
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return '/var/www/sustainage/sustainage.db'

def ensure_esrs_notes(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='esrs_assessments'")
    if not cur.fetchone():
        cur.execute("CREATE TABLE IF NOT EXISTS esrs_assessments (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id INTEGER, standard_code TEXT, status TEXT)")
        conn.commit()
    cur.execute("PRAGMA table_info(esrs_assessments)")
    cols = [r[1] for r in cur.fetchall()]
    added = []
    for c in ['governance_notes', 'strategy_notes', 'impact_risk_notes', 'metrics_notes']:
        if c not in cols:
            cur.execute(f"ALTER TABLE esrs_assessments ADD COLUMN {c} TEXT")
            added.append(c)
    conn.commit()
    conn.close()
    print(f"ESRS schema fix done. Added: {added}")

if __name__ == "__main__":
    db_path = get_db_path()
    print(f"DB_PATH: {db_path}")
    ensure_esrs_notes(db_path)
