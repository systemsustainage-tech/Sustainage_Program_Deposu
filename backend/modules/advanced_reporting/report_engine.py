import os
import json
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class ReportEngine:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_report(self, data: dict, report_id: str) -> dict:
        """
        Generates a report based on the provided data.
        Returns a dictionary with file paths.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"report_{data['company_id']}_{data['period']}_{report_id}"
        
        # 1. Save JSON Data
        json_filename = f"{base_filename}.json"
        json_path = os.path.join(self.output_dir, json_filename)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # 2. Generate PDF (Simple Summary)
        pdf_filename = f"{base_filename}.pdf"
        pdf_path = os.path.join(self.output_dir, pdf_filename)
        self._create_pdf(pdf_path, data)

        return {
            'json_path': json_path,
            'pdf_path': pdf_path,
            'json_url': f"/static/reports/{json_filename}", # Assuming mapped to static/reports
            'pdf_url': f"/static/reports/{pdf_filename}"
        }

    def _create_pdf(self, path: str, data: dict):
        try:
            c = canvas.Canvas(path, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, f"SustainAge Report - {data['period']}")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Company ID: {data['company_id']}")
            c.drawString(50, height - 100, f"Scope: {data['scope']}")
            c.drawString(50, height - 120, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            y = height - 160
            c.drawString(50, y, "Summary of Data:")
            y -= 20
            
            if 'modules' in data:
                for module_name, module_data in data['modules'].items():
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(70, y, module_name.upper())
                    y -= 20
                    c.setFont("Helvetica", 10)
                    
                    # Flatten stats for display
                    stats_str = json.dumps(module_data, default=str)
                    # Simple wrap
                    max_len = 90
                    for i in range(0, len(stats_str), max_len):
                        chunk = stats_str[i:i+max_len]
                        c.drawString(90, y, chunk)
                        y -= 15
                        if y < 50:
                            c.showPage()
                            y = height - 50
                    y -= 10
                    
            c.save()
        except Exception as e:
            logging.error(f"Error creating PDF: {e}")
            raise
