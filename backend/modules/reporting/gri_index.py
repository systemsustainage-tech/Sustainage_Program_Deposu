#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI İçerik İndeksi
GRI standartlarına göre otomatik içerik indeksi oluşturur
"""

from typing import Any, Dict, List


class GRIIndex:
    """GRI İçerik İndeksi oluşturucu"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    # GRI Standartları mapping
    GRI_STANDARDS: Dict[str, Dict[str, Any]] = {
        # Çevresel
        'GRI 302': {'name': 'Enerji', 'topics': {
            '302-1': 'Örgüt içi enerji tüketimi',
            '302-3': 'Enerji yoğunluğu',
            '302-4': 'Enerji tüketiminde azalma'
        }},
        'GRI 305': {'name': 'Emisyonlar', 'topics': {
            '305-1': 'Doğrudan (Scope 1) GHG emisyonları',
            '305-2': 'Enerji dolaylı (Scope 2) GHG emisyonları',
            '305-3': 'Diğer dolaylı (Scope 3) GHG emisyonları',
            '305-4': 'GHG emisyon yoğunluğu'
        }},
        'GRI 303': {'name': 'Su ve Atıksu', 'topics': {
            '303-3': 'Su çekimi',
            '303-4': 'Su deşarjı',
            '303-5': 'Su tüketimi'
        }},
        'GRI 306': {'name': 'Atık', 'topics': {
            '306-3': 'Oluşturulan atık',
            '306-4': 'Bertaraftan yönlendirilen atık',
            '306-5': 'Bertarafa yönlendirilen atık'
        }},

        # Sosyal
        'GRI 401': {'name': 'İstihdam', 'topics': {
            '401-1': 'Yeni işe alımlar ve işten ayrılmalar',
            '401-2': 'Çalışan yan hakları',
            '401-3': 'Ebeveyn izni'
        }},
        'GRI 403': {'name': 'İş Sağlığı ve Güvenliği', 'topics': {
            '403-8': 'İSG yönetim sistemine tabi çalışanlar',
            '403-9': 'İşle ilgili yaralanmalar',
            '403-10': 'İşle ilgili hastalıklar'
        }},
        'GRI 404': {'name': 'Eğitim', 'topics': {
            '404-1': 'Çalışan başına yıllık ortalama eğitim saati',
            '404-2': 'Çalışan becerilerini geliştirme programları',
            '404-3': 'Performans ve kariyer gelişimi değerlendirmesi'
        }},
        'GRI 405': {'name': 'Çeşitlilik ve Fırsat Eşitliği', 'topics': {
            '405-1': 'Yönetişim organları ve çalışanlarda çeşitlilik',
            '405-2': 'Kadın erkek temel maaş ve ücret oranı'
        }},

        # Ekonomik
        'GRI 201': {'name': 'Ekonomik Performans', 'topics': {
            '201-1': 'Üretilen ve dağıtılan doğrudan ekonomik değer',
            '201-2': 'İklim değişikliğinin finansal etkileri',
            '201-3': 'Tanımlanmış fayda planı yükümlülükleri',
            '201-4': 'Hükümetten alınan mali yardım'
        }}
    }

    def generate_index(self, company_id: int, year: int) -> List[Dict]:
        """
        GRI içerik indeksi oluştur
        
        Args:
            company_id: Firma ID
            year: Rapor yılı
            
        Returns:
            List[Dict]: İndeks kayıtları
        """
        index = []

        # Her GRI standardı için kontrol et
        for std_code, std_info in self.GRI_STANDARDS.items():
            for topic_code, topic_name in std_info['topics'].items():
                # Veri var mı kontrol et
                has_data = self._check_data_availability(company_id, year, std_code, topic_code)

                if has_data:
                    index.append({
                        'standard': std_code,
                        'disclosure': topic_code,
                        'name': topic_name,
                        'location': self._get_report_location(topic_code),
                        'status': 'Raporlandı'
                    })

        return index

    def _check_data_availability(self, company_id: int, year: int,
                                 standard: str, disclosure: str) -> bool:
        """Veri mevcut mu kontrol et"""
        # Basitleştirilmiş - gerçekte veritabanından kontrol edilir

        # Enerji (302)
        if standard == 'GRI 302':
            return True  # Enerji modülü var

        # Emisyonlar (305)
        if standard == 'GRI 305':
            return True  # Karbon modülü var

        # Su (303)
        if standard == 'GRI 303':
            return True  # Su modülü var

        # Atık (306)
        if standard == 'GRI 306':
            return True  # Atık modülü var

        # İstihdam (401)
        if standard == 'GRI 401':
            return True  # İK modülü var

        # İSG (403)
        if standard == 'GRI 403':
            return True  # İSG modülü var

        # Eğitim (404)
        if standard == 'GRI 404':
            return True  # Eğitim modülü var

        # Çeşitlilik (405)
        if standard == 'GRI 405':
            return True  # İK diversity modülü var

        return False

    def _get_report_location(self, disclosure: str) -> str:
        """Rapor içindeki konum"""
        # Basitleştirilmiş mapping
        location_map = {
            '302-1': 'Bölüm 3.2 - Enerji Yönetimi',
            '302-3': 'Bölüm 3.2 - Enerji Yoğunluğu',
            '305-1': 'Bölüm 3.1 - Scope 1 Emisyonlar',
            '305-2': 'Bölüm 3.1 - Scope 2 Emisyonlar',
            '305-3': 'Bölüm 3.1 - Scope 3 Emisyonlar',
            '303-5': 'Bölüm 3.3 - Su Yönetimi',
            '306-3': 'Bölüm 3.4 - Atık Yönetimi',
            '401-1': 'Bölüm 4.1 - İnsan Kaynakları',
            '403-9': 'Bölüm 4.2 - İş Sağlığı ve Güvenliği',
            '404-1': 'Bölüm 4.3 - Eğitim ve Geliştirme',
            '405-1': 'Bölüm 4.1 - Çeşitlilik',
            '405-2': 'Bölüm 4.1 - Ücret Eşitliği'
        }

        return location_map.get(disclosure, 'Ekler')

    def export_to_text(self, index: List[Dict]) -> str:
        """İndeksi metin formatına çevir"""
        text = "GRI ICERIK INDEKSI\n"
        text += "="*60 + "\n\n"

        current_standard = None

        for item in index:
            # Yeni standart başlığı
            if item['standard'] != current_standard:
                current_standard = item['standard']
                std_name = self.GRI_STANDARDS[current_standard]['name']
                text += f"\n{current_standard}: {std_name}\n"
                text += "-"*60 + "\n"

            # Disclosure
            text += f"{item['disclosure']}: {item['name']}\n"
            text += f"  Konum: {item['location']}\n"
            text += f"  Durum: {item['status']}\n\n"

        return text

