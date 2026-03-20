import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Line, Rect, String


def _register_fonts() -> Tuple[str, str]:
    regular = "Helvetica"
    bold = "Helvetica-Bold"
    arial = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arial.ttf")
    arial_bold = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arialbd.ttf")
    try:
        if os.path.exists(arial) and os.path.exists(arial_bold):
            pdfmetrics.registerFont(TTFont("Arial", arial))
            pdfmetrics.registerFont(TTFont("Arial-Bold", arial_bold))
            regular = "Arial"
            bold = "Arial-Bold"
    except Exception:
        pass
    return regular, bold


def _load_json(path: str) -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _find_suspicious_tr_values(tr: Dict[str, str]) -> List[Tuple[str, str]]:
    suspicious = []
    patterns = [
        re.compile(r"\b(Title|Desc|Supporting)\b", re.IGNORECASE),
        re.compile(r"^[A-Za-z0-9 _:.\\-]+$"),
    ]
    for k, v in tr.items():
        if not isinstance(v, str):
            continue
        vv = v.strip()
        if not vv:
            continue
        if any(p.search(vv) for p in patterns):
            if any(ch in vv for ch in "çğıİöşüÇĞÖŞÜ"):
                continue
            if len(vv) < 5:
                continue
            suspicious.append((k, vv))
    suspicious.sort(key=lambda x: x[0])
    return suspicious


@dataclass
class TestIssue:
    kind: str
    name: str
    detail: str


def _parse_unittest_output(path: str) -> Tuple[int, int, List[TestIssue]]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception:
        return 0, 0, []

    failures = 0
    errors = 0
    issues: List[TestIssue] = []

    m = re.search(r"FAILED \\(failures=(\\d+), errors=(\\d+)\\)", text)
    if m:
        failures = int(m.group(1))
        errors = int(m.group(2))

    for line in text.splitlines():
        if line.startswith("ERROR: "):
            errors += 1 if m is None else 0
            name = line.replace("ERROR: ", "").strip()
            issues.append(TestIssue(kind="ERROR", name=name, detail=""))
        elif line.startswith("FAIL: "):
            failures += 1 if m is None else 0
            name = line.replace("FAIL: ", "").strip()
            issues.append(TestIssue(kind="FAIL", name=name, detail=""))

    snippets: Dict[str, str] = {}
    for issue in issues[:80]:
        key = f"{issue.kind}: {issue.name}"
        idx = text.find(key)
        if idx == -1:
            continue
        chunk = text[idx : idx + 900]
        chunk = chunk.split("======================================================================", 1)[0]
        chunk = re.sub(r"\\s+", " ", chunk).strip()
        snippets[key] = chunk

    enriched: List[TestIssue] = []
    for issue in issues[:80]:
        key = f"{issue.kind}: {issue.name}"
        detail = snippets.get(key, "")
        if "Traceback" in detail:
            tb = detail.split("Traceback", 1)[1]
            tb = tb.strip()
            detail = "Traceback " + tb[:450]
        enriched.append(TestIssue(kind=issue.kind, name=issue.name, detail=detail))

    return failures, errors, enriched


def _smoke_key_pages() -> List[Tuple[str, str, int, str]]:
    try:
        import web_app
    except Exception as e:
        return [("IMPORT", "web_app", 0, str(e))]

    app = getattr(web_app, "app", None)
    if app is None:
        return [("IMPORT", "web_app.app", 0, "app not found")]

    app.config["TESTING"] = True
    results: List[Tuple[str, str, int, str]] = []
    paths = [
        ("WEB", "/dashboard"),
        ("WEB", "/users"),
        ("WEB", "/companies"),
        ("WEB", "/social"),
        ("WEB", "/supply_chain"),
        ("WEB", "/governance"),
        ("WEB", "/cdp"),
        ("WEB", "/csrd"),
        ("WEB", "/taxonomy"),
        ("WEB", "/economic"),
        ("WEB", "/prioritization"),
    ]

    with app.test_client() as c:
        try:
            with c.session_transaction() as s:
                s["user"] = "__super__"
                s["username"] = "__super__"
                s["user_id"] = 1
                s["role"] = "super_admin"
                s["company_id"] = 1
        except Exception:
            pass

        for kind, path in paths:
            try:
                r = c.get(path, follow_redirects=False)
                loc = r.headers.get("Location", "")
                results.append((kind, path, int(r.status_code), loc))
            except Exception as e:
                results.append((kind, path, 0, str(e)))

    return results


