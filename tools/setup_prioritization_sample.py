import logging
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from modules.prioritization.prioritization_manager import \
        PrioritizationManager
except Exception:
    PrioritizationManager = None

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sdg_desktop.sqlite")

def ensure_tables() -> None:
    if PrioritizationManager:
        try:
            PrioritizationManager(db_path=DB_PATH)
            # constructor already creates tables
            return True
        except Exception as e:
            logging.error("[HATA] Tablolar oluşturulamadı:", e)
            return False
    else:
        # Fallback: minimal table create if manager import fails
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                category TEXT,
                sdg_mapping TEXT,
                FOREIGN KEY(template_id) REFERENCES survey_templates(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
        conn.close()
        return True

def upsert_sample_survey() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # 1) Template
    cur.execute("SELECT id FROM survey_templates WHERE name = ? LIMIT 1", (
        "Sürdürülebilirlik Önceliklendirme 2024",
    ))
    row = cur.fetchone()
    if row:
        template_id = row[0]
    else:
        cur.execute(
            """
            INSERT INTO survey_templates (name, description, category, created_at, is_active)
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                "Sürdürülebilirlik Önceliklendirme 2024",
                "Paydaş önem ve iş etkisi değerlendirmesi",
                "Genel",
                datetime.now().isoformat(timespec='seconds'),
            ),
        )
        template_id = cur.lastrowid

    # 2) Ensure a stakeholder survey to satisfy NOT NULL survey_id in survey_questions
    cur.execute(
        "SELECT id FROM stakeholder_surveys WHERE company_id=? AND survey_name=? LIMIT 1",
        (1, "Sürdürülebilirlik Önceliklendirme 2024"),
    )
    sr = cur.fetchone()
    if sr:
        survey_id = sr[0]
    else:
        cur.execute(
            """
            INSERT INTO stakeholder_surveys (company_id, survey_name, stakeholder_category, survey_data)
            VALUES (?, ?, ?, ?)
            """,
            (1, "Sürdürülebilirlik Önceliklendirme 2024", "Genel", None),
        )
        survey_id = cur.lastrowid

    # 3) Questions (insert if not exists)
    questions = [
        (
            template_id,
            "İklim değişikliğinin önemi",
            "scale",
            1.0,
            "Environmental",
            "SDG 13",
        ),
        (
            template_id,
            "Çevresel mevzuat uyumu",
            "scale",
            0.8,
            "Governance",
            "SDG 16",
        ),
    ]

    for tpl_id, text, qtype, weight, category, sdg in questions:
        cur.execute(
            "SELECT 1 FROM survey_questions WHERE survey_id=? AND question_text=?",
            (survey_id, text),
        )
        if not cur.fetchone():
            cur.execute(
            """
            INSERT INTO survey_questions (
                survey_id, template_id, question_text,
                question_type, weight, category, sdg_mapping
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (survey_id, tpl_id, text, qtype, weight, category, sdg),
            )

    conn.commit()
    conn.close()
    return True

def show_counts() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for t in ["survey_templates", "survey_questions"]:
        try:
            if t == "survey_templates":
                cur.execute("SELECT COUNT(*) FROM survey_templates")
            elif t == "survey_questions":
                cur.execute("SELECT COUNT(*) FROM survey_questions")
            else:
                logging.info(t, "ERR", "geçersiz tablo")
                continue
            logging.info(t, cur.fetchone()[0])
        except Exception as e:
            logging.info(t, "ERR", e)
    conn.close()

if __name__ == "__main__":
    ok = ensure_tables()
    if ok:
        upsert_sample_survey()
        show_counts()
        logging.info("[OK] Önceliklendirme örnek anket ve sorular eklendi.")
    else:
        logging.error("[HATA] Tablolar hazır değil, işlem atlandı.")
