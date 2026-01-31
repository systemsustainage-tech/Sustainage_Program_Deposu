#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI DESTEKLI RAPOR OLUŞTURMA - GUI
==================================

OpenAI entegrasyonu ile otomatik rapor oluşturma arayüzü
"""

import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from utils.language_manager import LanguageManager

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class AIReportsGUI:
    """AI Destekli Rapor Oluşturma GUI"""

    def __init__(self, parent, company_id: int = None):
        self.parent = parent
        self.company_id = company_id
        self.lm = LanguageManager()

        # Check if OpenAI is available
        self.openai_available = self._check_openai_available()

        # Setup UI directly
        self.setup_ui()

    def _check_openai_available(self) -> bool:
        """Check if OpenAI is configured"""
        try:
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv('OPENAI_API_KEY')
            return api_key and api_key.startswith('sk-')
        except Exception:
            return False

    def setup_ui(self):
        """Ana arayüzü oluştur"""
        # Main frame
        main_frame = tk.Frame(self.parent, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Header
        header = tk.Frame(main_frame, bg='#667eea', height=80)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)

        tk.Label(header, text=self.lm.tr("ai_report_generation_title", " AI Destekli Rapor Oluşturma"),
                font=('Segoe UI', 18, 'bold'), fg='white', bg='#667eea').pack(expand=True)

        # Main content
        content = tk.Frame(main_frame, bg='#f5f5f5')
        content.pack(fill='both', expand=True)

        self._create_ui(content)

    def _create_ui(self, content):
        """UI oluştur"""

        # OpenAI Status
        status_frame = tk.LabelFrame(content, text="OpenAI Durumu",
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        status_frame.pack(fill='x', pady=(0, 15))

        status_color = '#27ae60' if self.openai_available else '#e74c3c'
        status_text = " OpenAI API Key Yapılandırılmış" if self.openai_available else " OpenAI API Key Bulunamadı"

        tk.Label(status_frame, text=status_text, font=('Segoe UI', 10),
                fg=status_color, bg='white').pack(pady=10)

        if not self.openai_available:
            tk.Label(status_frame, text="Lütfen .env dosyasına OPENAI_API_KEY ekleyin",
                    font=('Segoe UI', 9), fg='#7f8c8d', bg='white').pack(pady=(0, 5))

            setup_btn = tk.Button(status_frame, text=" Kurulum Kılavuzunu Göster",
                                 bg='#3498db', fg='white', command=self._show_setup_guide)
            setup_btn.pack(pady=10)

        # Report Configuration
        config_frame = tk.LabelFrame(content, text="Rapor Ayarları",
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        config_frame.pack(fill='both', expand=True, pady=(0, 15))

        # Report Type
        tk.Label(config_frame, text="Rapor Türü:", bg='white').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.report_type = ttk.Combobox(config_frame, width=40, state='readonly')
        self.report_type['values'] = [
            'Sürdürülebilirlik Raporu',
            'GRI Uyumluluk Raporu',
            'SDG İlerleme Raporu',
            'TCFD İklim Raporu',
            'SASB Sektör Raporu',
            'ESG Performans Raporu',
            'Yönetici Özeti'
        ]
        self.report_type.current(0)
        self.report_type.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        # Standards
        tk.Label(config_frame, text="Standartlar:", bg='white').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.standards_var = tk.StringVar(value="GRI,SDG,TCFD")
        standards_entry = tk.Entry(config_frame, textvariable=self.standards_var, width=40)
        standards_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=5)

        # Timeframe
        tk.Label(config_frame, text="Zaman Aralığı:", bg='white').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.timeframe_var = tk.StringVar(value=f"{datetime.now().year}")
        timeframe_entry = tk.Entry(config_frame, textvariable=self.timeframe_var, width=40)
        timeframe_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

        # Language
        tk.Label(config_frame, text="Dil:", bg='white').grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.language = ttk.Combobox(config_frame, width=40, state='readonly')
        self.language['values'] = ['Türkçe (tr)', 'İngilizce (en)']
        self.language.current(0)
        self.language.grid(row=3, column=1, sticky='ew', padx=10, pady=5)

        # Style
        tk.Label(config_frame, text="Stil:", bg='white').grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.style = ttk.Combobox(config_frame, width=40, state='readonly')
        self.style['values'] = ['Kurumsal', 'Akademik', 'Teknik', 'Genel']
        self.style.current(0)
        self.style.grid(row=4, column=1, sticky='ew', padx=10, pady=5)

        # Model
        tk.Label(config_frame, text="AI Modeli:", bg='white').grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.model = ttk.Combobox(config_frame, width=40, state='readonly')
        self.model['values'] = [
            'gpt-4o-mini (Hızlı, Ekonomik)',
            'gpt-4o (En İyi Kalite)',
            'gpt-4-turbo (Dengeli)'
        ]
        self.model.current(0)
        self.model.grid(row=5, column=1, sticky='ew', padx=10, pady=5)

        # Temperature
        tk.Label(config_frame, text="Yaratıcılık (0.0-1.0):", bg='white').grid(row=6, column=0, sticky='w', padx=10, pady=5)
        self.temperature_var = tk.DoubleVar(value=0.2)
        temperature_scale = tk.Scale(config_frame, from_=0.0, to=1.0, resolution=0.1,
                                    orient='horizontal', variable=self.temperature_var)
        temperature_scale.grid(row=6, column=1, sticky='ew', padx=10, pady=5)

        config_frame.columnconfigure(1, weight=1)

        # Options
        options_frame = tk.LabelFrame(content, text="Seçenekler",
                                     font=('Segoe UI', 11, 'bold'), bg='white')
        options_frame.pack(fill='x', pady=(0, 15))

        self.dry_run_var = tk.BooleanVar(value=not self.openai_available)
        dry_run_check = tk.Checkbutton(options_frame, text="Test Modu (OpenAI çağrısı yapmadan örnek rapor)",
                                      variable=self.dry_run_var, bg='white')
        dry_run_check.pack(anchor='w', padx=10, pady=5)

        self.save_docx_var = tk.BooleanVar(value=True)
        save_check = tk.Checkbutton(options_frame, text="DOCX formatında kaydet",
                                    variable=self.save_docx_var, bg='white')
        save_check.pack(anchor='w', padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(content, bg='#f5f5f5')
        button_frame.pack(fill='x', pady=(0, 20))

        if self.openai_available or True:  # Her zaman test modunda çalıştırılabilir
            generate_btn = tk.Button(button_frame, text=" Rapor Oluştur",
                                    font=('Segoe UI', 12, 'bold'), bg='#27ae60', fg='white',
                                    command=self._generate_report)
            generate_btn.pack(side='left', padx=5, ipadx=20, ipady=10)

        test_btn = tk.Button(button_frame, text=" Test Raporu Oluştur (Dry Run)",
                            font=('Segoe UI', 11), bg='#3498db', fg='white',
                            command=self._generate_test_report)
        test_btn.pack(side='left', padx=5, ipadx=10, ipady=10)


    def _show_setup_guide(self):
        """Kurulum kılavuzunu göster"""
        guide_window = tk.Toplevel(self.parent)
        guide_window.title("OpenAI Kurulum Kılavuzu")
        guide_window.geometry("700x500")

        text = tk.Text(guide_window, wrap='word', padx=15, pady=15)
        text.pack(fill='both', expand=True)

        guide_text = """
