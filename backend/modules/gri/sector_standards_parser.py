import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Sektörel Standartlar PDF Parser İskeleti
- 14 sektörel PDF için metin çıkarımı ve basit bölümleme
- pdfminer.six varsa kullanır, yoksa basit okuma yapar
"""

import os
import re
from typing import Dict, List

try:
    from pdfminer.high_level import extract_text  # type: ignore
    from pdfminer.layout import LAParams  # type: ignore
    PDFMINER_AVAILABLE = True
except Exception:
    PDFMINER_AVAILABLE = False
    logging.info("[WARN] pdfminer.six not available. Using fallback read.")


def _normalize_text(text: str) -> str:
    """Metni normalize eder: gereksiz boşlukları ve kontrol karakterlerini temizler."""
    # CRLF -> LF
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Birden fazla boşluğu tek boşluğa indir
    text = re.sub(r"[\t\x0b\x0c]", " ", text)
    text = re.sub(r" +", " ", text)
    # Birden fazla boş satırı tek satıra indir
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf_text(path: str) -> str:
    if PDFMINER_AVAILABLE:
        try:
            laparams = LAParams(char_margin=2.0, word_margin=0.1, line_margin=0.5)
            text = extract_text(path, laparams=laparams)
            return _normalize_text(text)
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    # Fallback: naive binary read -> decode best-effort
    try:
        with open(path, 'rb') as f:
            data = f.read()
        return _normalize_text(data.decode('utf-8', errors='ignore'))
    except Exception:
        return ""


def split_sections(text: str) -> List[Dict[str, str]]:
    """
    Gelişmiş bölümleme: GRI başlıklarını ve gereklilik bölümlerini yakalamaya çalışır.

    Heuristikler:
    - Satır başı anahtar kelimeler: Disclosure, Requirement, Topic, Scope, Sector, Metric
    - Büyük harfli başlıklar veya iki nokta ile biten satırlar
    - "General Requirements", "Introduction", "Application", "Definitions" gibi genel bölümler
    """
    if not text:
        return []

    heading_patterns = [
        r"^(Disclosure\b.*)",
        r"^(Requirement\b.*)",
        r"^(Topic\b.*)",
        r"^(Scope\b.*)",
        r"^(Sector\b.*)",
        r"^(Metric\b.*)",
        r"^(General Requirements\b.*)",
        r"^(Introduction\b.*)",
        r"^(Application\b.*)",
        r"^(Definitions\b.*)",
    ]
    heading_regexes = [re.compile(p, re.IGNORECASE) for p in heading_patterns]

    def is_heading(line: str) -> bool:
        ls = line.strip()
        if not ls:
            return False
        # Anahtar kelime eşleşmesi
        for rx in heading_regexes:
            if rx.match(ls):
                return True
        # Tamamen büyük harf ve kısa satırlar başlık olabilir
        if len(ls) <= 80 and re.match(r"^[A-Z0-9 \-/&]+$", ls) and not ls.endswith('.'):
            return True
        # İki nokta ile biten satırlar başlık olabilir
        if ls.endswith(":") and len(ls) <= 120:
            return True
        return False

    sections: List[Dict[str, str]] = []
    current_title = "Giriş"
    current_lines: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if is_heading(line):
            if current_lines:
                sections.append({"title": current_title, "content": "\n".join(current_lines).strip()})
            current_title = line[:120]
            current_lines = []
        else:
            current_lines.append(raw_line)

    if current_lines:
        sections.append({"title": current_title, "content": "\n".join(current_lines).strip()})

    return sections


def parse_sector_pdfs(input_dir: str) -> Dict[str, List[Dict[str, str]]]:
    """
    input_dir altındaki PDF'leri tarar ve bölümleme çıktısı üretir.

    Returns:
        { filename: [ {title, content}, ... ] }
    """
    result: Dict[str, List[Dict[str, str]]] = {}
    if not os.path.isdir(input_dir):
        logging.error(f"[ERROR] Klasör bulunamadı: {input_dir}")
        return result
    for name in os.listdir(input_dir):
        if not name.lower().endswith('.pdf'):
            continue
        path = os.path.join(input_dir, name)
        text = parse_pdf_text(path)
        sections = split_sections(text)
        result[name] = sections
        logging.info(f"[GRI] Parsed {name}: {len(sections)} sections")
    return result
