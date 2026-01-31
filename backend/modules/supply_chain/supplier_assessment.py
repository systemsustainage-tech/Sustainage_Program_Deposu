#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEDARİKÇİ DEĞERLENDİRME SİSTEMİ
Sürdürülebilirlik skorlaması ve risk analizi
"""

from datetime import datetime
from typing import Dict
from utils.language_manager import LanguageManager


class SupplierAssessment:
    """Tedarikçi değerlendirme ve skorlama sınıfı"""

    def __init__(self):
        self.lm = LanguageManager()
        
        # Değerlendirme Kategorileri ve Ağırlıkları
        self.ASSESSMENT_CATEGORIES = {
            'environmental': {
                'name': self.lm.tr('environmental_performance', 'Çevresel Performans'),
                'weight': 0.30,
                'criteria': {
                    'iso14001': {'name': self.lm.tr('iso14001', 'ISO 14001 Sertifikası'), 'max_score': 20},
                    'carbon_footprint': {'name': self.lm.tr('carbon_footprint', 'Karbon Ayak İzi Raporlaması'), 'max_score': 15},
                    'waste_management': {'name': self.lm.tr('waste_management', 'Atık Yönetimi'), 'max_score': 15},
                    'water_management': {'name': self.lm.tr('water_management', 'Su Yönetimi'), 'max_score': 10},
                    'renewable_energy': {'name': self.lm.tr('renewable_energy', 'Yenilenebilir Enerji Kullanımı'), 'max_score': 10}
                }
            },
            'social': {
                'name': self.lm.tr('social_responsibility', 'Sosyal Sorumluluk'),
                'weight': 0.30,
                'criteria': {
                    'labor_rights': {'name': self.lm.tr('labor_rights', 'Çalışan Hakları'), 'max_score': 20},
                    'health_safety': {'name': self.lm.tr('health_safety', 'İSG (ISO 45001)'), 'max_score': 15},
                    'no_child_labor': {'name': self.lm.tr('no_child_labor', 'Çocuk İşçiliği Yok'), 'max_score': 15},
                    'fair_wages': {'name': self.lm.tr('fair_wages', 'Adil Ücretlendirme'), 'max_score': 10},
                    'diversity': {'name': self.lm.tr('diversity', 'Çeşitlilik ve Kapsayıcılık'), 'max_score': 10}
                }
            },
            'governance': {
                'name': self.lm.tr('corporate_governance', 'Kurumsal Yönetişim'),
                'weight': 0.20,
                'criteria': {
                    'ethics_policy': {'name': self.lm.tr('ethics_policy', 'Etik Politikası'), 'max_score': 15},
                    'anti_corruption': {'name': self.lm.tr('anti_corruption', 'Anti-Korupsiyon'), 'max_score': 15},
                    'transparency': {'name': self.lm.tr('transparency', 'Şeffaflık ve Raporlama'), 'max_score': 10},
                    'compliance': {'name': self.lm.tr('compliance', 'Mevzuata Uyum'), 'max_score': 10}
                }
            },
            'quality': {
                'name': self.lm.tr('quality_and_reliability', 'Kalite ve Güvenilirlik'),
                'weight': 0.20,
                'criteria': {
                    'iso9001': {'name': self.lm.tr('iso9001', 'ISO 9001 Sertifikası'), 'max_score': 15},
                    'on_time_delivery': {'name': self.lm.tr('on_time_delivery', 'Zamanında Teslimat'), 'max_score': 15},
                    'defect_rate': {'name': self.lm.tr('defect_rate', 'Düşük Hata Oranı'), 'max_score': 10},
                    'quality_systems': {'name': self.lm.tr('quality_systems', 'Kalite Yönetim Sistemi'), 'max_score': 10}
                }
            }
        }

        # Risk Seviyeleri
        self.RISK_LEVELS = {
            'low': {'threshold': 80, 'color': '#27ae60', 'label': self.lm.tr('low_risk', 'Düşük Risk')},
            'medium': {'threshold': 60, 'color': '#f39c12', 'label': self.lm.tr('medium_risk', 'Orta Risk')},
            'high': {'threshold': 40, 'color': '#e67e22', 'label': self.lm.tr('high_risk', 'Yüksek Risk')},
            'critical': {'threshold': 0, 'color': '#e74c3c', 'label': self.lm.tr('critical_risk', 'Kritik Risk')}
        }

    def calculate_category_score(self, responses: Dict, category: str) -> float:
        """
        Kategori skoru hesapla
        
        Args:
            responses: {'iso14001': 20, 'carbon_footprint': 10, ...}
            category: 'environmental', 'social', 'governance', 'quality'
        
        Returns:
            0-100 arası kategori skoru
        """
        if category not in self.ASSESSMENT_CATEGORIES:
            return 0.0

        category_data = self.ASSESSMENT_CATEGORIES[category]
        criteria = category_data['criteria']

        total_score = 0
        max_possible = sum(c['max_score'] for c in criteria.values())

        for criterion_key, criterion_data in criteria.items():
            score = responses.get(criterion_key, 0)
            # Max score kontrolü
            score = min(score, criterion_data['max_score'])
            total_score += score

        # 0-100 skalasına normalize et
        normalized_score = (total_score / max_possible) * 100 if max_possible > 0 else 0

        return round(normalized_score, 2)

    def calculate_total_score(self, category_scores: Dict) -> float:
        """
        Toplam tedarikçi skoru (ağırlıklı ortalama)
        
        Args:
            category_scores: {
                'environmental': 85.5,
                'social': 90.0,
                'governance': 75.0,
                'quality': 88.0
            }
        
        Returns:
            0-100 arası toplam skor
        """
        total = 0.0

        for category, score in category_scores.items():
            if category in self.ASSESSMENT_CATEGORIES:
                weight = self.ASSESSMENT_CATEGORIES[category]['weight']
                total += score * weight

        return round(total, 2)

    def determine_risk_level(self, total_score: float) -> Dict:
        """
        Risk seviyesi belirle
        
        Returns:
            {
                'level': 'low',
                'label': 'Düşük Risk',
                'color': '#27ae60',
                'score': 85.5
            }
        """
        for level, data in self.RISK_LEVELS.items():
            if total_score >= data['threshold']:
                return {
                    'level': level,
                    'label': data['label'],
                    'color': data['color'],
                    'score': total_score
                }

        # Fallback (should never reach here)
        return {
            'level': 'critical',
            'label': self.lm.tr('critical_risk', 'Kritik Risk'),
            'color': '#e74c3c',
            'score': total_score
        }

    def assess_supplier_risk(self, risk_data: Dict) -> Dict:
        """Tedarikçi risk analizi"""
        risk_scores = {
            'country_risk': {'low': 1, 'medium': 2, 'high': 3}.get(risk_data.get('country_risk', 'medium'), 2),
            'financial_stability': {'low': 3, 'medium': 2, 'high': 1}.get(risk_data.get('financial_stability', 'medium'), 2),
            'environmental_compliance': {'low': 3, 'medium': 2, 'high': 1}.get(risk_data.get('environmental_compliance', 'medium'), 2),
            'labor_practices': {'low': 3, 'medium': 2, 'high': 1}.get(risk_data.get('labor_practices', 'medium'), 2),
            'data_security': {'low': 3, 'medium': 2, 'high': 1}.get(risk_data.get('data_security', 'medium'), 2)
        }

        total_score = sum(risk_scores.values())
        avg_score = total_score / len(risk_scores)

        if avg_score <= 1.5:
            risk_level = 'low'
        elif avg_score <= 2.5:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        key_risks = []
        for risk_type, score in risk_scores.items():
            if score >= 3:
                key_risks.append(risk_type)

        return {
            'overall_risk': risk_level,
            'risk_score': round(avg_score, 2),
            'key_risks': key_risks,
            'risk_breakdown': risk_scores
        }

    def map_sdg_contributions(self, performance_data: Dict) -> Dict:
        """SDG katkılarını haritalandır"""
        sdg_mappings = {
            'SDG 6': ['water_management', 'waste_reduction'],
            'SDG 7': ['renewable_energy', 'energy_efficiency'],
            'SDG 8': ['decent_work', 'employee_development'],
            'SDG 9': ['innovation', 'infrastructure'],
            'SDG 12': ['responsible_consumption', 'waste_reduction'],
            'SDG 13': ['climate_action', 'carbon_reduction'],
            'SDG 15': ['biodiversity', 'ecosystem_protection']
        }

        contributing_sdgs = []
        initiatives = performance_data.get('sustainability_initiatives', [])

        for sdg, keywords in sdg_mappings.items():
            for initiative in initiatives:
                if any(keyword in initiative for keyword in keywords):
                    if sdg not in contributing_sdgs:
                        contributing_sdgs.append(sdg)

        # Skorlara göre ek SDG'ler
        env_score = performance_data.get('environmental_score', 0)
        social_score = performance_data.get('social_score', 0)

        if env_score >= 80 and 'SDG 13' not in contributing_sdgs:
            contributing_sdgs.append('SDG 13')
        if social_score >= 80 and 'SDG 8' not in contributing_sdgs:
            contributing_sdgs.append('SDG 8')

        return {
            'contributing_sdgs': contributing_sdgs,
            'primary_sdg': contributing_sdgs[0] if contributing_sdgs else None,
            'sdg_alignment_score': len(contributing_sdgs) * 10,
            'sustainability_initiatives': initiatives
        }

    def generate_assessment_report(self, supplier_data: Dict,
                                  category_scores: Dict,
                                  responses: Dict) -> Dict:
        """
        Değerlendirme raporu oluştur
        
        Returns:
            Detaylı değerlendirme raporu
        """
        total_score = self.calculate_total_score(category_scores)
        risk_assessment = self.determine_risk_level(total_score)

        # Strengths and weaknesses
        strengths = []
        weaknesses = []

        for category, score in category_scores.items():
            if score >= 80:
                strengths.append({
                    'category': self.ASSESSMENT_CATEGORIES[category]['name'],
                    'score': score
                })
            elif score < 60:
                weaknesses.append({
                    'category': self.ASSESSMENT_CATEGORIES[category]['name'],
                    'score': score
                })

        return {
            'supplier_name': supplier_data.get('name', 'Unknown'),
            'assessment_date': datetime.now().isoformat(),
            'total_score': total_score,
            'risk_level': risk_assessment['level'],
            'risk_label': risk_assessment['label'],
            'category_scores': category_scores,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendation': self._generate_recommendation(total_score),
            'next_assessment_date': self._calculate_next_assessment(total_score)
        }

    def _generate_recommendation(self, total_score: float) -> str:
        """Öneri oluştur"""
        if total_score >= 80:
            return self.lm.tr('rec_excellent', "Mükemmel tedarikçi. İlişkiyi sürdürün ve stratejik ortaklık düşünün.")
        elif total_score >= 60:
            return self.lm.tr('rec_good', "İyi performans. Zayıf alanlarda iyileştirme planı yapın.")
        elif total_score >= 40:
            return self.lm.tr('rec_poor', "Yetersiz performans. Acil iyileştirme gerekli veya alternatif tedarikçi arayın.")
        else:
            return self.lm.tr('rec_critical', "Kritik seviye. İlişkiyi sonlandırmayı veya kapsamlı iyileştirme planı yapmayı düşünün.")

    def _calculate_next_assessment(self, total_score: float) -> str:
        """Sonraki değerlendirme tarihini hesapla"""
        from datetime import timedelta

        # Düşük riskli: yıllık, yüksek riskli: 3 ayda bir
        if total_score >= 80:
            months = 12
        elif total_score >= 60:
            months = 6
        else:
            months = 3

        next_date = datetime.now() + timedelta(days=30 * months)
        return next_date.strftime('%Y-%m-%d')

    def calculate_spend_concentration(self, supplier_spend: float,
                                     total_spend: float) -> Dict:
        """
        Tedarikçi harcama konsantrasyonu analizi
        
        Returns:
            {
                'spend_percentage': float,
                'concentration_level': str,  # low, medium, high
                'risk_note': str
            }
        """
        if total_spend == 0:
            return {'spend_percentage': 0, 'concentration_level': 'unknown', 'risk_note': self.lm.tr('total_spend_zero', 'Toplam harcama 0')}

        percentage = (supplier_spend / total_spend) * 100

        if percentage < 10:
            level = 'low'
            note = self.lm.tr('low_dependency', 'Düşük bağımlılık')
        elif percentage < 25:
            level = 'medium'
            note = self.lm.tr('medium_dependency', 'Orta seviye bağımlılık')
        else:
            level = 'high'
            note = self.lm.tr('high_dependency', 'Yüksek bağımlılık - alternatif tedarikçi geliştirin')

        return {
            'spend_percentage': round(percentage, 2),
            'concentration_level': level,
            'risk_note': note
        }

