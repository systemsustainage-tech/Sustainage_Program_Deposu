#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Anket Şablonları
Her SDG için özel anket soruları
"""

from typing import Dict


class SDGSurveys:
    """SDG anket şablonları"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    @staticmethod
    def get_sdg_survey(sdg_number: int) -> Dict:
        """SDG numarasına göre anket şablonu"""

        surveys = {
            1: SDGSurveys._sdg1_poverty(),
            7: SDGSurveys._sdg7_energy(),
            8: SDGSurveys._sdg8_work(),
            13: SDGSurveys._sdg13_climate(),
            # Diğerleri benzer şekilde
        }

        return surveys.get(sdg_number, SDGSurveys._default_template(sdg_number))

    @staticmethod
    def _sdg7_energy() -> Dict:
        """SDG 7: Erişilebilir ve Temiz Enerji"""
        return {
            'title': 'SDG 7 - Erişilebilir ve Temiz Enerji Anketi',
            'description': 'Firmanızın enerji tüketimi ve yenilenebilir enerji kullanımı hakkında bilgi toplamak için.',
            'category': 'SDG',
            'questions': [
                {
                    'text': '2024 yılında toplam elektrik tüketiminiz (kWh)?',
                    'type': 'number',
                    'required': 1,
                    'help_text': 'Yıllık toplam elektrik faturalarınızdan bulabilirsiniz'
                },
                {
                    'text': 'Yenilenebilir enerji kullanıyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Yenilenebilir enerji kullanıyorsanız, hangi kaynaktan?',
                    'type': 'multiple',
                    'options': 'Güneş|Rüzgar|Hidroelektrik|Biyokütle|Jeotermal|Diğer',
                    'required': 0,
                    'help_text': 'Birden fazla seçebilirsiniz'
                },
                {
                    'text': 'Toplam enerji tüketiminizin yüzde kaçı yenilenebilir?',
                    'type': 'number',
                    'required': 0,
                    'help_text': 'Yaklaşık oran yeterli (0-100 arası)'
                },
                {
                    'text': 'Enerji verimliliği projeleriniz var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Varsa, hangi enerji verimliliği projeleri uyguladınız?',
                    'type': 'textarea',
                    'required': 0,
                    'help_text': 'LED aydınlatma, ısı yalıtımı, verimli ekipman vb.'
                },
                {
                    'text': 'Son 3 yılda enerji tüketiminizde azalma oldu mu?',
                    'type': 'choice',
                    'options': 'Evet, önemli ölçüde azaldı|Evet, az miktarda azaldı|Değişmedi|Arttı',
                    'required': 1
                },
                {
                    'text': 'Çalışanlarınıza enerji tasarrufu eğitimi veriyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Enerji yönetimiyle ilgili hedefleriniz var mı?',
                    'type': 'textarea',
                    'required': 0,
                    'help_text': 'Örn: 2025 yılına kadar %20 azaltma'
                }
            ]
        }

    @staticmethod
    def _sdg13_climate() -> Dict:
        """SDG 13: İklim Eylemi"""
        return {
            'title': 'SDG 13 - İklim Eylemi Anketi',
            'description': 'Firmanızın iklim değişikliğine karşı aldığı önlemler hakkında.',
            'category': 'SDG',
            'questions': [
                {
                    'text': 'Karbon ayak izinizi ölçüyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Scope 1 emisyonlarınız var mı? (Doğrudan emisyonlar)',
                    'type': 'yes_no',
                    'required': 1,
                    'help_text': 'Şirket araçları, kazanlar, jeneratörler'
                },
                {
                    'text': 'Yıllık yakıt tüketiminiz (litre)?',
                    'type': 'number',
                    'required': 0,
                    'help_text': 'Benzin, mazot, doğalgaz toplamı'
                },
                {
                    'text': 'İklim değişikliği risk değerlendirmesi yaptınız mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Karbon azaltım hedefi var mı?',
                    'type': 'choice',
                    'options': 'Evet, belirli hedefimiz var|Planlıyoruz|Hayır|Bilmiyorum',
                    'required': 1
                },
                {
                    'text': 'İklim değişikliğine uyum planınız var mı?',
                    'type': 'textarea',
                    'required': 0
                },
                {
                    'text': 'Çalışanlarınıza iklim değişikliği eğitimi veriyor musunuz?',
                    'type': 'scale',
                    'required': 1,
                    'help_text': '1=Hiç, 5=Düzenli olarak'
                }
            ]
        }

    @staticmethod
    def _sdg8_work() -> Dict:
        """SDG 8: İnsana Yakışır İş ve Ekonomik Büyüme"""
        return {
            'title': 'SDG 8 - İnsana Yakışır İş Anketi',
            'description': 'İstihdam, çalışma koşulları ve ekonomik gelişme hakkında.',
            'category': 'SDG',
            'questions': [
                {
                    'text': 'Toplam çalışan sayınız?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Son 1 yılda kaç kişi işe aldınız?',
                    'type': 'number',
                    'required': 1
                },
                {
                    'text': 'Gençlere (18-24 yaş) istihdam sağlıyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Asgari ücretin üzerinde maaş ödüyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Çalışanlara ek yan haklar sağlıyor musunuz?',
                    'type': 'multiple',
                    'options': 'Sağlık sigortası|Yemek|Servis|Eğitim desteği|Performans primi|Diğer',
                    'required': 1
                },
                {
                    'text': 'İş sağlığı ve güvenliği politikanız var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Çalışma saatleri yasal limitlere uygun mu?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Çocuk işçi çalıştırılmasına karşı politikanız var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Zorla çalıştırmaya karşı önlemleriniz neler?',
                    'type': 'textarea',
                    'required': 0
                }
            ]
        }

    @staticmethod
    def _sdg1_poverty() -> Dict:
        """SDG 1: Yoksulluğa Son"""
        return {
            'title': 'SDG 1 - Yoksulluğa Son Anketi',
            'description': 'Firmanızın yoksullukla mücadele çalışmaları.',
            'category': 'SDG',
            'questions': [
                {
                    'text': 'Düşük gelirli bölgelerde faaliyet gösteriyor musunuz?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Yerel istihdama katkınız nedir?',
                    'type': 'textarea',
                    'required': 1
                },
                {
                    'text': 'Sosyal yardım programlarınız var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'Çalışanlarınıza finansal okuryazarlık eğitimi veriyor musunuz?',
                    'type': 'yes_no',
                    'required': 0
                },
                {
                    'text': 'Topluma yönelik yoksulluk azaltma projeleriniz var mı?',
                    'type': 'textarea',
                    'required': 0
                }
            ]
        }

    @staticmethod
    def _default_template(sdg_number: int) -> Dict:
        """Diğer SDG'ler için genel şablon"""
        return {
            'title': f'SDG {sdg_number} Anketi',
            'description': f'SDG {sdg_number} ile ilgili veri toplama anketi',
            'category': 'SDG',
            'questions': [
                {
                    'text': f'SDG {sdg_number} ile ilgili hangi faaliyetleri yapıyorsunuz?',
                    'type': 'textarea',
                    'required': 1
                },
                {
                    'text': 'Bu alanda ölçülebilir hedefleriniz var mı?',
                    'type': 'yes_no',
                    'required': 1
                },
                {
                    'text': 'İlerlemenizi nasıl ölçüyorsunuz?',
                    'type': 'textarea',
                    'required': 0
                }
            ]
        }

