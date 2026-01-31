#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
Güvenlik Core - Hardware ID Modülü
SUSTAINAGE-SDG'den adapte edilmiş donanım kimliği sistemi
"""

import hashlib
import subprocess
import uuid


def _sha256(txt: str) -> str:
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()

def _wmic_first(cmd: str) -> str:
    try:
        out = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.DEVNULL, text=True
        )
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        if len(lines) >= 2:
            return lines[1]
    except Exception as e:
        logging.error(f'Silent error in hw.py: {str(e)}')
    return ""

def snapshot() -> dict:
    """
    Disk seri, CPU ID, MAC (hash) alır.
    """
    disk = _wmic_first("wmic diskdrive get SerialNumber")
    cpu  = _wmic_first("wmic cpu get ProcessorId")
    mac  = _sha256(str(uuid.getnode()))
    return {"disk": disk, "cpu": cpu, "mac": mac}

def hwid_full_core() -> None:
    s = snapshot()
    full = _sha256(f"{s.get('disk','')}|{s.get('cpu','')}|{s.get('mac','')}")
    core = _sha256(f"{s.get('disk','')}|{s.get('cpu','')}")
    return s, full, core

def get_hwid_info() -> None:
    """Donanım kimliği bilgilerini getir"""
    try:
        s, full, core = hwid_full_core()
        return {
            'disk_serial': s.get('disk', ''),
            'cpu_id': s.get('cpu', ''),
            'mac_hash': s.get('mac', ''),
            'hwid_core': core,
            'hwid_full': full
        }
    except Exception as e:
        return {
            'disk_serial': '',
            'cpu_id': '',
            'mac_hash': '',
            'hwid_core': '',
            'hwid_full': '',
            'error': str(e)
        }