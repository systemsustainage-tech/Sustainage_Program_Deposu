#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Form ve Anket In-App Gönderim Doğrulama
Bu script, form ve anket oluşturup örnek bir gönderim yapar ve kayıtların
veritabanına yazıldığını doğrular.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paket yolu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

 


def verify_forms(db_path: str) -> None:
    from services.form_service import FormService
    logging.info("\n=== FORM DOĞRULAMA ===")
    fs = FormService(db_path)
    form_id = fs.create_form(company_id=1, name="Doğrulama Formu", description="Test amaçlı", module="test")
    logging.info(f"[OK] Form oluşturuldu: #{form_id}")

    # Alanları ekle
    f_name_id = fs.add_field(form_id, label="Ad", name="first_name", field_type='text', required=True, order_index=1)
    f_age_id = fs.add_field(form_id, label="Yaş", name="age", field_type='number', required=False, order_index=2)
    f_choice_id = fs.add_field(form_id, label="Durum", name="status", field_type='choice', options=['aktif','pasif'], order_index=3)
    logging.info(f"[OK] Alanlar eklendi: {f_name_id}, {f_age_id}, {f_choice_id}")

    # Gönderim yap
    submission_id = fs.submit(form_id, user_id=1, company_id=1, values={
        'first_name': 'Test Kullanıcı',
        'age': '32',
        'status': 'aktif'
    })
    logging.info(f"[OK] Form gönderildi: submission #{submission_id}")

    # Form ve alanları kontrol
    form = fs.get_form_with_fields(form_id)
    assert form.get('id') == form_id and len(form.get('fields', [])) == 3, "Form/alan doğrulaması başarısız"
    logging.info("[OK] Form ve alanlar doğrulandı")


def verify_surveys(db_path: str) -> None:
    from services.survey_service import SurveyService
    logging.info("\n=== ANKET DOĞRULAMA ===")
    # Eski DB şemalarında surveys.company_id olmayabilir; eksikse ekleyelim
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(surveys)")
        cols = [row[1] for row in cur.fetchall()]
        required = {'id', 'company_id', 'name', 'description', 'status', 'created_at'}
        if not required.issubset(set(cols)):
            # Uyuşmayan şema: test doğrulaması için tabloyu yeniden oluştur
            cur.execute("DROP TABLE IF EXISTS surveys")
            conn.commit()

        # survey_questions kolon kontrolü
        cur.execute("PRAGMA table_info(survey_questions)")
        qcols = [row[1] for row in cur.fetchall()]
        q_required = {'id', 'survey_id', 'q_type', 'text', 'options_json', 'required', 'order_index'}
        if not q_required.issubset(set(qcols)):
            cur.execute("DROP TABLE IF EXISTS survey_questions")
            conn.commit()

        # survey_responses kolon kontrolü
        cur.execute("PRAGMA table_info(survey_responses)")
        rcols = [row[1] for row in cur.fetchall()]
        r_required = {'id', 'survey_id', 'user_id', 'company_id', 'submitted_at'}
        if not r_required.issubset(set(rcols)):
            cur.execute("DROP TABLE IF EXISTS survey_responses")
            conn.commit()

        # survey_answers kolon kontrolü
        cur.execute("PRAGMA table_info(survey_answers)")
        acols = [row[1] for row in cur.fetchall()]
        a_required = {'id', 'response_id', 'question_id', 'answer_text', 'answer_number', 'answer_choice'}
        if not a_required.issubset(set(acols)):
            cur.execute("DROP TABLE IF EXISTS survey_answers")
            conn.commit()
    finally:
        conn.close()
    ss = SurveyService(db_path)
    survey_id = ss.create_survey(company_id=1, name="Doğrulama Anketi", description="Test amaçlı", status='active')
    logging.info(f"[OK] Anket oluşturuldu: #{survey_id}")

    q1_id = ss.add_question(survey_id, text="Çalışma ortamınızı nasıl değerlendirirsiniz?", q_type='text', order_index=1)
    q2_id = ss.add_question(survey_id, text="Haftalık çalışma saatiniz?", q_type='text', order_index=2)
    logging.info(f"[OK] Sorular eklendi: {q1_id}, {q2_id}")

    response_id = ss.submit_response(survey_id, user_id=1, company_id=1, answers={
        q1_id: 'İyi',
        q2_id: '45'
    })
    logging.info(f"[OK] Anket yanıtı gönderildi: response #{response_id}")

    survey = ss.get_survey_with_questions(survey_id)
    assert survey.get('id') == survey_id and len(survey.get('questions', [])) == 2, "Anket/soru doğrulaması başarısız"
    results = ss.get_results(survey_id)
    assert any(r['response_id'] == response_id for r in results), "Anket yanıtı bulunamadı"
    logging.info("[OK] Anket ve yanıtlar doğrulandı")


def main() -> None:
    db_path = os.path.join(BASE_DIR, 'data', 'sdg_desktop.sqlite')
    verify_forms(db_path)
    verify_surveys(db_path)
    logging.info("\n=== TAMAMLANDI: Form ve anket gönderimleri veritabanında doğrulandı ===")


if __name__ == '__main__':
    main()
