#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS/SKDM Anketleri
Türkiye Sürdürülebilirlik Raporlama Standartları
"""

from typing import Dict


class TSRSQuestionnaires:
    """TSRS/SKDM anketleri"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def get_tsrs_survey(code: str) -> Dict:
        """TSRS kodu için anket"""

        surveys = {
            'E1': TSRSQuestionnaires._tsrs_e1(),
            'S1': TSRSQuestionnaires._tsrs_s1(),
            'G1': TSRSQuestionnaires._tsrs_g1(),
        }

        return surveys.get(code, {})

    @staticmethod
    def _tsrs_e1() -> Dict:
        """E1: İklim Değişikliği"""
        return {
            'title': 'TSRS E1 - İklim Değişikliği',
            'description': 'İklim stratejisi ve emisyon yönetimi',
            'category': 'TSRS',
            'questions': [
                {'text': 'İklim değişikliği stratejiniz var mı?', 'type': 'yes_no', 'required': 1},
                {'text': 'Scope 1+2 emisyonlarınız (ton CO2e)?', 'type': 'number', 'required': 1},
                {'text': 'Karbon azaltım hedefi var mı?', 'type': 'yes_no', 'required': 1},
                {'text': 'Hedef yılınız ve azaltım oranı?', 'type': 'text', 'required': 0},
                {'text': 'İklim riskleri değerlendirdiniz mi?', 'type': 'yes_no', 'required': 1}
            ]
        }

    @staticmethod
    def _tsrs_s1() -> Dict:
        """S1: İş Gücü"""
        return {
            'title': 'TSRS S1 - İş Gücü',
            'description': 'Çalışan hakları ve çalışma koşulları',
            'category': 'TSRS',
            'questions': [
                {'text': 'Toplam çalışan sayısı?', 'type': 'number', 'required': 1},
                {'text': 'Kadın çalışan oranı (%)?', 'type': 'number', 'required': 1},
                {'text': 'İş sözleşmesi türleri?', 'type': 'multiple',
                 'options': 'Süresiz|Süreli|Yarı zamanlı|Danışman', 'required': 1},
                {'text': 'Sendika üyelik oranı (%)?', 'type': 'number', 'required': 0},
                {'text': 'İnsan hakları politikanız var mı?', 'type': 'yes_no', 'required': 1}
            ]
        }

    @staticmethod
    def _tsrs_g1() -> Dict:
        """G1: Yönetişim"""
        return {
            'title': 'TSRS G1 - Yönetişim',
            'description': 'Kurumsal yönetim ve sürdürülebilirlik entegrasyonu',
            'category': 'TSRS',
            'questions': [
                {'text': 'Sürdürülebilirlik komitesi var mı?', 'type': 'yes_no', 'required': 1},
                {'text': 'Yönetim kurulunda kadın üye oranı (%)?', 'type': 'number', 'required': 1},
                {'text': 'Etik kurallar belgesi var mı?', 'type': 'yes_no', 'required': 1},
                {'text': 'Çıkar çatışması politikası var mı?', 'type': 'yes_no', 'required': 1}
            ]
        }

