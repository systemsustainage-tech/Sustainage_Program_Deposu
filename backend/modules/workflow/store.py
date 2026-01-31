#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Tabanlı Kalıcı Store
- İşler ve onay talepleri için basit kalıcılık katmanı
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DEFAULT_DB = os.path.join('data', 'db', 'workflow.sqlite')


class WorkflowStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_type TEXT NOT NULL,
                    run_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    params TEXT,
                    result TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    decided_at TEXT,
                    approver TEXT,
                    comment TEXT,
                    FOREIGN KEY(job_id) REFERENCES jobs(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    # Jobs
    def create_job(self, job_type: str, run_at: datetime, status: str, params: Dict) -> int:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO jobs(job_type, run_at, status, params, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_type, run_at.isoformat(), status, json.dumps(params or {}), datetime.now().isoformat()),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def update_job_status(self, job_id: int, status: str, result: Optional[Dict] = None) -> bool:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE jobs SET status = ?, result = ?, updated_at = ? WHERE id = ?
                """,
                (status, json.dumps(result) if result is not None else None, datetime.now().isoformat(), job_id),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def get_job(self, job_id: int) -> Optional[Dict]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, job_type, run_at, status, params, result FROM jobs WHERE id = ?", (job_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'job_type': row[1],
                'run_at': row[2],
                'status': row[3],
                'params': json.loads(row[4]) if row[4] else {},
                'result': json.loads(row[5]) if row[5] else None,
            }
        finally:
            conn.close()

    def list_jobs(self) -> List[Dict]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, job_type, run_at, status FROM jobs ORDER BY id DESC")
            return [
                {'id': r[0], 'job_type': r[1], 'run_at': r[2], 'status': r[3]}
                for r in cur.fetchall()
            ]
        finally:
            conn.close()

    # Approvals
    def create_approval(self, job_id: int) -> int:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO approvals(job_id, status, created_at)
                VALUES (?, ?, ?)
                """,
                (job_id, 'PENDING', datetime.now().isoformat()),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def set_approval(self, approval_id: int, status: str, approver: Optional[str], comment: Optional[str]) -> bool:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE approvals
                SET status = ?, decided_at = ?, approver = ?, comment = ?
                WHERE id = ?
                """,
                (status, datetime.now().isoformat(), approver, comment, approval_id),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def get_approval(self, approval_id: int) -> Optional[Dict]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, job_id, status, created_at, decided_at, approver, comment FROM approvals WHERE id = ?",
                (approval_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                'id': row[0],
                'job_id': row[1],
                'status': row[2],
                'created_at': row[3],
                'decided_at': row[4],
                'approver': row[5],
                'comment': row[6],
            }
        finally:
            conn.close()