def _build_styles(font_regular: str, font_bold: str):
    styles = getSampleStyleSheet()
    base = ParagraphStyle(
        "Base",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName=font_bold,
        fontSize=13.5,
        leading=18,
        spaceBefore=8,
        spaceAfter=6,
    )
    h3 = ParagraphStyle(
        "H3",
        parent=styles["Heading3"],
        fontName=font_bold,
        fontSize=11.5,
        leading=15,
        spaceBefore=6,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "Small",
        parent=base,
        fontSize=9.2,
        leading=12,
        textColor=colors.grey,
    )
    return {"base": base, "h1": h1, "h2": h2, "h3": h3, "small": small}


def _p(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _safe_image(path: str, width_cm: float, height_cm: float) -> Optional[Image]:
    if not path or not os.path.exists(path):
        return None
    try:
        return Image(path, width=width_cm * cm, height=height_cm * cm)
    except Exception:
        return None

def _mock_ui(title: str, subtitle: str, blocks: List[str], width_cm: float = 16.2, height_cm: float = 7.8) -> Drawing:
    w = width_cm * cm
    h = height_cm * cm
    d = Drawing(w, h)

    d.add(Rect(0, 0, w, h, strokeColor=colors.HexColor("#d1d5db"), fillColor=colors.white, strokeWidth=1))
    d.add(Rect(0, h - 1.0 * cm, w, 1.0 * cm, strokeColor=None, fillColor=colors.HexColor("#111827")))
    d.add(String(0.6 * cm, h - 0.72 * cm, "Sustainage", fillColor=colors.white, fontSize=10))

    d.add(Rect(0, 0, 3.2 * cm, h - 1.0 * cm, strokeColor=None, fillColor=colors.HexColor("#f3f4f6")))
    d.add(String(0.6 * cm, h - 1.55 * cm, "Menü", fillColor=colors.HexColor("#374151"), fontSize=9))
    for i in range(6):
        y = h - (2.05 + i * 0.72) * cm
        d.add(Rect(0.4 * cm, y, 2.4 * cm, 0.46 * cm, strokeColor=None, fillColor=colors.HexColor("#e5e7eb")))

    d.add(String(3.7 * cm, h - 1.55 * cm, title, fillColor=colors.HexColor("#111827"), fontSize=11))
    d.add(String(3.7 * cm, h - 2.0 * cm, subtitle, fillColor=colors.HexColor("#6b7280"), fontSize=8.5))
    d.add(Line(3.7 * cm, h - 2.15 * cm, w - 0.6 * cm, h - 2.15 * cm, strokeColor=colors.HexColor("#e5e7eb"), strokeWidth=1))

    x0 = 3.7 * cm
    y0 = h - 2.9 * cm
    col_w = (w - x0 - 0.6 * cm) / 3.0
    for idx, b in enumerate(blocks[:3]):
        bx = x0 + idx * col_w
        d.add(Rect(bx, y0, col_w - 0.35 * cm, 1.55 * cm, strokeColor=None, fillColor=colors.HexColor("#eff6ff")))
        d.add(String(bx + 0.3 * cm, y0 + 1.05 * cm, b[:22], fillColor=colors.HexColor("#1d4ed8"), fontSize=8.5))
        d.add(Rect(bx + 0.3 * cm, y0 + 0.35 * cm, col_w - 0.95 * cm, 0.18 * cm, strokeColor=None, fillColor=colors.HexColor("#bfdbfe")))

    d.add(Rect(x0, 0.55 * cm, w - x0 - 0.6 * cm, 2.25 * cm, strokeColor=None, fillColor=colors.HexColor("#ffffff")))
    d.add(Rect(x0, 0.55 * cm, w - x0 - 0.6 * cm, 2.25 * cm, strokeColor=colors.HexColor("#e5e7eb"), fillColor=None, strokeWidth=1))
    for r in range(5):
        y = 0.55 * cm + (r + 1) * 0.36 * cm
        d.add(Line(x0, y, w - 0.6 * cm, y, strokeColor=colors.HexColor("#f3f4f6"), strokeWidth=1))
    d.add(Rect(x0, 0.55 * cm + 2.25 * cm - 0.5 * cm, w - x0 - 0.6 * cm, 0.5 * cm, strokeColor=None, fillColor=colors.HexColor("#f9fafb")))
    d.add(String(x0 + 0.3 * cm, 0.55 * cm + 2.25 * cm - 0.33 * cm, "Örnek Tablo / Liste", fillColor=colors.HexColor("#374151"), fontSize=8.2))

    return d


def generate_technical_pdf(out_path: str) -> None:
    font_regular, font_bold = _register_fonts()
    st = _build_styles(font_regular, font_bold)

    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    story = []

    story.append(Paragraph(_p("Sustainage – Teknik İnceleme Raporu"), st["h1"]))
    story.append(Paragraph(_p(f"Tarih/Saat: {ts}"), st["small"]))
    story.append(Spacer(1, 10))

    audit = _load_json(os.path.join("tools", "audit_report.json"))
    missing_tr = audit.get("missing_tr") or []
    audit_errors = audit.get("errors") or []

    failures, errors, issues = _parse_unittest_output(os.path.join("tools", "unittest_full_output.txt"))
    smoke = _smoke_key_pages()

    tr_root = _load_json(os.path.join("locales", "tr.json"))
    tr_front = _load_json(os.path.join("frontend", "src", "locales", "tr.json"))
    suspicious_root = _find_suspicious_tr_values(tr_root)
    suspicious_front = _find_suspicious_tr_values(tr_front)

    story.append(Paragraph(_p("Yönetici Özeti"), st["h2"]))
    story.append(
        Paragraph(
            _p(
                "Bu rapor, uygulamanın satışa hazır hale gelebilmesi için teknik riskleri, çalışmayan/bozulan noktaları ve kalite açıklarını düzeltme yapmadan tespit etmek amacıyla hazırlanmıştır."
            ),
            st["base"],
        )
    )
    story.append(
        Paragraph(
            _p(
                f"Birim test sonucu: {failures} başarısız (FAIL), {errors} hata (ERROR). Bu seviye, sürümün satış öncesi stabilizasyon gerektirdiğini gösterir."
            ),
            st["base"],
        )
    )
    story.append(
        Paragraph(
            _p(
                f"Çeviri kontrolü: root TR şüpheli değer {len(suspicious_root)}, frontend TR şüpheli değer {len(suspicious_front)}. Eksik TR anahtar: {len(missing_tr)}."
            ),
            st["base"],
        )
    )

    story.append(Paragraph(_p("Metodoloji"), st["h2"]))
    story.append(Paragraph(_p("1) Statik analiz: şablonlar, url_for kullanımları ve çeviri anahtarları tarandı."), st["base"]))
    story.append(Paragraph(_p("2) Otomatik denetim: tools/audit_system.py çıktısı incelendi."), st["base"]))
    story.append(Paragraph(_p("3) Test çalıştırma: tests klasörü altında unittest keşfi çalıştırıldı."), st["base"]))
    story.append(Paragraph(_p("4) Duman testi (lokal): temel sayfalara GET istekleri atılarak 500/redirect kontrolü yapıldı."), st["base"]))

    story.append(PageBreak())
    story.append(Paragraph(_p("Kritik Bulgular (Önceliklendirilmiş)"), st["h2"]))

    top_items = []
    for issue in issues[:18]:
        top_items.append([issue.kind, issue.name[:78], (issue.detail[:120] + "…") if len(issue.detail) > 120 else issue.detail])

    if top_items:
        table = Table([["Tür", "Test", "Özet"]] + top_items, colWidths=[1.2 * cm, 8.5 * cm, 6.6 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), font_bold),
                    ("FONTSIZE", (0, 0), (-1, 0), 9.5),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 1), (-1, -1), font_regular),
                    ("FONTSIZE", (0, 1), (-1, -1), 8.8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

    story.append(Paragraph(_p("Öne Çıkan Teknik Riskler"), st["h3"]))
    bullets = [
        "AI modülü import zinciri kırık: backend/modules/ai/__init__.py, olmayan ai_module_gui import ediyor.",
        "Test veritabanı şema kurulumunda tutarsızlık: bazı testlerde 'companies' tablosu yok.",
        "2FA şifreleme akışında None dönebilen durum: test_2fa_encryption TypeError ile düşüyor.",
        "E-posta servisi API uyumsuzluğu: send_email imzası testte kullanılan is_html parametresini kabul etmiyor.",
        "Çok kiracılı izolasyon testleri: birden fazla modülde isolation beklentileri sağlanmıyor.",
        "Çeviri CI: anahtar eksikleri ve metin standardizasyonu (noktalama/büyük-küçük) testleri kırıyor.",
    ]
    for b in bullets:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_p("Lokal Duman Testi Sonuçları"), st["h3"]))
    smoke_rows = [[k, p, str(code), loc] for (k, p, code, loc) in smoke]
    smoke_table = Table([["Tür", "Path", "HTTP", "Location/Detay"]] + smoke_rows, colWidths=[1.2 * cm, 4.5 * cm, 1.3 * cm, 9.3 * cm])
    smoke_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTSIZE", (0, 0), (-1, 0), 9.3),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 8.7),
            ]
        )
    )
    story.append(smoke_table)

    story.append(PageBreak())
    story.append(Paragraph(_p("Çeviri ve İçerik Tutarlılığı"), st["h2"]))
    story.append(Paragraph(_p("Root TR – Şüpheli İngilizce/placeholder değerler (örnekler)"), st["h3"]))
    for k, v in suspicious_root[:35]:
        story.append(Paragraph(_p(f"• {k}: {v}"), st["base"]))
    if len(suspicious_root) > 35:
        story.append(Paragraph(_p(f"• … (+{len(suspicious_root) - 35} ek kayıt)"), st["base"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph(_p("Frontend TR – Şüpheli İngilizce/placeholder değerler (örnekler)"), st["h3"]))
    for k, v in suspicious_front[:35]:
        story.append(Paragraph(_p(f"• {k}: {v}"), st["base"]))
    if len(suspicious_front) > 35:
        story.append(Paragraph(_p(f"• … (+{len(suspicious_front) - 35} ek kayıt)"), st["base"]))

    if missing_tr:
        story.append(Spacer(1, 8))
        story.append(Paragraph(_p("Eksik TR Anahtarlar"), st["h3"]))
        for k in missing_tr[:60]:
            story.append(Paragraph(_p(f"• {k}"), st["base"]))
        if len(missing_tr) > 60:
            story.append(Paragraph(_p(f"• … (+{len(missing_tr) - 60} ek anahtar)"), st["base"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(_p("Denetim Aracı Notu"), st["h3"]))
    story.append(
        Paragraph(
            _p(
                f"tools/audit_system.py bazı ikili dosyaları (pdf/xlsx/db) UTF-8 okumaya çalıştığı için {len(audit_errors)} adet 'READ ERROR' üretti. Bu uyarılar uygulama hatası değil; denetim aracının filtreleme eksikliği olarak ele alınmalıdır."
            ),
            st["base"],
        )
    )

    story.append(PageBreak())
    story.append(Paragraph(_p("Satışa Hazırlık İçin Önerilen Stabilizasyon Planı"), st["h2"]))
    phases = [
        ("0–2 gün", "Kırmızı bloklayıcılar: test_ai_module import, 2FA encryption None, EmailService imza uyumu, test DB şema init (companies tablosu)."),
        ("3–7 gün", "Çok kiracılı izolasyon testlerini geçirecek şekilde tenant filtreleri ve 'global tablolara' erişim standardizasyonu."),
        ("1–2 hafta", "Çeviri CI standardizasyonu (TR/EN/DE), UI metinlerinin tamamen yerelleştirilmesi, DataTables kapsamının sayfa bazlı kontrolü."),
        ("2–4 hafta", "E2E smoke test paketi, staging ortamı gözlemi, raporlama çıktılarının (PDF/Excel/Word) regresyon testleri."),
    ]
    plan_table = Table([["Süre", "Hedef"]] + [[a, b] for a, b in phases], colWidths=[2.4 * cm, 14.0 * cm])
    plan_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.4),
            ]
        )
    )
    story.append(plan_table)

    doc.build(story)