OPENAI API KURULUM KILAVUZU
===========================

1. OpenAI API Key Alma:
   • https://platform.openai.com/api-keys adresine gidin
   • "Create new secret key" butonuna tıklayın
   • Anahtarı kopyalayın (sk- ile başlar)

2. .env Dosyası Oluşturma:
   • Proje ana dizininde .env dosyası oluşturun
   • Veya .env.openai.example dosyasını .env olarak kopyalayın
   
3. API Key'i .env Dosyasına Ekleyin:
   OPENAI_API_KEY=sk-your-api-key-here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_TEMPERATURE=0.2

4. OpenAI Paketi Kurun:
   pip install openai>=1.3.0

5. Maliyet Tahminleri (gpt-4o-mini):
   • Kısa rapor (2-3 sayfa): ~$0.01-0.02
   • Orta rapor (5-10 sayfa): ~$0.03-0.05
   • Uzun rapor (20+ sayfa): ~$0.10-0.15

6. Test Edin:
   • "Test Raporu Oluştur" butonuna tıklayın
   • Dry Run modunda ücretsiz test edebilirsiniz

7. Güvenlik:
   • API Key'inizi asla paylaşmayın
   • .env dosyasını git'e commit etmeyin
   • Kullanımı düzenli kontrol edin: https://platform.openai.com/usage

