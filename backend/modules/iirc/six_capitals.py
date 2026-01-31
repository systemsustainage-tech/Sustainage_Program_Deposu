#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
6 Sermaye Yönetim Modülü
IIRC 6 Sermaye modelinin detaylı yönetimi
"""

from typing import Dict, List
from utils.language_manager import LanguageManager

class SixCapitalsManager:
    """6 Sermaye detaylı yönetimi"""

    def __init__(self):
        self.lm = LanguageManager()
        self.CAPITAL_CATEGORIES = {
            "mali": {
                "alt_kategoriler": [
                    self.lm.tr('cap_fin_sub1', "Nakit ve Nakit Benzerleri"),
                    self.lm.tr('cap_fin_sub2', "Yatırımlar"),
                    self.lm.tr('cap_fin_sub3', "Borçlanma Kapasitesi"),
                    self.lm.tr('cap_fin_sub4', "Özkaynaklar")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_fin_kpi1', "Toplam Varlıklar"),
                    self.lm.tr('cap_fin_kpi2', "Özkaynak Getirisi (ROE)"),
                    self.lm.tr('cap_fin_kpi3', "Borç/Özkaynak Oranı"),
                    self.lm.tr('cap_fin_kpi4', "Serbest Nakit Akışı")
                ]
            },
            "imalat": {
                "alt_kategoriler": [
                    self.lm.tr('cap_mfg_sub1', "Üretim Tesisleri"),
                    self.lm.tr('cap_mfg_sub2', "Makineler ve Ekipman"),
                    self.lm.tr('cap_mfg_sub3', "Binalar ve Altyapı"),
                    self.lm.tr('cap_mfg_sub4', "Lojistik Ağı")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_mfg_kpi1', "Üretim Kapasitesi"),
                    self.lm.tr('cap_mfg_kpi2', "Kapasite Kullanım Oranı"),
                    self.lm.tr('cap_mfg_kpi3', "Varlık Verimliliği"),
                    self.lm.tr('cap_mfg_kpi4', "Bakım Maliyetleri")
                ]
            },
            "entelektuel": {
                "alt_kategoriler": [
                    self.lm.tr('cap_int_sub1', "Patentler ve Fikri Mülkiyet"),
                    self.lm.tr('cap_int_sub2', "Markalar"),
                    self.lm.tr('cap_int_sub3', "Kurumsal Bilgi ve Sistemler"),
                    self.lm.tr('cap_int_sub4', "Ar-Ge Portföyü")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_int_kpi1', "Patent Sayısı"),
                    self.lm.tr('cap_int_kpi2', "Ar-Ge Yatırımı"),
                    self.lm.tr('cap_int_kpi3', "Marka Değeri"),
                    self.lm.tr('cap_int_kpi4', "Yeni Ürün Geliştirilme Süresi")
                ]
            },
            "insani": {
                "alt_kategoriler": [
                    self.lm.tr('cap_hum_sub1', "Çalışan Yetkinlikleri"),
                    self.lm.tr('cap_hum_sub2', "Eğitim ve Gelişim"),
                    self.lm.tr('cap_hum_sub3', "Çalışan Motivasyonu"),
                    self.lm.tr('cap_hum_sub4', "Liderlik Kapasitesi")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_hum_kpi1', "Çalışan Memnuniyeti"),
                    self.lm.tr('cap_hum_kpi2', "Eğitim Saati/Çalışan"),
                    self.lm.tr('cap_hum_kpi3', "İşgücü Devir Oranı"),
                    self.lm.tr('cap_hum_kpi4', "Liderlik Programları")
                ]
            },
            "sosyal": {
                "alt_kategoriler": [
                    self.lm.tr('cap_soc_sub1', "Müşteri İlişkileri"),
                    self.lm.tr('cap_soc_sub2', "Tedarikçi İlişkileri"),
                    self.lm.tr('cap_soc_sub3', "Topluluk Bağlantıları"),
                    self.lm.tr('cap_soc_sub4', "Kurumsal İtibar")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_soc_kpi1', "Müşteri Memnuniyeti"),
                    self.lm.tr('cap_soc_kpi2', "Net Tavsiye Skoru (NPS)"),
                    self.lm.tr('cap_soc_kpi3', "Tedarikçi İşbirliği Programları"),
                    self.lm.tr('cap_soc_kpi4', "Topluluk Yatırımları")
                ]
            },
            "dogal": {
                "alt_kategoriler": [
                    self.lm.tr('cap_nat_sub1', "Enerji Kaynakları"),
                    self.lm.tr('cap_nat_sub2', "Su Kaynakları"),
                    self.lm.tr('cap_nat_sub3', "Ham Maddeler"),
                    self.lm.tr('cap_nat_sub4', "Ekosistem Hizmetleri")
                ],
                "kpi_ornekleri": [
                    self.lm.tr('cap_nat_kpi1', "Enerji Tüketimi"),
                    self.lm.tr('cap_nat_kpi2', "Su Tüketimi"),
                    self.lm.tr('cap_nat_kpi3', "Karbon Ayak İzi"),
                    self.lm.tr('cap_nat_kpi4', "Atık Azaltma")
                ]
            }
        }

    def get_capital_details(self, capital_type: str) -> Dict:
        """Sermaye detaylarını getir"""
        return self.CAPITAL_CATEGORIES.get(capital_type, {})

    def get_all_kpis(self) -> Dict[str, List[str]]:
        """Tüm KPI'ları getir"""
        kpis = {}
        for capital_type, details in self.CAPITAL_CATEGORIES.items():
            kpis[capital_type] = details.get("kpi_ornekleri", [])
        return kpis
