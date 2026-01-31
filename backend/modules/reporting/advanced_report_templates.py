#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Rapor Şablonları
4 farklı rapor türü: Özet, Standart, Detaylı, Tam
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class AdvancedReportTemplates:
    """Gelişmiş rapor şablonları yöneticisi"""

    # Rapor türleri
    REPORT_TYPES = {
        'summary': {
            'name': 'Özet Rapor',
            'pages': '5-10',
            'sections': ['Executive Summary', 'Key Metrics', 'Highlights'],
            'detail_level': 'low',
            'graphs': 'minimal'
        },
        'standard': {
            'name': 'Standart Rapor',
            'pages': '20-30',
            'sections': ['Executive Summary', 'Methodology', 'Data', 'Analysis', 'Recommendations'],
            'detail_level': 'medium',
            'graphs': 'moderate'
        },
        'detailed': {
            'name': 'Detaylı Rapor',
            'pages': '40-60',
            'sections': ['Full Methodology', 'Comprehensive Data', 'In-depth Analysis', 'Appendices'],
            'detail_level': 'high',
            'graphs': 'comprehensive'
        },
        'comprehensive': {
            'name': 'Tam Kapsamlı Rapor',
            'pages': '80-120',
            'sections': ['All Sections', 'All Data Tables', 'All Analysis', 'All Appendices'],
            'detail_level': 'maximum',
            'graphs': 'all'
        }
    }

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get_template_structure(self, report_type: str, standard: str) -> Dict:
        """
        Rapor şablonu yapısını getir
        
        Args:
            report_type: 'summary', 'standard', 'detailed', 'comprehensive'
            standard: 'sdg', 'gri', 'tsrs', 'esg'
        
        Returns:
            Dict: Şablon yapısı
        """
        if report_type not in self.REPORT_TYPES:
            report_type = 'standard'

        template_info = self.REPORT_TYPES[report_type]

        # Standart bazlı bölümler
        if standard == 'sdg':
            sections = self._get_sdg_sections(report_type)
        elif standard == 'gri':
            sections = self._get_gri_sections(report_type)
        elif standard == 'tsrs':
            sections = self._get_tsrs_sections(report_type)
        elif standard == 'esg':
            sections = self._get_esg_sections(report_type)
        else:
            sections = []

        return {
            'type': report_type,
            'name': template_info['name'],
            'standard': standard.upper(),
            'estimated_pages': template_info['pages'],
            'detail_level': template_info['detail_level'],
            'sections': sections
        }

    def _get_sdg_sections(self, report_type: str) -> List[Dict]:
        """SDG rapor bölümleri"""
        base_sections = [
            {'id': 'cover', 'title': 'Kapak Sayfası', 'required': True},
            {'id': 'exec_summary', 'title': 'Yönetici Özeti', 'required': True},
            {'id': 'intro', 'title': 'Giriş ve Metodoloji', 'required': True},
        ]

        if report_type == 'summary':
            return base_sections + [
                {'id': 'key_sdgs', 'title': 'Öncelikli SDG Hedefleri (Top 5)', 'required': True},
                {'id': 'metrics', 'title': 'Özet Metrikler', 'required': True},
                {'id': 'conclusion', 'title': 'Sonuç ve Gelecek Planları', 'required': True}
            ]

        elif report_type == 'standard':
            return base_sections + [
                {'id': 'sdg_overview', 'title': 'SDG Genel Bakış', 'required': True},
                {'id': 'sdg_targets', 'title': 'Hedef ve Alt Hedefler', 'required': True},
                {'id': 'progress', 'title': 'İlerleme Analizi', 'required': True},
                {'id': 'indicators', 'title': 'Gösterge Bazlı Sonuçlar', 'required': True},
                {'id': 'graphs', 'title': 'Grafik ve Görseller', 'required': False},
                {'id': 'conclusion', 'title': 'Sonuç ve Öneriler', 'required': True}
            ]

        elif report_type == 'detailed':
            return base_sections + [
                {'id': 'context', 'title': 'Bağlam ve Arka Plan', 'required': True},
                {'id': 'all_sdgs', 'title': 'Tüm 17 SDG Analizi', 'required': True},
                {'id': 'methodology_detailed', 'title': 'Detaylı Metodoloji', 'required': True},
                {'id': 'data_collection', 'title': 'Veri Toplama Süreci', 'required': True},
                {'id': 'validation', 'title': 'Veri Doğrulama ve Kalite', 'required': True},
                {'id': 'analysis', 'title': 'Kapsamlı Analiz', 'required': True},
                {'id': 'comparisons', 'title': 'Yıllık Karşılaştırmalar', 'required': True},
                {'id': 'trends', 'title': 'Trend Analizleri', 'required': True},
                {'id': 'appendices', 'title': 'Ekler ve Veri Tabloları', 'required': True}
            ]

        else:  # comprehensive
            return base_sections + [
                {'id': 'full_context', 'title': 'Tam Bağlam ve Metodoloji', 'required': True},
                {'id': 'all_17_sdgs', 'title': '17 SDG Detaylı Analiz', 'required': True},
                {'id': 'all_169_targets', 'title': '169 Alt Hedef Değerlendirmesi', 'required': True},
                {'id': 'all_indicators', 'title': 'Tüm Göstergeler', 'required': True},
                {'id': 'data_tables', 'title': 'Tüm Veri Tabloları', 'required': True},
                {'id': 'graphs_all', 'title': 'Tüm Grafik ve Görseller', 'required': True},
                {'id': 'stakeholder', 'title': 'Paydaş Analizi', 'required': True},
                {'id': 'comparisons_full', 'title': 'Tam Karşılaştırmalar', 'required': True},
                {'id': 'case_studies', 'title': 'Örnek Çalışmalar', 'required': True},
                {'id': 'appendices_full', 'title': 'Tam Ekler', 'required': True}
            ]

    def _get_gri_sections(self, report_type: str) -> List[Dict]:
        """GRI rapor bölümleri"""
        base_sections = [
            {'id': 'cover', 'title': 'Kapak Sayfası', 'required': True},
            {'id': 'message', 'title': 'Yönetici Mesajı', 'required': True},
            {'id': 'about', 'title': 'Kurum Hakkında (GRI 2)', 'required': True},
        ]

        if report_type == 'summary':
            return base_sections + [
                {'id': 'material_topics', 'title': 'Önemli Konular (Top 5)', 'required': True},
                {'id': 'key_metrics', 'title': 'Ana Metrikler', 'required': True},
                {'id': 'gri_index_short', 'title': 'GRI İçerik İndeksi (Özet)', 'required': True}
            ]

        elif report_type == 'standard':
            return base_sections + [
                {'id': 'gri_102', 'title': 'GRI 102: Genel Açıklamalar', 'required': True},
                {'id': 'material_topics_full', 'title': 'GRI 3: Önemli Konular', 'required': True},
                {'id': 'economic', 'title': 'Ekonomik Performans', 'required': True},
                {'id': 'environmental', 'title': 'Çevresel Performans', 'required': True},
                {'id': 'social', 'title': 'Sosyal Performans', 'required': True},
                {'id': 'gri_index', 'title': 'GRI İçerik İndeksi', 'required': True}
            ]

        elif report_type == 'detailed':
            return base_sections + [
                {'id': 'gri_foundation', 'title': 'GRI 1: Foundation', 'required': True},
                {'id': 'gri_102_full', 'title': 'GRI 2: Tam Açıklamalar', 'required': True},
                {'id': 'gri_103_full', 'title': 'GRI 3: Detaylı Materialite', 'required': True},
                {'id': 'economic_full', 'title': 'Ekonomik Standartlar (200 Serisi)', 'required': True},
                {'id': 'environmental_full', 'title': 'Çevresel Standartlar (300 Serisi)', 'required': True},
                {'id': 'social_full', 'title': 'Sosyal Standartlar (400 Serisi)', 'required': True},
                {'id': 'sector_specific', 'title': 'Sektörel Standartlar', 'required': False},
                {'id': 'data_tables', 'title': 'Veri Tabloları ve Göstergeler', 'required': True},
                {'id': 'gri_index_full', 'title': 'Tam GRI İçerik İndeksi', 'required': True}
            ]

        else:  # comprehensive
            return base_sections + [
                {'id': 'gri_all_standards', 'title': 'Tüm GRI Standartları', 'required': True},
                {'id': 'all_disclosures', 'title': 'Tüm Açıklamalar (102-419)', 'required': True},
                {'id': 'full_data', 'title': 'Tam Veri Setleri', 'required': True},
                {'id': 'assurance', 'title': 'Dış Güvence Raporu', 'required': False},
                {'id': 'appendices_full', 'title': 'Tam Ekler', 'required': True}
            ]

    def _get_tsrs_sections(self, report_type: str) -> List[Dict]:
        """TSRS rapor bölümleri"""
        base_sections = [
            {'id': 'cover', 'title': 'Kapak', 'required': True},
            {'id': 'message', 'title': 'Genel Müdür Mesajı', 'required': True},
            {'id': 'company', 'title': 'Kurum Tanıtımı', 'required': True},
        ]

        if report_type in ['summary', 'standard']:
            return base_sections + [
                {'id': 'general', 'title': 'Genel Bilgiler', 'required': True},
                {'id': 'environment', 'title': 'Çevre', 'required': True},
                {'id': 'social', 'title': 'Sosyal', 'required': True},
                {'id': 'governance', 'title': 'Yönetişim', 'required': True},
                {'id': 'climate', 'title': 'İklim Değişikliği', 'required': True}
            ]
        else:
            return base_sections + [
                {'id': 'full_general', 'title': 'Genel Bilgiler (Detaylı)', 'required': True},
                {'id': 'full_environment', 'title': 'Çevre (Tüm Alt Başlıklar)', 'required': True},
                {'id': 'full_social', 'title': 'Sosyal (Tüm Alt Başlıklar)', 'required': True},
                {'id': 'full_governance', 'title': 'Yönetişim (Tüm Alt Başlıklar)', 'required': True},
                {'id': 'full_climate', 'title': 'İklim (TCFD Uyumlu)', 'required': True},
                {'id': 'double_materiality', 'title': 'Çift Önemlendirme Analizi', 'required': True},
                {'id': 'esrs_compliance', 'title': 'ESRS Uyumluluk Matrisi', 'required': True}
            ]

    def _get_esg_sections(self, report_type: str) -> List[Dict]:
        """ESG rapor bölümleri"""
        base_sections = [
            {'id': 'cover', 'title': 'Kapak', 'required': True},
            {'id': 'overview', 'title': 'ESG Genel Bakış', 'required': True},
        ]

        return base_sections + [
            {'id': 'environmental', 'title': 'Çevresel (E) Performans', 'required': True},
            {'id': 'social', 'title': 'Sosyal (S) Performans', 'required': True},
            {'id': 'governance', 'title': 'Yönetişim (G) Performans', 'required': True},
            {'id': 'esg_score', 'title': 'ESG Skorları ve Benchmark', 'required': True}
        ]

    def generate_report_from_template(self, company_id: int,
                                     report_type: str, standard: str,
                                     year: int, language: str = 'tr',
                                     brand_config: Optional[Dict] = None) -> str:
        """
        Şablondan rapor oluştur
        
        Args:
            company_id: Şirket ID
            report_type: Rapor türü
            standard: Standart (sdg/gri/tsrs/esg)
            year: Yıl
            language: Dil (tr/en)
            brand_config: Marka ayarları
        
        Returns:
            str: Oluşturulan rapor içeriği (Markdown)
        """
        template = self.get_template_structure(report_type, standard)

        # Başlık
        report = f"""# {template['name'].upper()} - {standard.upper()}
## {year} Sürdürülebilirlik Raporu

**Rapor Türü:** {template['name']}  
**Standart:** {template['standard']}  
**Dönem:** {year}  
**Oluşturma Tarihi:** {datetime.now().strftime('%d.%m.%Y')}  
**Tahmini Sayfa Sayısı:** {template['estimated_pages']}

---

"""

        # Bölümleri ekle
        for section in template['sections']:
            report += f"\n## {section['title']}\n\n"

            # Bölüm içeriği (placeholder)
            if section['id'] == 'exec_summary':
                report += self._generate_executive_summary(company_id, year, standard)
            elif section['id'] == 'material_topics':
                report += self._generate_material_topics(company_id, year)
            elif section['id'] == 'key_metrics':
                report += self._generate_key_metrics(company_id, year, standard)
            else:
                report += f"*{section['title']} bölümü - Veri toplama ve analiz sonuçları burada görüntülenecek*\n\n"

        # Footer
        report += f"\n---\n**Rapor Sonu** - {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"

        return report

    def _generate_executive_summary(self, company_id: int, year: int, standard: str) -> str:
        """Yönetici özeti oluştur"""
        return f"""
### Sürdürülebilirlik Performansımız

{year} yılında {standard.upper()} standartlarına göre sürdürülebilirlik performansımızı değerlendirdik.

**Ana Başarılar:**
-  Karbon emisyonlarında azaltma
-  Çalışan memnuniyetinde artış
-  Sürdürülebilir tedarik zinciri iyileştirmeleri
-  Sosyal sorumluluk projelerinde büyüme

**Gelecek Taahhütlerimiz:**
-  Net sıfır emisyon hedefi
-  %100 yenilenebilir enerji kullanımı
-  Çalışan çeşitliliğinde artış
-  Döngüsel ekonomi uygulamaları

"""

    def _generate_material_topics(self, company_id: int, year: int) -> str:
        """Önemli konular (materialite) oluştur"""
        return """
### Öncelikli Sürdürülebilirlik Konuları

1. **İklim Değişikliği ve Emisyonlar** - Çok Yüksek Öncelik
2. **Enerji Yönetimi** - Yüksek Öncelik  
3. **Çalışan Sağlığı ve Güvenliği** - Yüksek Öncelik
4. **Atık Yönetimi** - Orta Öncelik
5. **Toplum İlişkileri** - Orta Öncelik

*Materialite analizi paydaş görüşleri ve işletme etkileri dikkate alınarak gerçekleştirilmiştir.*

"""

    def _fetch_yearly_data(self, company_id: int, year: int) -> Dict:
        """Yıllık verileri veritabanından çek"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        data = {
            'ghg_total': 0.0, 'energy_total': 0.0, 'water_total': 0.0, 'waste_total': 0.0,
            'total_employees': 0, 'female_ratio': 0.0, 'training_hours_per_employee': 0.0,
            'accident_rate': 0.0, 'board_diversity': 0.0, 'ethics_training_ratio': 0.0,
            'whistleblowing_count': 0
        }
        
        try:
            # GHG
            cursor.execute("SELECT SUM(total_emissions) FROM scope1_emissions WHERE company_id=? AND year=?", (company_id, year))
            s1 = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(total_emissions) FROM scope2_emissions WHERE company_id=? AND year=?", (company_id, year))
            s2 = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(total_emissions) FROM scope3_emissions WHERE company_id=? AND year=?", (company_id, year))
            s3 = cursor.fetchone()[0] or 0
            data['ghg_total'] = s1 + s2 + s3
            
            # Energy
            cursor.execute("SELECT SUM(consumption_amount) FROM energy_consumption WHERE company_id=? AND year=?", (company_id, year))
            data['energy_total'] = cursor.fetchone()[0] or 0
            
            # Water
            cursor.execute("SELECT SUM(consumption_amount) FROM water_consumption WHERE company_id=? AND year=?", (company_id, year))
            data['water_total'] = cursor.fetchone()[0] or 0
            
            # Waste
            cursor.execute("SELECT SUM(waste_amount) FROM waste_generation WHERE company_id=? AND year=?", (company_id, year))
            data['waste_total'] = cursor.fetchone()[0] or 0
            
            # HR - Employees
            cursor.execute("SELECT AVG(total_employees) FROM employee_statistics WHERE company_id=? AND year=?", (company_id, year))
            val = cursor.fetchone()[0]
            data['total_employees'] = int(val) if val else 0
            
            # HR - Female Ratio
            cursor.execute("SELECT AVG(percentage) FROM employee_demographics WHERE company_id=? AND year=? AND (gender='Female' OR gender='Kadın')", (company_id, year))
            val = cursor.fetchone()[0]
            data['female_ratio'] = val if val else 0
            
            # HR - Training
            if data['total_employees'] > 0:
                cursor.execute("SELECT SUM(total_hours) FROM employee_development WHERE company_id=? AND year=?", (company_id, year))
                total_hours = cursor.fetchone()[0] or 0
                data['training_hours_per_employee'] = total_hours / data['total_employees']
            
            # 4. SAFETY DATA
            # Kaza orani ve kayip gunler
            cursor.execute("""
                SELECT COUNT(*), SUM(lost_work_days)
                FROM safety_incidents
                WHERE company_id = ? AND strftime('%Y', incident_date) = ?
            """, (company_id, str(year)))
            safety_row = cursor.fetchone()
            total_incidents = safety_row[0] if safety_row and safety_row[0] else 0
            total_lost_days = safety_row[1] if safety_row and safety_row[1] else 0
            
            # Calisan sayisini al (Safety oranlari icin)
            cursor.execute("SELECT COUNT(*) FROM employees WHERE company_id = ? AND status = 'Active'", (company_id,))
            emp_row = cursor.fetchone()
            total_employees = emp_row[0] if emp_row and emp_row[0] > 0 else 1 # Bolme hatasini onle

            # accident_rate olarak kaydet (key uyumu icin)
            data['accident_rate'] = round((total_incidents / total_employees) * 100, 2)
            data['lost_time_injury_freq'] = round(total_lost_days, 2) # Simdilik toplam kayip gun olarak

            # 5. GOVERNANCE DATA
            # YK Cesitliligi (Kadin uye orani)
            cursor.execute("""
                SELECT 
                    COUNT(*),
                    SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END)
                FROM board_members
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))
            board_row = cursor.fetchone()
            total_board = board_row[0] if board_row and board_row[0] else 0
            female_board = board_row[1] if board_row and board_row[1] else 0
            
            # board_diversity olarak kaydet (key uyumu icin)
            if total_board > 0:
                data['board_diversity'] = round((female_board / total_board) * 100, 2)
            else:
                data['board_diversity'] = 0.0

            # 6. ETHICS DATA
            # Etik Egitim Orani
            cursor.execute("""
                SELECT SUM(participant_count)
                FROM ethics_training
                WHERE company_id = ? AND strftime('%Y', training_date) = ?
            """, (company_id, str(year)))
            ethics_row = cursor.fetchone()
            total_ethics_participants = ethics_row[0] if ethics_row and ethics_row[0] else 0
            
            data['ethics_training_ratio'] = round((total_ethics_participants / total_employees) * 100, 2)

            # Whistleblowing Raporlari
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ethics_violations 
                WHERE company_id = ? AND strftime('%Y', violation_date) = ?
            """, (company_id, str(year)))
            whistle_row = cursor.fetchone()
            data['whistleblowing_count'] = whistle_row[0] if whistle_row and whistle_row[0] else 0

            # TODO: Diger metrikler icin veritabani sorgulari eklenecek
            # Simdilik eksik kalanlari 0 olarak birakiyoruz, ama [HESAPLANACAK] degil
            
        except Exception as e:
            print(f"Data fetch error: {e}")
        finally:
            conn.close()
            
        return data

    def _generate_key_metrics(self, company_id: int, year: int, standard: str) -> str:
        """Ana metrikler oluştur"""
        data = self._fetch_yearly_data(company_id, year)
        
        return f"""
