import json
import os
import sqlite3
from typing import Dict, List, Optional


class SurveyService:
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
                CREATE TABLE IF NOT EXISTS surveys (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_questions (
                    id INTEGER PRIMARY KEY,
                    survey_id INTEGER NOT NULL,
                    q_type TEXT DEFAULT 'text',
                    text TEXT NOT NULL,
                    options_json TEXT,
                    required INTEGER DEFAULT 0,
                    order_index INTEGER DEFAULT 0,
                    FOREIGN KEY (survey_id) REFERENCES surveys(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_responses (
                    id INTEGER PRIMARY KEY,
                    survey_id INTEGER NOT NULL,
                    user_id INTEGER,
                    company_id INTEGER,
                    submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (survey_id) REFERENCES surveys(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS survey_answers (
                    id INTEGER PRIMARY KEY,
                    response_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    answer_text TEXT,
                    answer_number REAL,
                    answer_choice TEXT,
                    FOREIGN KEY (response_id) REFERENCES survey_responses(id),
                    FOREIGN KEY (question_id) REFERENCES survey_questions(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def create_survey(self, company_id: int, name: str, description: str = None, status: str = 'draft') -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO surveys (company_id, name, description, status) VALUES (?, ?, ?, ?)",
                (company_id, name, description, status),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_question(self, survey_id: int, text: str, q_type: str = 'text', options: Optional[List[str]] = None, required: bool = False, order_index: int = 0) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        options_json = json.dumps(options or [])
        try:
            cursor.execute(
                """
                INSERT INTO survey_questions (survey_id, q_type, text, options_json, required, order_index)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (survey_id, q_type, text, options_json, int(required), order_index),
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def submit_response(self, survey_id: int, user_id: int, company_id: int, answers: Dict[int, str]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO survey_responses (survey_id, user_id, company_id) VALUES (?, ?, ?)",
                (survey_id, user_id, company_id),
            )
            response_id = cursor.lastrowid
            for qid, value in answers.items():
                # Store as text; numeric can be parsed later if needed
                cursor.execute(
                    "INSERT INTO survey_answers (response_id, question_id, answer_text) VALUES (?, ?, ?)",
                    (response_id, qid, str(value)),
                )
            conn.commit()
            return response_id
        finally:
            conn.close()

    def get_survey_with_questions(self, survey_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, company_id, name, description, status, created_at FROM surveys WHERE id=?", (survey_id,))
            srow = cursor.fetchone()
            if not srow:
                return {}
            cursor.execute(
                "SELECT id, q_type, text, options_json, required, order_index FROM survey_questions WHERE survey_id=? ORDER BY order_index, id",
                (survey_id,),
            )
            qs = cursor.fetchall()
            questions = []
            for q in qs:
                options = []
                try:
                    options = json.loads(q[3]) if q[3] else []
                except Exception:
                    options = []
                questions.append({
                    'id': q[0], 'q_type': q[1], 'text': q[2], 'options': options, 'required': bool(q[4]), 'order_index': q[5]
                })
            return {
                'id': srow[0], 'company_id': srow[1], 'name': srow[2], 'description': srow[3], 'status': srow[4], 'created_at': srow[5],
                'questions': questions,
            }
        finally:
            conn.close()

    def get_results(self, survey_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, user_id, company_id, submitted_at FROM survey_responses WHERE survey_id=? ORDER BY submitted_at DESC", (survey_id,))
            responses = cursor.fetchall()
            results = []
            for r in responses:
                cursor.execute(
                    "SELECT question_id, answer_text, answer_number, answer_choice FROM survey_answers WHERE response_id=?",
                    (r[0],),
                )
                answers = cursor.fetchall()
                results.append({
                    'response_id': r[0], 'user_id': r[1], 'company_id': r[2], 'submitted_at': r[3],
                    'answers': [
                        {'question_id': a[0], 'answer_text': a[1], 'answer_number': a[2], 'answer_choice': a[3]}
                        for a in answers
                    ]
                })
            return results
        finally:
            conn.close()
