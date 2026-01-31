import logging
import os
import sqlite3
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sdg_desktop.sqlite')

def list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [r[0] for r in cur.fetchall()]

def get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def add_column(conn: sqlite3.Connection, table: str, column: str, type_sql: str) -> bool:
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_sql}")
        return True
    except Exception:
        return False

def apply_migration(db_path: str) -> Dict[str, List[str]]:
    if not os.path.isabs(db_path):
        db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    applied: Dict[str, List[str]] = {}
    skipped: Dict[str, List[str]] = {}
    try:
        tables = set(list_tables(conn))
        plan: Dict[str, Dict[str, str]] = {
            # Emisyon toplamı alanları
            'scope1_emissions': {'total_emissions': 'REAL DEFAULT 0'},
            'scope2_emissions': {'total_emissions': 'REAL DEFAULT 0'},
            'scope3_emissions': {'total_emissions': 'REAL DEFAULT 0'},
            'carbon_emissions': {'total_emissions': 'REAL DEFAULT 0'},
            'cbam_emissions': {'total_emissions': 'REAL DEFAULT 0'},
            # Yanıt alanları
            'tsrs_responses': {'response': 'TEXT'},
            'sasb_metric_responses': {'response': 'TEXT'},
            'survey_responses': {'response': 'TEXT'},
            'responses': {'response': 'TEXT'},
            # Modül adı alanı (raporlama/kalite skor grup anahtarı)
            'audit_logs': {'module_name': 'TEXT'},
            'missing_data_alerts': {'module_name': 'TEXT'},
            'yearly_comparisons': {'module_name': 'TEXT'},
        }

        for table, cols in plan.items():
            if table not in tables:
                continue
            existing = set(get_columns(conn, table))
            for col, type_sql in cols.items():
                if col in existing:
                    skipped.setdefault(table, []).append(col)
                    continue
                ok = add_column(conn, table, col, type_sql)
                if ok:
                    applied.setdefault(table, []).append(col)
                else:
                    skipped.setdefault(table, []).append(col)

        conn.commit()
        return {'applied': applied, 'skipped': skipped}
    finally:
        conn.close()

if __name__ == '__main__':
    db = DB_PATH
    # Normalize path to project data directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    candidate = os.path.join(project_root, 'data', 'sdg_desktop.sqlite')
    if os.path.exists(candidate):
        db = candidate
    result = apply_migration(db)
    logging.info('Applied changes:')
    for t, cols in result['applied'].items():
        logging.info(f"  {t}: {', '.join(cols)}")
    logging.info('Skipped/existing:')
    for t, cols in result['skipped'].items():
        logging.info(f"  {t}: {', '.join(cols)}")
