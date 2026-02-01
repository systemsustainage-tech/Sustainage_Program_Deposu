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
        "csrd": """
Aşağıdaki Kurumsal Sürdürülebilirlik Raporlama Direktifi (CSRD) verilerini analiz et.
Çifte önemlilik (double materiality) perspektifinden etkileri ve riskleri değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Yönetici Özeti
2. Önemlilik Analizi (Etki ve Finansal)
3. Sürdürülebilirlik Konuları ve Göstergeleri
4. AB Taksonomisi Uyumu
""",
        "esrs": """
Aşağıdaki Avrupa Sürdürülebilirlik Raporlama Standartları (ESRS) verilerini analiz et.
Çevresel (E), Sosyal (S) ve Yönetişim (G) başlıklarındaki uyumu değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. ESRS Genel Gereklilikler
2. Çevresel Performans (E1-E5)
3. Sosyal Performans (S1-S4)
4. Yönetişim (G1)
""",
        "tcfd": """
Aşağıdaki İklimle Bağlantılı Finansal Beyanlar (TCFD) verilerini analiz et.
İklim risklerinin finansal etkilerine odaklan.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Yönetişim
2. Strateji (Senaryo Analizi)
3. Risk Yönetimi
4. Metrikler ve Hedefler
""",
        "tnfd": """
Aşağıdaki Doğayla Bağlantılı Finansal Beyanlar (TNFD) verilerini analiz et.
Doğa kaynaklı riskleri ve fırsatları LEAP yaklaşımı çerçevesinde değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Doğa ile İlgili Bağımlılıklar ve Etkiler
2. Riskler ve Fırsatlar
3. Yönetişim ve Strateji
4. Metrikler ve Hedefler
""",
        "cdp": """
Aşağıdaki Carbon Disclosure Project (CDP) verilerini analiz et.
Karbon emisyonları, su güvenliği ve ormansızlaşma konularındaki performansı değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Emisyon Performansı ve Hedefler
2. Risk ve Fırsat Yönetimi
3. Değer Zinciri Etkileşimi
4. CDP Puanlama Potansiyeli
""",
        "cbam": """
Aşağıdaki Sınırda Karbon Düzenleme Mekanizması (CBAM) verilerini analiz et.
Gömülü emisyonlar ve potansiyel mali yükümlülükleri değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Toplam Gömülü Emisyonlar
2. Ürün Bazlı Emisyon Yoğunluğu
3. Mali Yükümlülük Tahmini
4. Azaltım Stratejileri
""",
        "lca": """
Aşağıdaki Yaşam Döngüsü Analizi (LCA) verilerini analiz et.
Ürün veya hizmetin beşikten mezara çevresel etkilerini değerlendir.

Veri:
{data}

Lütfen raporu aşağıdaki başlıklar altında yapılandır:
1. Etki Kategorileri Özeti (GWP, Su, Enerji)
2. Yaşam Döngüsü Aşamaları Analizi
3. Sıcak Noktalar (Hotspots)
4. İyileştirme Fırsatları
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
        "csrd": """
Analyze the following Corporate Sustainability Reporting Directive (CSRD) data.
Evaluate impacts and risks from a double materiality perspective.

Data:
{data}

Please structure the report under the following headings:
1. Executive Summary
2. Materiality Analysis (Impact and Financial)
3. Sustainability Topics and Indicators
4. EU Taxonomy Alignment
""",
        "esrs": """
Analyze the following European Sustainability Reporting Standards (ESRS) data.
Evaluate compliance in Environmental (E), Social (S), and Governance (G) topics.

Data:
{data}

Please structure the report under the following headings:
1. ESRS General Requirements
2. Environmental Performance (E1-E5)
3. Social Performance (S1-S4)
4. Governance (G1)
""",
        "tcfd": """
Analyze the following Task Force on Climate-related Financial Disclosures (TCFD) data.
Focus on the financial impacts of climate risks.

Data:
{data}

Please structure the report under the following headings:
1. Governance
2. Strategy (Scenario Analysis)
3. Risk Management
4. Metrics and Targets
""",
        "tnfd": """
Analyze the following Taskforce on Nature-related Financial Disclosures (TNFD) data.
Evaluate nature-related risks and opportunities using the LEAP approach.

Data:
{data}

Please structure the report under the following headings:
1. Nature-related Dependencies and Impacts
2. Risks and Opportunities
3. Governance and Strategy
4. Metrics and Targets
""",
        "cdp": """
Analyze the following Carbon Disclosure Project (CDP) data.
Evaluate performance in carbon emissions, water security, and deforestation.

Data:
{data}

Please structure the report under the following headings:
1. Emissions Performance and Targets
2. Risk and Opportunity Management
3. Value Chain Engagement
4. CDP Scoring Potential
""",
        "cbam": """
Analyze the following Carbon Border Adjustment Mechanism (CBAM) data.
Evaluate embedded emissions and potential financial liabilities.

Data:
{data}

Please structure the report under the following headings:
1. Total Embedded Emissions
2. Product-Based Emission Intensity
3. Financial Liability Estimate
4. Mitigation Strategies
""",
        "lca": """
Analyze the following Life Cycle Assessment (LCA) data.
Evaluate the cradle-to-grave environmental impacts of the product or service.

Data:
{data}

Please structure the report under the following headings:
1. Impact Categories Summary (GWP, Water, Energy)
2. Life Cycle Stages Analysis
3. Hotspots
4. Improvement Opportunities
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
    },
    "de": {
        "sdg": """Analysieren Sie die folgenden Daten zu den Zielen für nachhaltige Entwicklung (SDG) und erstellen Sie eine Zusammenfassung.
Daten:
{data}
Bitte strukturieren Sie den Bericht entsprechend.
""",
        "gri": """Analysieren Sie die folgenden GRI-Daten.
Daten:
{data}
""",
        "general": """Fassen Sie die folgenden Daten zusammen.
Daten:
{data}
"""
    },
    "fr": {
        "sdg": """Analysez les données ODD suivantes et créez un résumé.
Données:
{data}
Veuillez structurer le rapport en conséquence.
""",
        "gri": """Analysez les données GRI suivantes.
Données:
{data}
""",
        "general": """Résumez les données suivantes.
Données:
{data}
"""
    }
}

def get_prompt(template_name: str, data: str, lang: str = "tr") -> str:
    """
    Belirtilen dil ve şablon için prompt metnini döner ve veriyi yerleştirir.
    
    Args:
        template_name (str): Şablon adı (sdg, gri, vb.)
        data (str): Prompt içine gömülecek veri
        lang (str): Dil kodu (tr, en, de, fr)
    
    Returns:
        str: Hazır prompt metni
    """
    # Desteklenmeyen diller için İngilizce'ye düş
    if lang not in PROMPTS:
        lang = "en"
        
    lang_prompts = PROMPTS.get(lang, PROMPTS["en"])
    
    # Şablon yoksa general'e, o da yoksa boş stringe düş
    template = lang_prompts.get(template_name, lang_prompts.get("general", "{data}"))
    
    return template.format(data=data)
