#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP AI Analiz Modülü
Verileri analiz eder ve yorumlar üretir
"""

import logging
import json
from typing import Any, Dict, Optional
from config.icons import Icons


class CDPAIAnalyzer:
    """CDP verileri için AI destekli analiz"""

    def __init__(self, use_api: bool = False, api_key: Optional[str] = None):
        """
        Args:
            use_api: OpenAI API kullan (False=Lokal analiz)
            api_key: OpenAI API anahtarı
        """
        self.use_api = use_api
        self.api_key = api_key

        if use_api and api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-3.5-turbo"  # veya "gpt-4"
            except ImportError:
                logging.info("[UYARI] OpenAI kütüphanesi bulunamadı. Lokal analiz kullanılacak.")
                self.use_api = False

    def analyze_climate_performance(self, data: Dict[str, Any]) -> Dict[str, str]:
        """İklim performansı analiz et"""

        emissions = data.get('emissions', {})
        comparison = data.get('comparison', {})

        if self.use_api:
            return self._analyze_with_openai(data, 'climate')
        else:
            return self._analyze_climate_local(emissions, comparison)

    def _analyze_climate_local(self, emissions: Dict, comparison: Dict) -> Dict[str, str]:
        """Lokal kural tabanlı iklim analizi"""

        analysis = {
            'summary': '',
            'performance': '',
            'trends': '',
            'risks': '',
            'opportunities': '',
            'recommendations': ''
        }

        total_emissions = emissions.get('total', 0)
        scope1 = emissions.get('scope1', 0)
        scope2 = emissions.get('scope2', 0)
        scope3 = emissions.get('scope3', 0)

        # Özet
        analysis['summary'] = f"""
Toplam sera gazı emisyonlarınız {total_emissions:,.0f} tCO2e'dir. 
Bu emisyonların {scope1:,.0f} tCO2e'si Scope 1 (doğrudan),
{scope2:,.0f} tCO2e'si Scope 2 (satın alınan enerji) ve
{scope3:,.0f} tCO2e'si Scope 3 (değer zinciri) kaynaklarından oluşmaktadır.
        """.strip()

        # Performans değerlendirmesi
        if comparison and 'emissions_change' in comparison:
            change = comparison['emissions_change']
            pct_change = change.get('percentage_change', 0)

            if pct_change < -10:
                performance_level = "mükemmel"
                emoji = "🌟"
            elif pct_change < -5:
                performance_level = "iyi"
                emoji = Icons.SUCCESS
            elif pct_change < 0:
                performance_level = "olumlu"
                emoji = Icons.REPORT
            elif pct_change < 5:
                performance_level = "stabil"
                emoji = Icons.RIGHT
            else:
                performance_level = "iyileştirme gerekli"
                emoji = Icons.WARNING

            analysis['performance'] = f"""
{emoji} Performans: {performance_level.upper()}

Önceki yıla göre emisyonlarınızda %{abs(pct_change):.1f} 
{'azalma' if pct_change < 0 else 'artış'} görülmüştür. 
Bu, {'karbon azaltım hedeflerinize ulaşma yolunda olduğunuzu' if pct_change < 0 else 'emisyon azaltım stratejilerinin gözden geçirilmesi gerektiğini'} göstermektedir.
            """.strip()
        else:
            analysis['performance'] = "Önceki yıl verisi bulunmamaktadır. Trend analizi yapılamıyor."

        # Scope analizi ve öneriler
        total = scope1 + scope2 + scope3
        if total > 0:
            scope3_ratio = (scope3 / total) * 100

            if scope3_ratio > 70:
                analysis['trends'] = f"""
{Icons.CHART_UP} Scope 3 Emisyonları Yüksek

Toplam emisyonlarınızın %{scope3_ratio:.1f}'i Scope 3 kaynaklarından geliyor.
Bu, değer zincirinizde önemli karbon azaltım fırsatları olduğunu gösterir.
                """.strip()

                analysis['opportunities'] = """
🎯 Tedarik Zinciri Optimizasyonu

- Tedarikçilerin emisyon verilerini toplayın
- Düşük karbonlu tedarikçileri tercih edin
- Taşımacılık optimizasyonu yapın
- Ürün ömrü döngüsü analizi gerçekleştirin
                """.strip()

        # Riskler
        if total_emissions > 10000:
            analysis['risks'] = f"""
{Icons.WARNING} Yüksek Emisyon Profili Riskleri

