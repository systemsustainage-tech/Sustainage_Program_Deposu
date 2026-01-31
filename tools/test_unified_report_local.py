
import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add path to backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.modules.reporting.unified_report_docx import UnifiedReportDocxGenerator
from backend.modules.stakeholder.stakeholder_engagement import StakeholderEngagement
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO)

def test_generate_report():
    print(f"Testing unified report generation using DB: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    metrics = {}
    
    # Simulate survey data retrieval (copied from web_app.py)
    try:
        print("Querying online_surveys...")
        survey_row = conn.execute(
            """
            SELECT id, survey_title, survey_description, response_count, created_at
            FROM online_surveys
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT 1
            """
        ).fetchone()

        if survey_row:
            print(f"Found survey: {survey_row['survey_title']} (ID: {survey_row['id']})")
            survey_id = survey_row['id']
            total_responses = survey_row['response_count'] or 0
            questions_summary = []
            
            # Yanitlari topic_code bazinda grupla ve ortalamalari al
            rows = conn.execute(
               """
               SELECT topic_code, AVG(importance_score) as avg_imp
               FROM survey_responses
               WHERE survey_id = ?
               GROUP BY topic_code
               """,
               (survey_id,),
            ).fetchall()
            
            print(f"Found {len(rows)} topic groups in responses.")
            
            totals = {r['topic_code']: (r['avg_imp'] or 0) for r in rows}
            
            questions_map = {q["id"]: q for q in StakeholderEngagement.SDG17_QUESTION_SET}
            
            for code, avg_score in totals.items():
                q_def = questions_map.get(code)
                if q_def:
                    questions_summary.append({
                        "id": code,
                        "goal": q_def.get("goal"),
                        "title": q_def.get("title"),
                        "question": q_def.get("question"),
                        "avg_score": round(avg_score, 2)
                    })

            if questions_summary:
                questions_summary.sort(key=lambda x: x.get("goal") or 0)
                ordered = sorted(
                    questions_summary,
                    key=lambda x: (x.get("avg_score") if x.get("avg_score") is not None else 0),
                    reverse=True,
                )
                strongest = ordered[:3]
                weakest = list(reversed(ordered[-3:])) if ordered else []
                metrics["stakeholder_survey"] = {
                    "survey_title": survey_row["survey_title"],
                    "survey_description": survey_row["survey_description"],
                    "created_at": survey_row["created_at"],
                    "response_count": total_responses,
                    "questions": questions_summary,
                    "top3": strongest,
                    "bottom3": weakest,
                }
                
                # Insight text generation
                insight_lines = []
                if strongest:
                    parts = []
                    for item in strongest:
                        g = item.get("goal")
                        t = item.get("title") or ""
                        s = item.get("avg_score")
                        if g is not None and s is not None:
                            parts.append(f"SDG {g} - {t} (ortalama {s})")
                    if parts:
                        insight_lines.append("En guclu hedefler: " + ", ".join(parts))
                if weakest:
                    parts = []
                    for item in weakest:
                        g = item.get("goal")
                        t = item.get("title") or ""
                        s = item.get("avg_score")
                        if g is not None and s is not None:
                            parts.append(f"SDG {g} - {t} (ortalama {s})")
                    if parts:
                        insight_lines.append("Gelisim gerektiren hedefler: " + ", ".join(parts))
                if insight_lines:
                    metrics["stakeholder_survey"]["insights_text"] = " | ".join(insight_lines)
        else:
            print("No active survey found.")
            
    except Exception as e:
        logging.error(f"Survey metrics error: {e}")
    finally:
        conn.close()

    # Generate report
    output_path = os.path.join(os.path.dirname(__file__), 'test_unified_report.docx')
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except:
            pass
            
    print(f"Generating report with metrics keys: {list(metrics.keys())}")
    try:
        # Pass backend dir (one level up from tools)
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        generator = UnifiedReportDocxGenerator(backend_dir)
        result_path = generator.generate(
            company_id=1,
            reporting_period='2025',
            report_name='Test Report',
            selected_modules=['stakeholder'],
            module_reports=[],
            ai_comment='Test AI Comment',
            description='Test Description',
            metrics=metrics
        )
        print(f"Report generated at: {result_path}")
    except Exception as e:
        print(f"Report generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generate_report()
