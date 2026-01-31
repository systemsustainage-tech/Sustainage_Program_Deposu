import logging
import datetime
import re
import shutil
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ROOT = Path(__file__).resolve().parents[1]
CONSOLIDATED_NAME = "TUM_ACIKLAMA_MD_KRONOLOJIK.md"
CONSOLIDATED_PATH = ROOT / CONSOLIDATED_NAME
BACKUP_DIR = ROOT / "archive" / f"md_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"


TURKISH_MONTHS = {
    "Ocak": 1, "Şubat": 2, "Subat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Mayis": 5,
    "Haziran": 6, "Temmuz": 7, "Ağustos": 8, "Agustos": 8, "Eylül": 9, "Eylul": 9,
    "Ekim": 10, "Kasım": 11, "Kasim": 11, "Aralık": 12, "Aralik": 12
}


DATE_PATTERNS = [
    # 23 Ekim 2025, 20:15
    re.compile(r"(?P<day>\d{1,2})\s+(?P<month>Ocak|Şubat|Subat|Mart|Nisan|Mayıs|Mayis|Haziran|Temmuz|Ağustos|Agustos|Eylül|Eylul|Ekim|Kasım|Kasim|Aralık|Aralik)\s+(?P<year>\d{4})(?:\s*,\s*(?P<hour>\d{1,2}):(?P<minute>\d{2}))?", re.IGNORECASE),
    # 2025-10-23 20:15
    re.compile(r"(?P<year>\d{4})[-/.](?P<month>\d{1,2})[-/.](?P<day>\d{1,2})(?:\s+(?P<hour>\d{1,2}):(?P<minute>\d{2}))?"),
    # 23/10/2025
    re.compile(r"(?P<day>\d{1,2})[\-/.](?P<month>\d{1,2})[\-/.](?P<year>\d{4})"),
]


def parse_date_from_text(text: str, fallback: datetime.datetime) -> datetime.datetime:
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        gd = m.groupdict()
        try:
            year = int(gd.get("year"))
            month_raw = gd.get("month")
            day = int(gd.get("day"))
            hour = int(gd.get("hour")) if gd.get("hour") else 0
            minute = int(gd.get("minute")) if gd.get("minute") else 0

            if isinstance(month_raw, str) and not month_raw.isdigit():
                month = TURKISH_MONTHS.get(month_raw, 1)
            else:
                month = int(month_raw)

            return datetime.datetime(year, month, day, hour, minute)
        except Exception:
            continue
    return fallback


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):  # tolerant
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    # final fallback binary decode
    with open(path, "rb") as f:
        data = f.read()
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return data.decode("latin-1", errors="ignore")


def collect_markdown_files(include_subdirs: bool = True):
    files = []
    for p in ROOT.rglob("*.md") if include_subdirs else ROOT.glob("*.md"):
        if p.name == CONSOLIDATED_NAME:
            continue
        files.append(p)
    return files


def build_consolidated(md_files):
    entries = []
    for fp in md_files:
        try:
            text = read_text(fp)
        except Exception:
            text = "(İçerik okunamadı)"
        mtime = datetime.datetime.fromtimestamp(fp.stat().st_mtime)
        dt = parse_date_from_text(text, mtime)
        entries.append({
            "path": fp,
            "rel": str(fp.relative_to(ROOT)),
            "date": dt,
            "content": text,
        })

    entries.sort(key=lambda e: e["date"])  # kronolojik

    lines = []
    lines.append("# 📚 Tüm Açıklama Raporları — Kronolojik Konsolidasyon")
    lines.append("")
    lines.append(f"Bu dosya otomatik oluşturuldu: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for e in entries:
        date_str = e["date"].strftime("%d %B %Y %H:%M")
        lines.append(f"## {date_str} — {e['rel']}")
        lines.append("")
        # İçeriği olduğu gibi koru; blok içine alarak güvenli gösterim
        lines.append("```")
        lines.append(e["content"].rstrip())
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    CONSOLIDATED_PATH.write_text("\n".join(lines), encoding="utf-8")


def backup_and_remove(md_files):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for fp in md_files:
        target = BACKUP_DIR / fp.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(fp), str(target))


def main():
    include_subdirs = True
    if "--root-only" in sys.argv:
        include_subdirs = False

    md_files = collect_markdown_files(include_subdirs=include_subdirs)
    if not md_files:
        logging.info("No markdown files found to consolidate.")
        return 0

    logging.info(f"Found {len(md_files)} markdown files. Building consolidated...")
    build_consolidated(md_files)
    logging.info(f"Consolidated written to: {CONSOLIDATED_PATH}")

    # Güvenli: önce yedekle, sonra ana klasörden kaldırılmış olur
    backup_and_remove(md_files)
    logging.info(f"Backed up originals to: {BACKUP_DIR}")
    logging.info("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
