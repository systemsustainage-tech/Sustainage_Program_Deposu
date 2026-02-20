#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Manager - OpenAI entegrasyonu ve rapor olusturma
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from modules.reporting.advanced_report_manager import AdvancedReportManager
from config.database import DB_PATH


class AIManager:
    """AI islemlerini yoneten sinif"""

    def __init__(self, db_path: str = DB_PATH):
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self.base_dir = os.path.dirname(os.path.dirname(db_path))

        # OpenAI API key
        self.api_key = self._load_api_key()
        self.client = None

        if self.api_key:
            self._init_openai()

    def _load_api_key(self) -> Optional[str]:
        """API key yukle (.env dosyasindan)"""
        env_file = os.path.join(self.base_dir, '.env')

        if os.path.exists(env_file):
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('OPENAI_API_KEY='):
                            return line.split('=', 1)[1].strip()
            except Exception as e:
                logging.error(f"[HATA] API key okunamadi: {e}")

        return None

    def _init_openai(self):
        """OpenAI client baslatma"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logging.info("[OK] OpenAI client baslatildi")
        except ImportError:
            logging.info("[UYARI] openai paketi yuklu degil. pip install openai")
            self.client = None
        except Exception as e:
            logging.error(f"[HATA] OpenAI client baslatilamadi: {e}")
            self.client = None

    def is_available(self) -> bool:
        """AI ozellikleri kullanilabilir mi?"""
        return self.client is not None

    def generate_summary(self, data: Dict, report_type: str = "genel") -> Optional[str]:
        """Veri ozetleme"""
        if not self.is_available():
            return "AI servisi kullanılamıyor. Lutfen API key ekleyin."

        try:
            # Prompt olustur
            prompt = self._create_prompt(data, report_type)

            # OpenAI API cagir
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen surdurulebilirlik raporlama uzmanisin."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"AI hatasi: {str(e)}"

    def _create_prompt(self, data: Dict, report_type: str) -> str:
        """Prompt olustur"""
        base_instruction = """
Lütfen aşağıdaki verileri profesyonel bir sürdürülebilirlik raporu formatında özetle.
Yanıtta şu başlıklara yer ver:
1. **Genel Durum Özeti**: Verilerin genel eğilimi.
2. **Öne Çıkan Metrikler**: En yüksek/düşük değerler ve anlamları.
3. **Kapsam ve Etki**: Bu verilerin çevresel/sosyal etkisi.

Dil: Türkçe, Resmi ve Kurumsal.
"""
        if report_type == "sdg":
            return f"""
{base_instruction}
Veriler (SDG Odaklı):
{json.dumps(data, indent=2, ensure_ascii=False)}
"""
        elif report_type == "gri":
            return f"""
{base_instruction}
Veriler (GRI Standartları):
{json.dumps(data, indent=2, ensure_ascii=False)}
"""
        else:
            return f"""
{base_instruction}
Veriler:
{json.dumps(data, indent=2, ensure_ascii=False)}
"""

    def analyze_performance(self, metrics: List[Dict]) -> Optional[str]:
        """Performans analizi"""
        if not self.is_available():
            return "AI servisi kullanılamıyor."

        try:
            prompt = f"""
Aşağıdaki performans metriklerini detaylı olarak analiz et:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

Lütfen şu yapıda bir analiz sun:
1. **Güçlü Yönler**: Başarılı olunan alanlar.
2. **Gelişim Alanları**: İyileştirilmesi gereken noktalar.
3. **Stratejik Öneriler**: Gelecek dönem için somut aksiyon önerileri.
4. **Trend Analizi**: Varsa artış/azalış eğilimlerinin yorumlanması.

Dil: Türkçe, Profesyonel.
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen kıdemli bir sürdürülebilirlik analisti ve strateji danışmanısın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"AI hatasi: {str(e)}"

    def get_recommendations(self, context: str) -> Optional[str]:
        """Akilli oneriler"""
        if not self.is_available():
            return "AI servisi kullanılamıyor."

        try:
            prompt = f"""
Asagidaki surdurulebilirlik durumu icin oneriler sun:
{context}

Lutfen somut ve uygulanabilir oneriler ver.
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen surdurulebilirlik danismanisin."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"AI hatasi: {str(e)}"

    def save_report(self, report_content: str, report_name: str) -> bool:
        """AI raporunu kaydet"""
        try:
            reports_dir = os.path.join(self.base_dir, "reports", "ai")
            os.makedirs(reports_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_name}_{timestamp}.txt"
            filepath = os.path.join(reports_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            mgr = AdvancedReportManager(self.db_path)
            reg_id = mgr.register_existing_file(
                company_id=1,
                module_code="ai",
                report_name=report_name,
                report_type="txt",
                file_path=filepath,
                reporting_period=str(datetime.now().year),
                tags=["ai"],
                description="AI tarafından üretilmiş özet"
            )
            if reg_id:
                logging.info(f"[OK] AI raporu kaydedildi: {filepath}")
                return True
            return False
        except Exception as e:
            logging.error(f"[HATA] AI raporu kaydedilemedi: {e}")
            return False

