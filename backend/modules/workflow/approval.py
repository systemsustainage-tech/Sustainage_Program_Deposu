#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit Onay İş Akışı İskeleti
- Tamamlanan işler için onay talebi, onaylama ve reddetme
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ApprovalRequest:
    id: int
    job_id: int
    status: ApprovalStatus
    created_at: datetime
    decided_at: Optional[datetime] = None
    approver: Optional[str] = None
    comment: Optional[str] = None


class ApprovalService:
    def __init__(self, store=None):
        self._next_id: int = 1
        self._requests: Dict[int, ApprovalRequest] = {}
        self._store = store

    def request(self, job_id: int) -> ApprovalRequest:
        req = ApprovalRequest(
            id=self._next_id,
            job_id=job_id,
            status=ApprovalStatus.PENDING,
            created_at=datetime.now(),
        )
        self._requests[req.id] = req
        self._next_id += 1
        if self._store:
            req_id = self._store.create_approval(job_id=job_id)
            req.id = req_id
            self._requests[req.id] = req
        return req

    def approve(self, request_id: int, approver: str, comment: Optional[str] = None) -> bool:
        req = self._requests.get(request_id)
        if not req:
            return False
        req.status = ApprovalStatus.APPROVED
        req.decided_at = datetime.now()
        req.approver = approver
        req.comment = comment
        if self._store:
            self._store.set_approval(approval_id=req.id, status=req.status, approver=approver, comment=comment)
        return True

    def reject(self, request_id: int, approver: str, comment: Optional[str] = None) -> bool:
        req = self._requests.get(request_id)
        if not req:
            return False
        req.status = ApprovalStatus.REJECTED
        req.decided_at = datetime.now()
        req.approver = approver
        req.comment = comment
        if self._store:
            self._store.set_approval(approval_id=req.id, status=req.status, approver=approver, comment=comment)
        return True

    def get(self, request_id: int) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)