def generate_sales_pdf(out_path: str) -> None:
    font_regular, font_bold = _register_fonts()
    st = _build_styles(font_regular, font_bold)

    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    story = []

    story.append(Paragraph(_p("Sustainage – Danışmanlık Firmalarına Yönelik Tanıtım Raporu"), st["h1"]))
    story.append(Paragraph(_p(f"Tarih/Saat: {ts}"), st["small"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(_p("Neden Sustainage?"), st["h2"]))
    story.append(
        Paragraph(
            _p(
                "Sürdürülebilirlik raporlaması (CSRD/ESRS, GRI, CDP, TCFD, EU Taxonomy, ISSB vb.) danışmanlık projelerinde en büyük maliyet kalemi; veri toplama, doğrulama ve rapor üretimindeki zaman kaybıdır. Sustainage, bu süreci modüler bir yapı ile standardize eder, hızlandırır ve denetlenebilir hale getirir."
            ),
            st["base"],
        )
    )

    story.append(Paragraph(_p("Danışmanlık Firmalarına Faydaları"), st["h2"]))
    benefits = [
        "Projeyi teslim süresini kısaltır: veri envanteri → KPI’lar → rapor taslağı akışını tek platformda toplar.",
        "Denetlenebilirlik sağlar: audit trail, veri kaynağı ve kullanıcı izleri ile müşteriye güven verir.",
        "Tekrarlanabilir metodoloji sunar: müşteri başına süreç standartlaşır; ekip eğitimi kolaylaşır.",
        "Çoklu çerçeve desteği ile yeniden kullanım sağlar: aynı veri seti farklı raporlara yansıtılabilir.",
        "Ek gelir kanalı oluşturur: lisans + danışmanlık paketi + entegrasyon (ERP/otomasyon) hizmetleri.",
    ]
    for b in benefits:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(PageBreak())
    story.append(Paragraph(_p("Modüller ve Kısa Tanımlar"), st["h2"]))

    module_rows = [
        ("Veri Girişi & Envanter", "Karbon, enerji, su, atık, biyoçeşitlilik, sosyal ve yönetişim verilerinin standart formlarla toplanması."),
        ("GRI", "GRI standartları, içerik indeksi, KPI ve rapor çıktıları ile hızlı GRI uyumu."),
        ("CSRD / ESRS", "Uyum kontrolü, çift önemlilik (impact/financial) ve ESRS odaklı rapor taslağı üretimi."),
        ("EU Taxonomy", "Faaliyet–c iro/capex/opex ayrıştırması ve taksonomi raporlaması."),
        ("CDP", "İklim, su ve orman modülleri için soru setleri, skorlama mantığı ve rapor çıktıları."),
        ("TCFD / ISSB", "İklim riskleri, senaryo analizi ve yönetişim/strateji metinlerinin yapılandırılması."),
        ("CBAM / SKDM", "Ürün bazlı emisyon hesaplama, izleme ve raporlama."),
        ("Tedarik Zinciri", "Tedarikçi değerlendirme, risk görünümü ve sürdürülebilir tedarik zinciri yönetimi."),
        ("Paydaş & Anketler", "Paydaş haritalama, anket tasarlama/uygulama ve sonuç analizi."),
        ("Hedefler & Yol Haritası", "SMART hedefler, aksiyon planları ve raporlama yolculuğu yönetimi."),
        ("Raporlama Motoru", "PDF/Excel/Word çıktıları, marka kimliği, yönetici özeti ve birleşik rapor üretimi."),
        ("Entegrasyon & Otomasyon", "ERP entegrasyonu, veri içe aktarma şablonları ve otomatik raporlama görevleri."),
        ("Güvenlik & Yetkilendirme", "Rol tabanlı erişim, denetim kayıtları, çoklu şirket yönetimi ve yönetim paneli."),
    ]
    table = Table([["Modül", "Ne İşe Yarar?"]] + [[a, b] for a, b in module_rows], colWidths=[5.0 * cm, 11.4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.2),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(table)

    story.append(PageBreak())
    story.append(Paragraph(_p("Raporlama Ne Kadar Hızlanır?"), st["h2"]))
    story.append(
        Paragraph(
            _p(
                "Tipik bir danışmanlık projesinde zamanın önemli kısmı veri toplama ve doğrulamaya gider. Sustainage ile proje planı çoğu senaryoda şu şekilde kısalır:"
            ),
            st["base"],
        )
    )
    timeline = [
        ("1–2 gün", "Kurulum, şirket tanımı, kullanıcı/rol yapılandırması, temel şablonların seçimi."),
        ("1–2 hafta", "Veri envanteri ve boşluk analizi: hangi veriler var/yok, kaynaklar ve sorumlular."),
        ("2–4 hafta", "Veri girişi/ithalat + doğrulama + ilk taslak rapor çıktısı."),
        ("4–6 hafta", "Gelişmiş entegrasyon (ERP) ve periyodik izleme: otomatik veri akışları ile sürekli raporlama."),
    ]
    t = Table([["Süre", "Çıktı"]] + timeline, colWidths=[2.8 * cm, 13.6 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.4),
            ]
        )
    )
    story.append(t)

    story.append(Spacer(1, 10))
    story.append(Paragraph(_p("Entegrasyon ve Otomasyon"), st["h2"]))
    story.append(
        Paragraph(
            _p(
                "Manuel girişler hızlı başlamak için idealdir; ancak sürdürülebilirlik verisinin kalitesi ve sürekliliği için ERP/CSV/Excel entegrasyonları ile otomasyon kritik rol oynar. Sustainage, veri içe aktarma şablonları ve entegrasyon modülleriyle danışmanlık ekiplerinin müşterilerinde kalıcı bir sistem kurmasına yardımcı olur."
            ),
            st["base"],
        )
    )

    story.append(Paragraph(_p("Neden Danışmanlık Firmaları Denemeli?"), st["h2"]))
    cta = [
        "30 dakikalık demo ile mevcut müşteri projenize göre senaryo üzerinden ilerleyelim.",
        "1 haftalık pilot: tek müşteriyle veri envanteri + ilk rapor taslağı üretimi.",
        "“Danışmanlık paketi” modeli: lisans + danışmanlık + entegrasyon ile tekrarlanabilir gelir.",
        "Fiyat/performans: modüler paketleme ile müşterinin ihtiyacına göre ölçeklenebilir yatırım.",
    ]
    for b in cta:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_p("Konumlandırma Notu"), st["h3"]))
    story.append(
        Paragraph(
            _p(
                "Sustainage, Türkiye’de yerelleştirme (TR dil desteği, yerel ihtiyaçlar) ile global raporlama çerçevelerini aynı platformda birleştirmeyi hedefler. Piyasada farklı parçaları çözen araçlar bulunabilse de, bu kapsamın tek platformda uçtan uca uygulanması danışmanlık firmaları için belirgin bir rekabet avantajı sağlar."
            ),
            st["base"],
        )
    )

    doc.build(story)