Daha fazla bilgi:
• Dokümantasyon: https://platform.openai.com/docs
• Fiyatlandırma: https://openai.com/pricing
        """

        text.insert('1.0', guide_text)
        text.config(state='disabled')

    def _generate_test_report(self):
        """Test raporu oluştur (dry run)"""
        self.dry_run_var.set(True)
        self._generate_report()

    def _generate_report(self):
        """Rapor oluştur"""
        try:
            # Get configuration
            report_type = self.report_type.get()
            standards = [s.strip() for s in self.standards_var.get().split(',')]
            timeframe = self.timeframe_var.get()
            language = self.language.get().split('(')[1].strip(')')
            style = self.style.get().lower()
            model = self.model.get().split(' ')[0]
            temperature = self.temperature_var.get()
            dry_run = self.dry_run_var.get()

            # Show progress
            progress_window = tk.Toplevel(self.parent)
            progress_window.title(self.lm.tr("report_generating", "Rapor Oluşturuluyor..."))
            progress_window.geometry("400x150")
            progress_window.transient(self.parent)

            tk.Label(progress_window, text=self.lm.tr("ai_report_generating_label", " AI Rapor Oluşturuluyor..."),
                    font=('Segoe UI', 12, 'bold')).pack(pady=20)

            status_label = tk.Label(progress_window, text=self.lm.tr("preparing", "Hazırlanıyor..."),
                                   font=('Segoe UI', 10))
            status_label.pack(pady=10)

            progress_window.update()

            # Import and create generator
            from services.ai_reporting import AIReportGenerator

            generator = AIReportGenerator(
                model=model,
                temperature=temperature,
                language=language
            )

            # Prepare inputs (demo data for now)
            inputs = {
                "company": {
                    "name": os.getenv("COMPANY_NAME", "Örnek Şirket A.Ş."),
                    "sector": os.getenv("COMPANY_SECTOR", "İmalat"),
                    "region": os.getenv("COMPANY_REGION", "TR")
                },
                "timeframe": timeframe,
                "metrics": {
                    "Toplam Enerji Tüketimi (MWh)": 125000,
                    "Yenilenebilir Enerji Oranı (%)": 42.7,
                    "Su Tüketimi (m3)": 98000,
                    "Toplam Atık (ton)": 3200,
                    "Kaza Sıklık Oranı": 0.7,
                },
                "findings": [
                    "Enerji verimliliği projeleri ile %8 tasarruf",
                    "İş sağlığı ve güvenliğinde iyileşme",
                    "Su geri kazanım hattı devreye alındı"
                ]
            }

            status_label.config(text="AI ile rapor oluşturuluyor...")
            progress_window.update()

            # Generate report
            text, usage = generator.generate_report(
                report_type=report_type,
                inputs=inputs,
                standards=standards,
                dry_run=dry_run
            )

            # Save to file
            if self.save_docx_var.get():
                status_label.config(text="DOCX kaydediliyor...")
                progress_window.update()

                # Ask for save location
                output_path = filedialog.asksaveasfilename(
                    title=self.lm.tr('save_report', "Raporu Kaydet"),
                    defaultextension=".docx",
                    filetypes=[(self.lm.tr('word_files', "Word Dosyaları"), "*.docx"), (self.lm.tr('all_files', "Tüm Dosyalar"), "*.*")],
                    initialfile=f"ai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                )

                if output_path:
                    generator.save_docx(text, output_path)

                    progress_window.destroy()

                    # Success message
                    mode_text = "(Test Modu)" if dry_run else ""
                    messagebox.showinfo(
                        "Başarılı",
                        f"Rapor başarıyla oluşturuldu! {mode_text}\n\n"
                        f"Dosya: {output_path}\n"
                        f"Model: {usage.get('model')}\n"
                        f"Token: {usage.get('total_tokens', 0)}"
                    )
                else:
                    progress_window.destroy()
            else:
                progress_window.destroy()

                # Show text
                text_window = tk.Toplevel(self.parent)
                text_window.title("Oluşturulan Rapor")
                text_window.geometry("800x600")

                text_widget = tk.Text(text_window, wrap='word', padx=15, pady=15)
                text_widget.pack(fill='both', expand=True)
                text_widget.insert('1.0', text)
                text_widget.config(state='disabled')

        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()

            messagebox.showerror(
                "Hata",
                f"Rapor oluşturulamadı:\n\n{str(e)}\n\n"
                "Lütfen:\n"
                "1. .env dosyasında OPENAI_API_KEY'i kontrol edin\n"
                "2. 'openai' paketinin kurulu olduğundan emin olun\n"
                "3. İnternet bağlantınızı kontrol edin\n"
                "4. Veya 'Test Raporu Oluştur' ile deneyebilirsiniz"
            )


if __name__ == "__main__":
    # Test
    root = tk.Tk()
    root.withdraw()

    app = AIReportsGUI(root)

    root.mainloop()

