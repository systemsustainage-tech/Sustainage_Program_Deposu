import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

STATUS_NOT_STARTED = 'not_started'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_BLOCKED = 'blocked'
STATUS_COMPLETED = 'completed'


class ProgressEngine:
    """Modül bazlı adım ilerleme motoru (genel)
    - user_module_progress: kullanıcı/şirket/modül bazlı adım durum takibi
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sdg_desktop.sqlite')
        self._create_tables()

    def _create_tables(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                company_id INTEGER,
                module_code TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_title TEXT,
                status TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                UNIQUE(company_id, user_id, module_code, step_id)
            )
            """
        )
        conn.commit()
        conn.close()

    def set_progress(self, user_id: int, company_id: int, module_code: str, step_id: str,
                     step_title: str, status: str, notes: Optional[str] = None) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec='seconds')
        cursor.execute(
            """
            INSERT INTO user_module_progress (user_id, company_id, module_code, step_id, step_title, status, updated_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(company_id, user_id, module_code, step_id)
            DO UPDATE SET status=excluded.status, updated_at=excluded.updated_at, step_title=excluded.step_title, notes=excluded.notes
            """,
            (user_id, company_id, module_code, step_id, step_title, status, now, notes)
        )
        conn.commit()
        conn.close()

    def get_module_progress(self, company_id: int, module_code: str, user_id: Optional[int] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if user_id is not None:
                cursor.execute(
                    """
                    SELECT step_id, step_title, status, updated_at
                    FROM user_module_progress
                    WHERE company_id = ? AND module_code = ? AND user_id = ?
                    ORDER BY updated_at DESC
                    """,
                    (company_id, module_code, user_id)
                )
            else:
                cursor.execute(
                    """
                    SELECT step_id, step_title, status, updated_at
                    FROM user_module_progress
                    WHERE company_id = ? AND module_code = ?
                    ORDER BY updated_at DESC
                    """,
                    (company_id, module_code)
                )
            rows = cursor.fetchall()
            return [
                {
                    'step_id': r[0], 'step_title': r[1], 'status': r[2], 'updated_at': r[3]
                } for r in rows
            ]
        finally:
            conn.close()

    def get_completion_percentage(self, company_id: int, module_code: str,
                                  steps: List[Tuple[str, str]], user_id: Optional[int] = None) -> float:
        progress = self.get_module_progress(company_id, module_code, user_id)
        status_map = {p['step_id']: p['status'] for p in progress}
        total = len(steps) or 1
        completed = sum(1 for sid, _ in steps if status_map.get(sid) == STATUS_COMPLETED)
        return round((completed / total) * 100.0, 1)

    def initialize_steps(self, user_id: int, company_id: int, module_code: str,
                         steps: List[Tuple[str, str]]) -> None:
        for sid, title in steps:
            self.set_progress(user_id, company_id, module_code, sid, title, STATUS_NOT_STARTED)