### {year} Yılı Ana Metrikler

**Çevresel:**
- Toplam GHG Emisyonu: {data['ghg_total']:.2f} ton CO2e
- Enerji Tüketimi: {data['energy_total']:.2f} MWh
- Su Tüketimi: {data['water_total']:.2f} m³
- Atık Üretimi: {data['waste_total']:.2f} ton

**Sosyal:**
- Toplam Çalışan: {data['total_employees']}
- Kadın Çalışan Oranı: %{data['female_ratio']:.1f}
- Eğitim Saati/Kişi: {data['training_hours_per_employee']:.1f} saat
- İSG Kaza Oranı: {data['accident_rate']:.2f}

**Yönetişim:**
- Yönetim Kurulu Çeşitliliği: {data['board_diversity']:.1f}%
- Etik Eğitimi Alan Çalışan: {data['ethics_training_ratio']:.1f}%
- Whistleblowing Raporları: {data['whistleblowing_count']}

"""

    def create_default_templates(self, company_id: int) -> List[Dict]:
        """Varsayılan şablonları oluştur"""
        templates = []

        # Her standart için 4 rapor türü
        for standard in ['sdg', 'gri', 'tsrs', 'esg']:
            for report_type in ['summary', 'standard', 'detailed', 'comprehensive']:
                template_name = f"{standard.upper()} - {self.REPORT_TYPES[report_type]['name']}"
                template_content = json.dumps(
                    self.get_template_structure(report_type, standard),
                    ensure_ascii=False
                )

                templates.append({
                    'name': template_name,
                    'type': report_type,
                    'standard': standard,
                    'content': template_content
                })

        return templates

    def get_report_type_description(self, report_type: str) -> str:
        """Rapor türü açıklaması"""
        descriptions = {
            'summary': """
**Özet Rapor (5-10 sayfa)**
- Yönetici özeti ve ana bulgular
- En önemli 5-7 gösterge
- Minimal grafikler
- Hızlı genel bakış
- Yönetim sunumları için ideal
""",
            'standard': """
**Standart Rapor (20-30 sayfa)**
- Kapsamlı yönetici özeti
- Tüm önemli konular
- Detaylı göstergeler
- Orta seviye grafikler
- Yıllık raporlama için standart
""",
            'detailed': """
**Detaylı Rapor (40-60 sayfa)**
- Tam metodoloji açıklaması
- Tüm göstergeler detaylı
- Kapsamlı veri tabloları
- Çok sayıda grafik ve görsel
- Paydaş raporlaması için ideal
""",
            'comprehensive': """
**Tam Kapsamlı Rapor (80-120+ sayfa)**
- Tüm veri setleri
- Tüm göstergeler tam detay
- Tüm grafikler ve görseller
- Ekler ve appendiks'ler
- Dış güvence için hazır
- Regülatör raporlama
"""
        }

        return descriptions.get(report_type, "Açıklama bulunamadı")

