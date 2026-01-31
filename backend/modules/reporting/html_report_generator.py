import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İnteraktif HTML Rapor Oluşturucu
Web tabanlı interaktif raporlar
"""

import base64
from datetime import datetime
from typing import Any, Dict, List, Optional


class HTMLReportGenerator:
    """HTML rapor oluşturucu"""

    def __init__(self):
        """Generator başlatıcı"""
        pass

    def generate_html_report(self, report_data: Dict[str, Any], logo_path: Optional[str] = None) -> str:
        """
        İnteraktif HTML rapor oluştur
        
        Args:
            report_data: Rapor verileri
            logo_path: Firma logosu yolu
        """
        # Logo'yu base64'e çevir
        logo_base64 = ""
        if logo_path:
            try:
                with open(logo_path, 'rb') as f:
                    logo_base64 = base64.b64encode(f.read()).decode()
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data.get('title', 'Sürdürülebilirlik Raporu')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #6A1B9A;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            max-width: 300px;
            max-height: 150px;
        }}
        h1 {{
            color: #6A1B9A;
            margin: 10px 0;
        }}
        h2 {{
            color: #8E24AA;
            border-left: 4px solid #8E24AA;
            padding-left: 15px;
            margin-top: 30px;
        }}
        .metric-card {{
            display: inline-block;
            width: 23%;
            margin: 1%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
        }}
        .metric-label {{
            font-size: 14px;
            margin-top: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #6A1B9A;
            color: white;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ddd;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {"<img src='data:image/png;base64," + logo_base64 + "' class='logo' alt='Logo'>" if logo_base64 else ""}
            <h1>{report_data.get('title', 'Sürdürülebilirlik Raporu')}</h1>
            <p>{report_data.get('company_name', 'Şirket')} - {report_data.get('period', '2024')}</p>
        </div>
        
        <h2>Ana Metrikler</h2>
        <div class="metrics">
            {self._generate_metric_cards(report_data.get('metrics', {}))}
        </div>
        
        <h2>Performans Özeti</h2>
        {self._generate_performance_table(report_data.get('performance', []))}
        
        <h2>Başarılar</h2>
        <ul>
            {self._generate_list_items(report_data.get('highlights', []))}
        </ul>
        
        <div class="footer">
            <p>Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            <p>SUSTAINAGE SDG Platform - Sürdürülebilirlik Raporlama Sistemi</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _generate_metric_cards(self, metrics: Dict) -> str:
        """Metrik kartları oluştur"""
        cards = []
        for label, value in metrics.items():
            cards.append(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """)
        return "".join(cards)

    def _generate_performance_table(self, performance: List[Dict]) -> str:
        """Performans tablosu oluştur"""
        if not performance:
            return "<p>Veri yok</p>"

        rows = []
        for item in performance:
            rows.append(f"""
            <tr>
                <td>{item.get('metric', '')}</td>
                <td>{item.get('value', '')}</td>
                <td>{item.get('target', '')}</td>
                <td>{item.get('status', '')}</td>
            </tr>
            """)

        return f"""
        <table>
            <thead>
                <tr>
                    <th>Metrik</th>
                    <th>Değer</th>
                    <th>Hedef</th>
                    <th>Durum</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
        """

    def _generate_list_items(self, items: List[str]) -> str:
        """Liste öğeleri oluştur"""
        return "".join([f"<li>{item}</li>" for item in items])