def generate_sales_detailed_pdf(out_path: str) -> None:
    font_regular, font_bold = _register_fonts()
    st = _build_styles(font_regular, font_bold)

    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=2.0 * cm, rightMargin=2.0 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    story = []

    logo = _safe_image(os.path.join("docs", "sustainage_logo.png"), width_cm=6.0, height_cm=2.0)
    if logo:
        story.append(logo)
        story.append(Spacer(1, 10))

    story.append(Paragraph(_p("Sustainage"), st["h1"]))
    story.append(Paragraph(_p("Danışmanlık Firmalarına Yönelik Detaylı Satış Tanıtımı"), st["h2"]))
    story.append(Paragraph(_p("Sürdürülebilirlik raporlamasını hızlandıran, denetlenebilir ve modüler platform"), st["base"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(_p(f"Tarih/Saat: {ts}"), st["small"]))
    story.append(PageBreak())

    story.append(Paragraph(_p("Bu Doküman Ne Sağlar?"), st["h2"]))
    intro = [
        "Danışmanlık projelerinde tekrar eden iş yükünü (veri toplama, doğrulama, rapor taslağı) sistematik hale getirir.",
        "Müşteri başına metodolojiyi standardize eder; ekip ölçeğini büyütmeyi kolaylaştırır.",
        "Çoklu raporlama çerçevelerini tek platformda birleştirerek yeniden kullanım yaratır.",
        "Pilot deneme planı ve paketleme önerisi ile hızlı ticari aksiyon sağlar.",
    ]
    for b in intro:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_p("Hedef Kitle"), st["h3"]))
    story.append(Paragraph(_p("Sürdürülebilirlik raporlaması hazırlayan danışmanlık firmaları, bağımsız denetim hazırlığı yapan ekipler, ESG veri yönetimi hizmeti veren teknoloji/danışmanlık hibrit ekipleri."), st["base"]))

    story.append(Paragraph(_p("Danışmanlık Firmaları İçin Temel Problem"), st["h2"]))
    pains = [
        "Veri parçalı: ERP, Excel, e-posta, farklı departmanlar.",
        "Süre baskısı: CSRD/ESRS ve müşteri talepleri ile kısa teslim süreleri.",
        "Kalite riski: veri doğrulama, kaynak belirsizliği, revizyon döngüleri.",
        "Raporlama çerçevesi çeşitliliği: GRI, CDP, EU Taxonomy, TCFD/ISSB gibi farklı formatlar.",
    ]
    for b in pains:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(_p("Sustainage Çözümü (Kısa)"), st["h2"]))
    sol = [
        "Veri envanteri ve formlar ile standardize veri toplama",
        "Çoklu çerçeve haritalama ve tek veri setinden çoklu rapor çıktısı",
        "Denetim izi ve kullanıcı/aksiyon kayıtları ile şeffaflık",
        "Hedef/aksiyon takibi ve yol haritası ile proje yönetimi",
        "İthalat şablonları + ERP entegrasyon yaklaşımı ile otomasyon",
    ]
    for b in sol:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(PageBreak())
    story.append(Paragraph(_p("Danışmanlık Projesi Akışı (Örnek)"), st["h2"]))
    flow = [
        ("1) Onboarding", "Şirket tanımı, organizasyon, rapor kapsamı, rol/izinler."),
        ("2) Veri Envanteri", "Mevcut veri kaynaklarını çıkarma, eksik veri listesi."),
        ("3) Toplama / İthalat", "Formlar, Excel şablonları, API/ERP entegrasyonu."),
        ("4) Doğrulama", "Kontroller, tutarlılık, audit trail ile izlenebilirlik."),
        ("5) Analiz", "Materiality, risk/senaryo, KPI’ların hazırlanması."),
        ("6) Rapor Üretimi", "Çerçeve bazlı taslaklar ve birleşik rapor çıktısı."),
        ("7) Süreklilik", "Dönemsel güncelleme, otomatik görevler, dashboard."),
    ]
    t = Table([["Adım", "Amaç"]] + [[a, b] for a, b in flow], colWidths=[3.6 * cm, 12.8 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph(_p("Bu akış sayesinde ekip kapasitesi artar: aynı danışman sayısı ile daha fazla müşteri projesi yürütülebilir."), st["base"]))

    story.append(PageBreak())
    story.append(Paragraph(_p("Modül Bazlı Detaylar (Danışmanlık Perspektifi)"), st["h2"]))
    story.append(Paragraph(_p("Aşağıdaki her modül, danışmanlık projelerinde somut çıktılar üreterek teslim süresini azaltmaya ve kaliteyi artırmaya odaklanır."), st["base"]))

    modules = [
        ("Dashboard & Performans", "Yönetime hızlı resim", "KPI panelleri, trendler, risk alanları.", ["KPI", "Trend", "Uyarılar"]),
        ("Veri Girişi & Envanter", "Standart veri toplama", "Modül bazlı formlar ve veri kalitesi kontrolleri.", ["Formlar", "Şablon", "Kaynak"]),
        ("Çevresel (Karbon/Enerji/Su/Atık)", "Hesaplama & izleme", "Scope mantığı, tüketimler, emisyonlar, raporlanabilir çıktılar.", ["Scope", "Tüketim", "Faktör"]),
        ("Sosyal Etki", "İnsan & işgücü metrikleri", "Eğitim, İSG, çeşitlilik, memnuniyet metrikleri ve trend.", ["İSG", "Eğitim", "Çeşitlilik"]),
        ("Kurumsal Yönetişim", "Politika & uyum", "Etik, uyum, yönetim yapısı, denetim ve kanıt akışı.", ["Politikalar", "Uyum", "Kanıt"]),
        ("Paydaş & Anketler", "Paydaş görüşü", "Paydaş haritalama, anket akışı, sonuç analizi.", ["Paydaş", "Anket", "Analiz"]),
        ("Önceliklendirme (Materiality)", "Çift önemlilik", "Konu listesi, skorlar, matriks, gerekçeler ve çıktı.", ["Konu", "Skor", "Matriks"]),
        ("CSRD / ESRS", "Uyum yol haritası", "Gereklilik takibi, boşluk analizi, rapor taslağı üretimi.", ["ESRS", "Boşluk", "Taslak"]),
        ("GRI", "Hızlı GRI uyumu", "Standart eşleme, içerik indeksi, KPI seti ve raporlama.", ["Standart", "İndeks", "KPI"]),
        ("CDP", "Soru setleri & skor", "İklim/su/orman anketleri, skor mantığı, çıktı raporları.", ["Anket", "Skor", "Rapor"]),
        ("EU Taxonomy", "Ciro/CAPEX/OPEX", "Faaliyet sınıflaması, uygunluk oranları ve raporlama.", ["Ciro", "CAPEX", "OPEX"]),
        ("CBAM / SKDM", "Ürün bazlı emisyon", "Malzeme/enerji girdileri, hesaplama ve rapor paketi.", ["Ürün", "Emisyon", "Beyan"]),
        ("Raporlama Motoru", "Tek tık çıktı", "Birleşik rapor, bölüm yönetimi, format dışa aktarma.", ["PDF", "Word", "Excel"]),
        ("Entegrasyon (ERP/İthalat)", "Otomasyon", "Excel/CSV şablonları, API yaklaşımı, ERP bağlantısı.", ["İthalat", "API", "ERP"]),
        ("Denetim & Güvenlik", "İzlenebilirlik", "Audit log, rol tabanlı erişim, şirket izolasyonu.", ["Audit", "RBAC", "Tenant"]),
    ]

    for name, promise, desc, blocks in modules:
        story.append(Paragraph(_p(name), st["h3"]))
        story.append(Paragraph(_p(f"Değer vaadi: {promise}"), st["base"]))
        story.append(Paragraph(_p(desc), st["base"]))
        story.append(Spacer(1, 4))
        story.append(KeepTogether([_mock_ui(name, promise, blocks), Spacer(1, 8)]))

        story.append(Paragraph(_p("Danışmanlık katkısı"), st["small"]))
        contrib = [
            "Müşteri verisini standardize eder; ekip içi teslim kalitesini yükseltir.",
            "Tekrarlanabilir çıktı şablonları ile yeni müşteri projelerinde yeniden kullanım sağlar.",
            "Denetlenebilirlik ve izlenebilirlik ile müşteri tarafında güveni artırır.",
        ]
        for c in contrib:
            story.append(Paragraph(_p(f"• {c}"), st["base"]))
        story.append(Spacer(1, 10))

    story.append(PageBreak())
    story.append(Paragraph(_p("Paketleme Önerisi (Danışmanlık Satışı İçin)"), st["h2"]))
    packs = [
        ("Starter", "1 müşteri – temel modüller + rapor çıktısı", "Hızlı başlangıç, pilot, metodoloji standardizasyonu."),
        ("Professional", "Çoklu modül + çoklu kullanıcı + export", "Danışmanlık ekibi ölçeği ve teslim süresi optimizasyonu."),
        ("Enterprise", "Entegrasyon + otomasyon + özel şablonlar", "ERP bağlantıları, sürekli raporlama, kurumsal yayılım."),
    ]
    pt = Table([["Paket", "Kapsam", "Kime Uygun?"]] + [[a, b, c] for a, b, c in packs], colWidths=[2.6 * cm, 6.4 * cm, 7.4 * cm])
    pt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ]
        )
    )
    story.append(pt)
    story.append(Spacer(1, 10))

    story.append(Paragraph(_p("Pilot Deneme Planı (7 Gün)"), st["h2"]))
    pilot = [
        ("Gün 1", "Kurulum + şirket profili + rol/izinler"),
        ("Gün 2", "Veri envanteri + eksik veri listesi"),
        ("Gün 3–4", "Formlar/ithalat ile veri toplama"),
        ("Gün 5", "Doğrulama + audit trail + revizyon turu"),
        ("Gün 6", "Modül bazlı taslak rapor çıktıları"),
        ("Gün 7", "Birleşik rapor + yol haritası + sonraki adımlar"),
    ]
    pilot_t = Table([["Süre", "Çıktı"]] + pilot, colWidths=[2.2 * cm, 14.2 * cm])
    pilot_t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 1), (-1, -1), 9.4),
            ]
        )
    )
    story.append(pilot_t)

    story.append(Spacer(1, 12))
    story.append(Paragraph(_p("Hemen Deneyin"), st["h2"]))
    cta = [
        "30 dakikalık canlı demo: kendi müşteri senaryonuza göre modül akışı.",
        "7 günlük pilot: tek müşteri ile ilk taslak rapor çıktısı üretimi.",
        "Danışmanlık firmaları için paket: lisans + danışmanlık + entegrasyon hizmeti.",
    ]
    for b in cta:
        story.append(Paragraph(_p(f"• {b}"), st["base"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph(_p("Not: Bu dokümandaki ekran önizlemeleri, ürün arayüzünü temsil eden görsel şemalardır; pilot/demo sırasında canlı ekranlar üzerinden yürütülür."), st["small"]))
    doc.build(story)


def main() -> int:
    base_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(base_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tech_path = os.path.join(base_dir, f"teknik_inceleme_{stamp}.pdf")
    sales_path = os.path.join(base_dir, f"tanitim_raporu_{stamp}.pdf")
    sales_detailed_path = os.path.join(base_dir, f"tanitim_raporu_detayli_{stamp}.pdf")

    generate_technical_pdf(tech_path)
    generate_sales_pdf(sales_path)
    generate_sales_detailed_pdf(sales_detailed_path)
    print(tech_path)
    print(sales_path)
    print(sales_detailed_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
