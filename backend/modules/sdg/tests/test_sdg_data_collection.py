import os
import sys
import tempfile

import pandas as pd

# Add parent directory to path to find sdg_data_collection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdg_data_collection import SDGDataCollection


def _make_temp_db_path():
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    path = tmp.name
    tmp.close()
    return path


def _sample_questions_df():
    return pd.DataFrame([
        {
            "SDG No": 9,
            "SDG Başlık": "Sanayi, Yenilik ve Altyapı",
            "Alt Hedef Kodu": "9.1",
            "Alt Hedef Tanımı (TR)": "Altyapı",
            "Gösterge Kodu": "9.1.1",
            "Gösterge Tanımı (TR)": "Test Gösterge",
            "Soru 1": "S1?",
            "Soru 2": "S2?",
            "Soru 3": "S3?",
        }
    ])


def test_get_questions_for_indicator_returns_three_questions():
    db_path = _make_temp_db_path()
    try:
        dc = SDGDataCollection(db_path=db_path)
        dc.questions_df = _sample_questions_df()

        questions = dc.get_questions_for_indicator("9.1.1")
        assert isinstance(questions, list)
        assert len(questions) == 3
        nums = {q["question_number"] for q in questions}
        assert nums == {1, 2, 3}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_save_answer_and_progress_updates():
    db_path = _make_temp_db_path()
    try:
        dc = SDGDataCollection(db_path=db_path)
        dc.questions_df = _sample_questions_df()

        ok1 = dc.save_answer(
            company_id=1,
            indicator_code="9.1.1",
            question_number=1,
            answer_text="Metin",
        )
        ok2 = dc.save_answer(
            company_id=1,
            indicator_code="9.1.1",
            question_number=2,
            answer_value=12.5,
        )
        ok3 = dc.save_answer(
            company_id=1,
            indicator_code="9.1.1",
            question_number=3,
            answer_boolean=True,
        )

        assert ok1 and ok2 and ok3

        progress = dc.get_company_progress(1)
        assert progress["total_questions"] >= 3
        assert progress["answered_questions"] >= 3
        assert progress["completion_percentage"] >= 100.0
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_get_indicator_responses_returns_saved_rows():
    db_path = _make_temp_db_path()
    try:
        dc = SDGDataCollection(db_path=db_path)
        dc.questions_df = _sample_questions_df()

        dc.save_answer(1, "9.1.1", 1, answer_text="A")
        dc.save_answer(1, "9.1.1", 2, answer_value=3.14)
        dc.save_answer(1, "9.1.1", 3, answer_boolean=False)

        rows = dc.get_indicator_responses(1, "9.1.1")
        assert isinstance(rows, list)
        assert len(rows) == 3
        qnums = sorted(r["question_number"] for r in rows)
        assert qnums == [1, 2, 3]
        assert any(r["answer_text"] == "A" for r in rows)
        assert any(r["answer_value"] == 3.14 for r in rows)
        assert any(r["answer_boolean"] is False for r in rows)
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)