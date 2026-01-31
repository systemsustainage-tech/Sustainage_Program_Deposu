#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Değer Yaratma Hikayesi Modülü
İşletmenin değer yaratma sürecinin anlatımı
"""

from typing import Dict, List
from utils.language_manager import LanguageManager


class ValueCreationStory:
    """Değer yaratma hikayesi yönetimi"""

    def __init__(self):
        self.lm = LanguageManager()
        self.STORY_ELEMENTS = {
            "organizasyon": {
                "baslik": self.lm.tr('story_org_title', "Organizasyona Genel Bakış"),
                "aciklama": self.lm.tr('story_org_desc', "Şirketin misyonu, vizyonu, kültürü ve değerleri"),
                "sorular": [
                    self.lm.tr('story_org_q1', "Şirketinizin misyonu nedir?"),
                    self.lm.tr('story_org_q2', "Vizyonunuz nedir?"),
                    self.lm.tr('story_org_q3', "Temel değerleriniz nelerdir?"),
                    self.lm.tr('story_org_q4', "Faaliyet gösterdiğiniz sektörler?")
                ]
            },
            "dis_cevre": {
                "baslik": self.lm.tr('story_env_title', "Dış Çevre ve Paydaşlar"),
                "aciklama": self.lm.tr('story_env_desc', "İş ortamı, makroekonomik koşullar ve paydaş ilişkileri"),
                "sorular": [
                    self.lm.tr('story_env_q1', "Ana paydaşlarınız kimlerdir?"),
                    self.lm.tr('story_env_q2', "Sektör eğilimleri nelerdir?"),
                    self.lm.tr('story_env_q3', "Ekonomik koşullar nasıl?"),
                    self.lm.tr('story_env_q4', "Düzenleyici ortam nasıl?")
                ]
            },
            "yonetisim": {
                "baslik": self.lm.tr('story_gov_title', "Yönetişim"),
                "aciklama": self.lm.tr('story_gov_desc', "Yönetim yapısı, liderlik ve karar alma süreçleri"),
                "sorular": [
                    self.lm.tr('story_gov_q1', "Yönetim yapınız nasıl organize edilmiş?"),
                    self.lm.tr('story_gov_q2', "Karar alma süreçleriniz nedir?"),
                    self.lm.tr('story_gov_q3', "Risk yönetimi nasıl yapılıyor?"),
                    self.lm.tr('story_gov_q4', "Etik ve uyum nasıl sağlanıyor?")
                ]
            },
            "is_modeli": {
                "baslik": self.lm.tr('story_biz_title', "İş Modeli"),
                "aciklama": self.lm.tr('story_biz_desc', "Şirketin değer yaratma süreci ve iş modeli"),
                "sorular": [
                    self.lm.tr('story_biz_q1', "Girdi sermayeleriniz nelerdir?"),
                    self.lm.tr('story_biz_q2', "İş faaliyetleriniz nelerdir?"),
                    self.lm.tr('story_biz_q3', "Çıktılarınız nelerdir?"),
                    self.lm.tr('story_biz_q4', "Sonuçlar ne oluyor?")
                ]
            },
            "riskler": {
                "baslik": self.lm.tr('story_risk_title', "Riskler ve Fırsatlar"),
                "aciklama": self.lm.tr('story_risk_desc', "Önemli riskler, fırsatlar ve bunlara karşı alınan tedbirler"),
                "sorular": [
                    self.lm.tr('story_risk_q1', "Ana risleriniz nelerdir?"),
                    self.lm.tr('story_risk_q2', "Fırsatlarınız nelerdir?"),
                    self.lm.tr('story_risk_q3', "Risk azaltma stratejileriniz?"),
                    self.lm.tr('story_risk_q4', "Fırsatları nasıl değerlendiriyorsunuz?")
                ]
            },
            "strateji": {
                "baslik": self.lm.tr('story_strat_title', "Strateji ve Kaynak Tahsisi"),
                "aciklama": self.lm.tr('story_strat_desc', "Stratejik hedefler ve kaynak dağılım kararları"),
                "sorular": [
                    self.lm.tr('story_strat_q1', "Stratejik öncelikleriniz nelerdir?"),
                    self.lm.tr('story_strat_q2', "Kaynakları nasıl tahsis ediyorsunuz?"),
                    self.lm.tr('story_strat_q3', "Kısa ve uzun vadeli hedefleriniz?"),
                    self.lm.tr('story_strat_q4', "Başarı nasıl ölçülüyor?")
                ]
            },
            "performans": {
                "baslik": self.lm.tr('story_perf_title', "Performans"),
                "aciklama": self.lm.tr('story_perf_desc', "Şirketin performans sonuçları ve hedef karşılaştırması"),
                "sorular": [
                    self.lm.tr('story_perf_q1', "Ana performans göstergeleriniz?"),
                    self.lm.tr('story_perf_q2', "Hedeflerinize ulaşma durumunuz?"),
                    self.lm.tr('story_perf_q3', "6 sermaye üzerindeki etkiler?"),
                    self.lm.tr('story_perf_q4', "Paydaşlar için değer yaratımı?")
                ]
            },
            "gelecek": {
                "baslik": self.lm.tr('story_fut_title', "Gelecek Görünümü"),
                "aciklama": self.lm.tr('story_fut_desc', "Gelecek beklentiler, tahminler ve stratejiler"),
                "sorular": [
                    self.lm.tr('story_fut_q1', "Gelecek beklentileriniz nelerdir?"),
                    self.lm.tr('story_fut_q2', "Potansiyel zorluklar?"),
                    self.lm.tr('story_fut_q3', "Fırsatlar neler olabilir?"),
                    self.lm.tr('story_fut_q4', "Hazırlık stratejileriniz?")
                ]
            }
        }

    def get_story_template(self) -> List[Dict]:
        """Değer yaratma hikayesi şablonunu getir"""
        template = []
        for key, element in self.STORY_ELEMENTS.items():
            template.append({
                "kod": key,
                "baslik": element["baslik"],
                "aciklama": element["aciklama"],
                "sorular": element["sorular"]
            })
        return template

    def validate_story(self, story_data: Dict) -> Dict:
        """Hikaye tamamlılığını doğrula"""
        validation = {
            "tamamlanma_yuzdesi": 0.0,
            "eksik_bilesenler": [],
            "tamamlanan_bilesenler": []
        }

        total_elements = len(self.STORY_ELEMENTS)
        completed = 0

        for key in self.STORY_ELEMENTS.keys():
            if story_data.get(key, {}).get("icerik", "").strip():
                completed += 1
                validation["tamamlanan_bilesenler"].append(key)
            else:
                validation["eksik_bilesenler"].append(key)

        validation["tamamlanma_yuzdesi"] = (completed / total_elements) * 100

        return validation