- Karbon fiyatlandırma maliyetleri artabilir
- CSRD/CBAM gibi yeni düzenlemeler etkilenme riski yüksek
- Yatırımcı baskısı artabilir
- Reputasyon riski
            """.strip()

        # Öneriler
        recommendations = []

        if scope1 > 0:
            recommendations.append("• Enerji verimliliği projelerine yatırım yapın")
            recommendations.append("• Yenilenebilir enerji kaynaklarına geçiş planlayın")

        if scope2 > 0:
            recommendations.append("• Yeşil enerji sertifikalı elektrik satın alın")
            recommendations.append("• Sahada güneş enerjisi sistemi kurun")

        if scope3 > total * 0.5:
            recommendations.append("• Tedarikçi engagement programı başlatın")
            recommendations.append("• Sürdürülebilir lojistik çözümleri kullanın")
            recommendations.append("• Ürün tasarımında karbon verimliliğine odaklanın")

        recommendations.append("• Science Based Targets (SBTi) inisiyatifine katılın")
        recommendations.append("• İç karbon fiyatlandırması uygulayın")

        analysis['recommendations'] = "\n".join(recommendations)

        return analysis

    def analyze_water_security(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Su güvenliği analizi"""

        water = data.get('water_consumption', {})

        analysis = {
            'summary': '',
            'performance': '',
            'risks': '',
            'opportunities': '',
            'recommendations': ''
        }

        withdrawn = water.get('withdrawn', 0)
        consumed = water.get('consumed', 0)
        recycled = water.get('recycled', 0)

        # Özet
        analysis['summary'] = f"""
Toplam su çekimi: {withdrawn:,.0f} m³
Su tüketimi: {consumed:,.0f} m³
Geri dönüştürülen su: {recycled:,.0f} m³
        """.strip()

        # Geri dönüşüm oranı
        if withdrawn > 0:
            recycling_rate = (recycled / withdrawn) * 100

            if recycling_rate > 50:
                level = "Mükemmel"
                emoji = "🌟"
            elif recycling_rate > 30:
                level = "İyi"
                emoji = Icons.SUCCESS
            elif recycling_rate > 10:
                level = "Orta"
                emoji = Icons.REPORT
            else:
                level = "Düşük"
                emoji = Icons.WARNING

            analysis['performance'] = f"""
{emoji} Su Geri Dönüşüm Performansı: {level}

Geri dönüşüm oranınız: %{recycling_rate:.1f}
            """.strip()

        # Öneriler
        recommendations = [
            "• Su verimliliği teknolojilerine yatırım yapın",
            "• Su geri dönüşüm sistemlerini geliştirin",
            "• Su risk haritalaması yapın",
            "• CEO Water Mandate'e katılın",
            "• Tedarikçilerden su verileri toplayın"
        ]

        analysis['recommendations'] = "\n".join(recommendations)

        return analysis

    def analyze_forests(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Orman analizi"""

        analysis = {
            'summary': 'Orman ürünleri kullanımı ve ormansızlaşma riski değerlendirmesi',
            'risks': 'Tedarik zincirinde ormansızlaşma riski değerlendirilmelidir',
            'opportunities': 'Sertifikalı ahşap/kağıt ürünleri kullanımı artırılabilir',
            'recommendations': """
• FSC/PEFC sertifikalı ürünler tercih edin
• Tedarikçi due diligence süreçlerini güçlendirin
• Ormansızlaşma-free taahhütleri yapın
• Şeffaf raporlama yapın
            """.strip()
        }

        return analysis

    def _analyze_with_openai(self, data: Dict[str, Any], report_type: str) -> Dict[str, str]:
        """OpenAI API ile analiz (gelişmiş)"""

        try:
            # Veriyi metne çevir
            data_str = json.dumps(data, indent=2, ensure_ascii=False)

            prompt = f"""
Sen bir CDP (Carbon Disclosure Project) uzmanısın. Aşağıdaki {report_type} verilerini analiz et ve 
profesyonel bir değerlendirme yap.

VERİLER:
{data_str}

Lütfen şu başlıklar altında analiz yap:
1. Özet (Executive Summary)
2. Performans Değerlendirmesi
3. Trendler
4. Riskler
5. Fırsatlar
6. Öneriler

Türkçe yaz ve profesyonel bir ton kullan.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen bir sürdürülebilirlik ve CDP raporlama uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            full_text = response.choices[0].message.content

            # Metni bölümlere ayır (basit parsing)
            analysis = {
                'summary': full_text,  # Tamamını summary'e koy
                'performance': '',
                'trends': '',
                'risks': '',
                'opportunities': '',
                'recommendations': ''
            }

            return analysis

        except Exception as e:
            logging.error(f"[HATA] OpenAI analizi başarısız: {e}")
            # Hata durumunda lokal analize geri dön
            if report_type == 'climate':
                return self._analyze_climate_local(data.get('emissions', {}), data.get('comparison', {}))
            else:
                return {'summary': 'Analiz yapılamadı', 'recommendations': 'Veri eksik'}

    def calculate_cdp_score_estimate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """CDP skoru tahmini"""

        score = {
            'disclosure': 0,
            'awareness': 0,
            'management': 0,
            'leadership': 0,
            'total': 0,
            'grade': 'D'
        }

        # Basit skorlama (geliştirilecek)
        emissions = data.get('emissions', {})

        # Veri eksiksizliği kontrolü
        if emissions.get('scope1', 0) > 0 and emissions.get('scope2', 0) > 0:
            score['disclosure'] = 60  # Veri paylaşımı

        # Emisyon azaltımı kontrolü
        comparison = data.get('comparison', {})
        if comparison and 'emissions_change' in comparison:
            change = comparison['emissions_change'].get('percentage_change', 0)
            if change < 0:  # Azalma varsa
                score['management'] = 50
                if change < -10:  # %10'dan fazla azalma
                    score['leadership'] = 30

        score['total'] = sum([score['disclosure'], score['awareness'], score['management'], score['leadership']])

        # Grade belirleme
        if score['total'] >= 90:
            score['grade'] = 'A'
        elif score['total'] >= 70:
            score['grade'] = 'B'
        elif score['total'] >= 50:
            score['grade'] = 'C'
        else:
            score['grade'] = 'D'

        return score

