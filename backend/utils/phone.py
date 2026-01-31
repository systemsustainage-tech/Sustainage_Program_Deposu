#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telefon Biçimlendirme ve Doğrulama Yardımcıları (Türkiye)

- format_tr_phone: Girilen değeri "+90 (XXX) XXX XX XX" biçimine dönüştürür.
- is_valid_tr_phone: Türkiye telefon numarası format geçerliliğini kontrol eder.
"""

import re


def _digits_only(s: str) -> str:
    """Metinden sadece rakamları ayıkla."""
    return re.sub(r"\D", "", s or "")


def _normalize_national_number(s: str) -> str:
    """
    Girilen değerden ülke/trunk kodlarını ayıklayarak 10 haneli ulusal numarayı döndür.
    Kabul edilen girdiler: 10 hane, 0 ile başlayan 11 hane, 90 ile başlayan 12+ hane, 905XXXXXXXXX.
    """
    if not s:
        return ""
    digits = _digits_only(s)
    if not digits:
        return ""

    # 90 ile başlayan (ülke kodu) -> son 10 hane
    if digits.startswith("90") and len(digits) >= 12:
        return digits[-10:]
    # 0 ile başlayan (trunk) -> 2..11 arası 10 hane
    if digits.startswith("0") and len(digits) >= 11:
        return digits[1:11]
    # 905XXXXXXXXX (11 hane) -> son 10 hane
    if len(digits) == 11 and digits.startswith("90"):
        return digits[-10:]
    # 10 hane doğrudan
    if len(digits) >= 10:
        return digits[-10:]

    # Eksik/incomplete -> olduğu gibi
    return ""


def format_tr_phone(s: str) -> str:
    """
    Girilen telefon değerini "+90 (XXX) XXX XX XX" biçimine dönüştür.
    Geçerli bir 10 haneli ulusal numara elde edilemezse girdiyi kırpıp döndürür.
    """
    if not s:
        return ""
    national = _normalize_national_number(s)
    if national and len(national) == 10:
        return f"+90 ({national[0:3]}) {national[3:6]} {national[6:8]} {national[8:10]}"
    return s.strip()


def is_valid_tr_phone(s: str) -> bool:
    """
    Türkiye telefon geçerliliği kontrolü.
    Kabul: +90, 90 veya 0 prefiksi ile 10 haneli ulusal numara.
    Örnek geçerler: "+90 (532) 123 45 67", "0(532)1234567", "05321234567", "905321234567", "5321234567"
    """
    if not s:
        return False
    cleaned = re.sub(r"[^\d+]", "", s.strip())
    return bool(re.match(r"^(\+?90|0)?[1-9]\d{9}$", cleaned))
