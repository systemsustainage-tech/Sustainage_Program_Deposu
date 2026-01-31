#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Soru Formları
GRI standartlarına göre veri toplama anketleri
"""

from typing import Dict


class GRIQuestionnaires:
    """GRI disclosure anketleri"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def get_gri_survey(disclosure: str) -> Dict:
        """GRI disclosure numarasına göre anket"""

        surveys = {
            '305-1': GRIQuestionnaires._gri_305_1(),
            '305-2': GRIQuestionnaires._gri_305_2(),
            '401-1': GRIQuestionnaires._gri_401_1(),
            '403-9': GRIQuestionnaires._gri_403_9(),
            '404-1': GRIQuestionnaires._gri_404_1(),
        }

        return surveys.get(disclosure, {})

    @staticmethod
    def _gri_305_1() -> Dict:
        """GRI 305-1: Doğrudan GHG Emisyonları (Scope 1)"""
        return {
            'title': 'GRI 305-1: Scope 1 GHG Emisyonları',
            'description': 'Doğrudan sera gazı emisyonlarınız',
            'category': 'GRI',
            'questions': [
                {
                    'text': 'Şirket araçlarınızdan kaynaklanan yakıt tüketimi (litre/yıl)?',
                    'type': 'number',
                    'required': 1,
                    'help_text': 'Benzin + Mazot toplamı'
                },
                {
                    'text': 'Sabit yanma kaynaklarınız var mı? (Kazan, jeneratör)',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Doğalgaz tüketiminiz (m³/yıl)?',
                    'type': 'number',
                    'required': 0
                },
                {
                    'text': 'Soğutucu gaz kaçağı yaşadınız mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Kaçan soğutucu gaz miktarı (kg)?',
                    'type': 'number',
                    'required': 0
                },
                {
                    'text': 'Toplam Scope 1 emisyonunuz (ton CO2e)?',
                    'type': 'number',
                    'required': 0,
                    'help_text': 'Hesaplamadıysanız boş bırakın'
                }
            ]
        }

    @staticmethod
    def _gri_305_2() -> Dict:
        """GRI 305-2: Enerji Dolaylı GHG Emisyonları (Scope 2)"""
        return {
            'title': 'GRI 305-2: Scope 2 GHG Emisyonları',
            'description': 'Satın alınan elektrik ve enerji emisyonları',
            'category': 'GRI',
            'questions': [
                {
                    'text': 'Yıllık elektrik tüketiminiz (kWh)?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Elektriğin ne kadarı şebekeden?',
                    'type': 'number',
                    'required': 1,
                    'help_text': 'kWh cinsinden'
                },
                {
                    'text': 'Yenilenebilir enerji sertifikanız var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Scope 2 emisyonunuz (ton CO2e)?',
                    'type': 'number',
                    'required': 0
                }
            ]
        }

    @staticmethod
    def _gri_401_1() -> Dict:
        """GRI 401-1: İşe Alım ve İşten Ayrılmalar"""
        return {
            'title': 'GRI 401-1: İşe Alım ve Ayrılmalar',
            'description': 'İş gücü hareketleri',
            'category': 'GRI',
            'questions': [
                {
                    'text': 'Son 1 yılda kaç kişi işe aldınız?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Bunların kaçı kadın?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Son 1 yılda kaç kişi ayrıldı?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Ayrılanların kaçı kadın?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Gönüllü ayrılma oranı nedir?',
                    'type': 'number',
                    'required': 0,
                    'help_text': 'Yüzde olarak'
                }
            ]
        }

    @staticmethod
    def _gri_403_9() -> Dict:
        """GRI 403-9: İşle İlgili Yaralanmalar"""
        return {
            'title': 'GRI 403-9: İş Kazaları',
            'description': 'İş sağlığı ve güvenliği verileri',
            'category': 'GRI',
            'questions': [
                {
                    'text': 'Son 1 yılda kaç iş kazası yaşandı?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Kayıp gün yaratan kaza sayısı?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Toplam kayıp gün sayısı?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Ölümlü kaza oldu mu?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'LTIFR (Lost Time Injury Frequency Rate) nedir?',
                    'type': 'number',
                    'required': 0
                }
            ]
        }

    @staticmethod
    def _gri_404_1() -> Dict:
        """GRI 404-1: Eğitim Saatleri"""
        return {
            'title': 'GRI 404-1: Çalışan Eğitimi',
            'description': 'Çalışan başına eğitim saatleri',
            'category': 'GRI',
            'questions': [
                {
                    'text': 'Son 1 yılda toplam eğitim saati?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Kaç çalışan eğitim aldı?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Kadın çalışanlar için ortalama eğitim saati?',
                    'type': 'number',
                    'required': 0
                },
                {
                    'text': 'Erkek çalışanlar için ortalama eğitim saati?',
                    'type': 'number',
                    'required': 0
                },
                {
                    'text': 'Hangi konularda eğitim veriliyor?',
                    'type': 'multiple',
                    'options': 'Teknik|İSG|Liderlik|Dil|Dijital|Sürdürülebilirlik|Diğer',
                    'required': 1
                }
            ]
        }

