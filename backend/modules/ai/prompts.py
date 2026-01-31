# -*- coding: utf-8 -*-
"""
AI Prompt Templates
"""

PROMPTS = {
    "tr": {
        "sdg": """
Aşağıdaki Sürdürülebilirlik Kalkınma Amaçları (SDG) verilerini analiz et ve bir yönetici özeti oluştur.
Her bir hedef (SDG) için performansı değerlendir, güçlü yönleri ve iyileştirme alanlarını vurgula.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Yönetici Özeti
2. Hedef Bazlı Performans Analizi
3. İyileştirme Önerileri
""",
        "gri": """
Aşağıdaki Global Reporting Initiative (GRI) verilerini analiz et ve standartlara uygun bir özet rapor oluştur.
Ekonomik, Çevresel ve Sosyal kategorilerdeki performansı değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Genel Bakış
2. Kategori Bazlı Değerlendirme (Ekonomik, Çevresel, Sosyal)
3. GRI Standartlarına Uyum Durumu
""",
        "unified": """
Aşağıdaki birleştirilmiş sürdürülebilirlik verilerini (Unified KPI Snapshot) analiz et.
Bu veri seti SDG, GRI, CSRD, Karbon Ayak İzi ve diğer modüllerden gelen verileri içermektedir.

Veri:
{data}

Lütfen kapsamlı bir sürdürülebilirlik raporu özeti oluştur. Rapor şu bölümleri içermelidir:
1. Yönetici Özeti: Genel sürdürülebilirlik performansı hakkında kısa bir özet.
2. Temel Performans Göstergeleri (KPI) Analizi: Öne çıkan metrikler ve trendler.
3. Modüller Arası Entegrasyon: Farklı standartlar (SDG, GRI, vb.) arasındaki uyum ve tutarlılık.
4. Stratejik Öneriler: Gelecek dönem için aksiyon önerileri.

Not: Sayısal verileri metin içinde kullanarak analizi destekle.
""",
        "general": """
Aşağıdaki sürdürülebilirlik verilerini özetle ve temel çıkarımları maddeler halinde listele.

Veri:
{data}

Çıktı Formatı:
- Özet Paragraf
- Temel Bulgular (Madde işaretleri)
- Öneriler
"""
    },
    "en": {
        "sdg": """
Analyze the following Sustainable Development Goals (SDG) data and create an executive summary.
Evaluate performance for each goal (SDG), highlighting strengths and areas for improvement.

Data:
{data}

Please structure the report under the following headings:
1. Executive Summary
2. Goal-Based Performance Analysis
3. Improvement Recommendations
""",
        "gri": """
Analyze the following Global Reporting Initiative (GRI) data and create a summary report compliant with standards.
Evaluate performance in Economic, Environmental, and Social categories.

Data:
{data}

Please structure the report under the following headings:
1. Overview
2. Category-Based Assessment (Economic, Environmental, Social)
3. GRI Standards Compliance Status
""",
        "unified": """
Analyze the following unified sustainability data (Unified KPI Snapshot).
This dataset contains data from SDG, GRI, CSRD, Carbon Footprint, and other modules.

Data:
{data}

Please create a comprehensive sustainability report summary. The report should include the following sections:
1. Executive Summary: A brief summary of overall sustainability performance.
2. Key Performance Indicators (KPI) Analysis: Prominent metrics and trends.
3. Cross-Module Integration: Alignment and consistency between different standards (SDG, GRI, etc.).
4. Strategic Recommendations: Action proposals for the upcoming period.

Note: Support the analysis by using numerical data within the text.
""",
        "general": """
Summarize the following sustainability data and list key takeaways in bullet points.

Data:
{data}

Output Format:
- Summary Paragraph
- Key Findings (Bullet points)
- Recommendations
"""
    }
}

def get_prompt(report_type: str, data: str, language: str = "tr") -> str:
    """Belirtilen rapor türü ve dil için prompt oluşturur"""
    lang_prompts = PROMPTS.get(language, PROMPTS["tr"])
    # If report_type not found in requested language, fallback to 'general' in that language
    template = lang_prompts.get(report_type, lang_prompts.get("general"))
    # If still None (unlikely), try 'tr' as fallback
    if template is None:
        template = PROMPTS["tr"]["general"]
        
    return template.format(data=data)
