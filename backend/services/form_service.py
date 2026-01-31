import json
import os
import sqlite3
from typing import Dict, List, Optional


class FormService:
    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_db()
        self.create_tables()

    def _ensure_db(self) -> None:
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.close()

    def get_connection(self) -> None:
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS forms (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    module TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS form_fields (
                    id INTEGER PRIMARY KEY,
                    form_id INTEGER NOT NULL,
                    field_type TEXT DEFAULT 'text',
                    label TEXT NOT NULL,
                    name TEXT NOT NULL,
                    options_json TEXT,
                    required INTEGER DEFAULT 0,
                    order_index INTEGER DEFAULT 0,
                    FOREIGN KEY (form_id) REFERENCES forms(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS form_submissions (
                    id INTEGER PRIMARY KEY,
                    form_id INTEGER NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (form_id) REFERENCES forms(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS form_submission_values (
                    id INTEGER PRIMARY KEY,
                    submission_id INTEGER NOT NULL,
                    field_id INTEGER NOT NULL,
                    value_text TEXT,
                    value_number REAL,
                    value_choice TEXT,
                    FOREIGN KEY (submission_id) REFERENCES form_submissions(id),
                    FOREIGN KEY (field_id) REFERENCES form_fields(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def create_form(self, company_id: int, name: str, description: str = None, module: str = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO forms (company_id, name, description, module) VALUES (?, ?, ?, ?)",
                (company_id, name, description, module),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_field(self, form_id: int, label: str, name: str, field_type: str = 'text', options: Optional[List[str]] = None, required: bool = False, order_index: int = 0) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        options_json = json.dumps(options or [])
        try:
            cursor.execute(
                """
                INSERT INTO form_fields (form_id, field_type, label, name, options_json, required, order_index)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (form_id, field_type, label, name, options_json, int(required), order_index),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def submit(self, form_id: int, user_id: int, company_id: int, values: Dict[str, str]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO form_submissions (form_id, user_id, company_id) VALUES (?, ?, ?)",
                (form_id, user_id, company_id),
            )
            submission_id = cursor.lastrowid

            # Map field name to id
            cursor.execute("SELECT id, name, field_type FROM form_fields WHERE form_id=?", (form_id,))
            fields = cursor.fetchall()
            field_map = {f[1]: (f[0], f[2]) for f in fields}

            for name, value in values.items():
                if name not in field_map:
                    continue
                field_id, ftype = field_map[name]
                if ftype in ('number', 'integer', 'float'):
                    cursor.execute(
                        "INSERT INTO form_submission_values (submission_id, field_id, value_number) VALUES (?, ?, ?)",
                        (submission_id, field_id, float(value)),
                    )
                elif ftype in ('choice', 'select'):
                    cursor.execute(
                        "INSERT INTO form_submission_values (submission_id, field_id, value_choice) VALUES (?, ?, ?)",
                        (submission_id, field_id, str(value)),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO form_submission_values (submission_id, field_id, value_text) VALUES (?, ?, ?)",
                        (submission_id, field_id, str(value)),
                    )
            conn.commit()
            return submission_id
        finally:
            conn.close()

    def get_form_with_fields(self, form_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, company_id, name, description, module, status, created_at FROM forms WHERE id=?", (form_id,))
            frow = cursor.fetchone()
            if not frow:
                return {}
            cursor.execute(
                "SELECT id, field_type, label, name, options_json, required, order_index FROM form_fields WHERE form_id=? ORDER BY order_index, id",
                (form_id,),
            )
            fs = cursor.fetchall()
            fields = []
            for f in fs:
                options = []
                try:
                    options = json.loads(f[4]) if f[4] else []
                except Exception:
                    options = []
                fields.append({
                    'id': f[0], 'field_type': f[1], 'label': f[2], 'name': f[3], 'options': options, 'required': bool(f[5]), 'order_index': f[6]
                })
            return {
                'id': frow[0], 'company_id': frow[1], 'name': frow[2], 'description': frow[3], 'module': frow[4], 'status': frow[5], 'created_at': frow[6],
                'fields': fields,
            }
        finally:
            conn.close()
