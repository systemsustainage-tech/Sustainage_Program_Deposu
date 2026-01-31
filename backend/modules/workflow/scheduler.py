#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit Planlama ve İş Kayıt İskeleti
- Rapor e-postası gibi işleri zamanlamak ve çalıştırmak için temel sınıflar
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class JobType(str, Enum):
    REPORT_EMAIL = "REPORT_EMAIL"


class JobStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Job:
    id: int
    job_type: JobType
    run_at: datetime
    status: JobStatus = JobStatus.DRAFT
    params: Dict = field(default_factory=dict)
    result: Optional[Dict] = None


class JobRegistry:
    def __init__(self, store=None):
        self._jobs: Dict[int, Job] = {}
        self._next_id: int = 1
        self._store = store

    def create_job(self, job_type: JobType, run_at: datetime, params: Dict) -> Job:
        job = Job(id=self._next_id, job_type=job_type, run_at=run_at, params=params)
        self._jobs[job.id] = job
        self._next_id += 1
        if self._store:
            # Persist as DRAFT initially
            job_id = self._store.create_job(
                job_type=job.job_type,
                run_at=job.run_at,
                status=job.status,
                params=job.params,
            )
            job.id = job_id
            self._jobs[job.id] = job
        return job

    def schedule_job(self, job_id: int) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = JobStatus.SCHEDULED
        if self._store:
            self._store.update_job_status(job_id=job.id, status=job.status)
        return True

    def start_job(self, job_id: int) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = JobStatus.RUNNING
        if self._store:
            self._store.update_job_status(job_id=job.id, status=job.status)
        return True

    def complete_job(self, job_id: int, result: Dict) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = JobStatus.COMPLETED
        job.result = result
        if self._store:
            self._store.update_job_status(job_id=job.id, status=job.status, result=result)
        return True

    def fail_job(self, job_id: int, error: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.status = JobStatus.FAILED
        job.result = {"error": error}
        if self._store:
            self._store.update_job_status(job_id=job.id, status=job.status, result=job.result)
        return True

    def list_jobs(self) -> List[Job]:
        return list(self._jobs.values())

    def get_job(self, job_id: int) -> Optional[Job]:
        return self._jobs.get(job_id)

    def run_due_jobs(self, now: Optional[datetime] = None) -> List[Job]:
        now = now or datetime.now()
        ran: List[Job] = []
        for job in self._jobs.values():
            if job.status == JobStatus.SCHEDULED and job.run_at <= now:
                self.start_job(job.id)
                try:
                    result = self._perform(job)
                    self.complete_job(job.id, result)
                except Exception as e:
                    self.fail_job(job.id, str(e))
                ran.append(job)
        return ran

    def _perform(self, job: Job) -> Dict:
        if job.job_type == JobType.REPORT_EMAIL:
            # Beklenen params: recipients (List[str]), subject (str), body (str), attachments (List[str])
            from modules.reporting.emailer import Emailer
            em = Emailer()
            ok = em.send_report(
                recipients=job.params.get("recipients", []),
                subject=job.params.get("subject", ""),
                body=job.params.get("body", ""),
                attachments=job.params.get("attachments", []),
            )
            return {"ok": ok}
        else:
            raise ValueError(f"Bilinmeyen iş tipi: {job.job_type}")
